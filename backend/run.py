
import sys
import os
import asyncio
import uvicorn
import logging

try:
    from watchfiles import run_process, DefaultFilter
except ImportError:
    print("❌ watchfiles not installed. Run 'pip install watchfiles'")
    sys.exit(1)

class ServerFilter(DefaultFilter):
    """
    Custom filter for watchfiles to ignore generated files and directories.
    This prevents the server from restarting every time it writes to a log or database.
    """
    def __call__(self, change, path):
        # Use default ignores (like .git, __pycache__, etc.)
        if not super().__call__(change, path):
            return False
        
        path_lower = path.lower()
        # Normalize separators for consistent checking
        normalized_path = path_lower.replace('\\', '/')
        parts = normalized_path.split('/')
        
        # 1. Ignore specific directories
        ignore_dirs = {'data', 'output', 'venv', 'logs', '.pytest_cache', '__pycache__'}
        if any(d in parts for d in ignore_dirs):
            return False
            
        # 2. Ignore generated file types that often change
        ignore_exts = {'.txt', '.log', '.png', '.html', '.db', '.pdf', '.docx'}
        if any(path_lower.endswith(ext) for ext in ignore_exts):
            # Never ignore python files
            if not path_lower.endswith('.py'):
                return False
                
        return True

def run_server():
    """
    Function to run the uvicorn server.
    This function is called in a separate process by watchfiles.
    """
    # 1. Set Policy for Windows
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
    # 2. Add paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    sys.path.insert(0, os.path.dirname(current_dir)) # Project root

    # 3. Running Config
    # We disable uvicorn's own reloader because we are handling it externally
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False, workers=1)

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"🚀 Starting Job Search Automation Backend (Custom Reloader + Noise Filter)")
    print(f"📂 Watching: {current_dir}")

    # Use watchfiles with the custom noise filter
    run_process(current_dir, target=run_server, watch_filter=ServerFilter())
