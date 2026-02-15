"""
Multi-provider AI abstraction layer.
Falls back through: Ollama (local, free) → Gemini Pro → OpenAI (paid)
"""

import json
import logging
from typing import Optional

from backend.app.core import config

logger = logging.getLogger(__name__)


class AIProvider:
    """
    Unified AI interface with automatic fallback.
    Priority: Ollama → Gemini Pro → OpenAI
    """

    def __init__(self):
        self._primary = config.AI_PRIMARY_PROVIDER
        self._backup = config.AI_BACKUP_PROVIDER
        self._ollama_client = None
        self._gemini_model = None
        self._openai_client = None

    def _get_ollama(self):
        """Lazy-init Ollama client."""
        if self._ollama_client is None:
            try:
                from ollama import Client
                # Initialize client with the base URL from config
                client = Client(host=config.OLLAMA_BASE_URL)
                # Test connection
                client.list()
                self._ollama_client = client
                logger.info(f"Ollama connected at {config.OLLAMA_BASE_URL}, using model: {config.OLLAMA_MODEL}")
            except Exception as e:
                logger.warning(f"Ollama unavailable at {config.OLLAMA_BASE_URL}: {e}")
                self._ollama_client = False  # Mark as failed
        return self._ollama_client if self._ollama_client else None

    def _get_gemini(self):
        """Lazy-init Gemini client."""
        if self._gemini_model is None:
            try:
                if not config.GEMINI_API_KEY:
                    raise ValueError("GEMINI_API_KEY not set")
                import google.generativeai as genai
                genai.configure(api_key=config.GEMINI_API_KEY)
                self._gemini_model = genai.GenerativeModel(config.GEMINI_MODEL)
                logger.info(f"Gemini connected, using model: {config.GEMINI_MODEL}")
            except Exception as e:
                logger.warning(f"Gemini unavailable: {e}")
                self._gemini_model = False
        return self._gemini_model if self._gemini_model else None

    def _get_openai(self):
        """Lazy-init OpenAI client."""
        if self._openai_client is None:
            try:
                if not config.OPENAI_API_KEY:
                    raise ValueError("OPENAI_API_KEY not set")
                from openai import OpenAI
                self._openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
                logger.info(f"OpenAI connected, using model: {config.OPENAI_MODEL}")
            except Exception as e:
                logger.warning(f"OpenAI unavailable: {e}")
                self._openai_client = False
        return self._openai_client if self._openai_client else None

    def _call_ollama(self, prompt: str, system_prompt: str = "") -> str:
        """Call Ollama local LLM."""
        client = self._get_ollama()
        if not client:
            raise ConnectionError("Ollama not available")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = client.chat(
            model=config.OLLAMA_MODEL,
            messages=messages,
        )
        return response["message"]["content"]

    def _call_gemini(self, prompt: str, system_prompt: str = "") -> str:
        """Call Gemini Pro API."""
        model = self._get_gemini()
        if not model:
            raise ConnectionError("Gemini not available")

        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        # Add timeout to request options
        from google.api_core import retry
        response = model.generate_content(
            full_prompt,
            request_options={"timeout": 60}
        )
        return response.text

    def _call_openai(self, prompt: str, system_prompt: str = "") -> str:
        """Call OpenAI API."""
        client = self._get_openai()
        if not client:
            raise ConnectionError("OpenAI not available")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=messages,
        )
        return response.choices[0].message.content

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """
        Generate text using AI with automatic fallback.
        Tries primary → backup → remaining provider.
        """
        providers = {
            "ollama": self._call_ollama,
            "gemini": self._call_gemini,
            "openai": self._call_openai,
        }

        # Build priority order
        order = []
        if self._primary in providers:
            order.append(self._primary)
        if self._backup in providers and self._backup not in order:
            order.append(self._backup)
        for name in providers:
            if name not in order:
                order.append(name)

        last_error = None
        for name in order:
            # Retry logic for rate limits (429) or timeouts (Error 4 / DEADLINE_EXCEEDED)
            retries = 2
            for attempt in range(retries + 1):
                try:
                    logger.debug(f"Trying AI provider: {name} (attempt {attempt + 1})")
                    result = providers[name](prompt, system_prompt)
                    if result and result.strip():
                        logger.info(f"AI response from: {name}")
                        return result.strip()
                except Exception as e:
                    error_msg = str(e)
                    
                    # If it's a rate limit error (429) or timeout (4/Deadline), wait a bit and retry
                    is_retryable = any(code in error_msg for code in ["429", "Error code: 4", "DEADLINE_EXCEEDED"])
                    
                    if is_retryable and attempt < retries:
                        import time
                        wait_time = (attempt + 1) * 5
                        logger.warning(f"Provider {name} hit retryable error ({error_msg[:50]}...). Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    
                    # Connection error hint for Ollama in Docker
                    if name == "ollama" and ("Connection" in error_msg or "ignored" in error_msg.lower()):
                        logger.warning("Ollama connection failed. Ensure Ollama is running on host and OLLAMA_HOST=0.0.0.0 is set.")
                    
                    logger.warning(f"Provider {name} failed: {e}")
                    last_error = e
                    break # Move to next provider

        raise RuntimeError(
            f"All AI providers failed. Last error: {last_error}"
        )

    def generate_json(self, prompt: str, system_prompt: str = "") -> dict:
        """
        Generate and parse JSON response from AI.
        Adds JSON instruction to the prompt and attempts to parse the response.
        """
        json_instruction = (
            "\n\nIMPORTANT: Respond ONLY with valid JSON. "
            "No markdown, no code fences, no explanation. Just the raw JSON object."
        )
        response = self.generate(prompt + json_instruction, system_prompt)

        # Try to extract JSON from response
        response = response.strip()
        # Remove markdown code fences if present
        if response.startswith("```"):
            lines = response.split("\n")
            response = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
            response = response.strip()

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to find JSON object in the response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(response[start:end])
            raise ValueError(f"Could not parse JSON from AI response: {response[:200]}")


# Singleton instance
_provider: Optional[AIProvider] = None


def get_ai() -> AIProvider:
    """Get the global AI provider instance."""
    global _provider
    if _provider is None:
        _provider = AIProvider()
    return _provider
