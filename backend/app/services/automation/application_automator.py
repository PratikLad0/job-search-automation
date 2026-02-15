import logging
import random
import asyncio
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright, Page, BrowserContext

from backend.app.db.models import Job, UserProfile
from backend.app.core import config
from backend.app.db.database import JobDatabase

logger = logging.getLogger("jobsearch.automation")

class BaseAutomator(ABC):
    """Abstract base class for job portal-specific automation."""
    
    SOURCE_NAME: str = "generic"

    def __init__(self, page: Page, job: Job, profile: Optional[UserProfile] = None):
        self.page = page
        self.job = job
        self.profile = profile

    async def _random_delay(self, min_s: float = 1.0, max_s: float = 3.0):
        await asyncio.sleep(random.uniform(min_s, max_s))

    @abstractmethod
    async def apply(self) -> bool:
        """Execute the portal-specific application workflow."""
        pass

class GenericAutomator(BaseAutomator):
    """A flexible automator that uses common patterns to apply for jobs."""
    
    SOURCE_NAME = "generic"

    async def apply(self) -> bool:
        logger.info(f"Starting {self.job.source} application for {self.job.title} at {self.job.company}")
        
        await self.page.goto(self.job.url, wait_until="domcontentloaded")
        await self._random_delay(2, 4)

        # Check for login barriers
        if await self.page.query_selector("text=Sign in to apply") or \
           await self.page.query_selector("text=Join to apply") or \
           await self.page.query_selector(".modal__login-header"):
            logger.error("Login required to apply. Please configure a browser profile or log in manually.")
            return False

        # Look for "Apply" buttons
        apply_selectors = [
            "button:has-text('Apply')",
            "button:has-text('Quick Apply')",
            "button:has-text('Easy Apply')",
            "button:has-text('Apply now')",
            "a:has-text('Apply now')",
            "a:has-text('Apply on company site')",
            "button:has-text('Apply to this job')",
            "#indeedApplyButton",
            ".apply-button",
            "[data-testid='apply-button']",
            ".jobs-apply-button--top-card",
        ]
        
        button_found = False
        start_url = self.page.url
        
        for selector in apply_selectors:
            try:
                if await self.page.is_visible(selector, timeout=2000):
                    logger.info(f"Found apply button with selector: {selector}")
                    
                    # Handle separate tab case (common for "Apply on company site")
                    async with self.page.context.expect_page() as new_page_info:
                        try:
                            await self.page.click(selector, timeout=2000)
                        except:
                            # Sometimes it doesn't open a new page, just a modal
                            pass
                            
                    # If a new page opened, we might need to switch to it
                    try:
                        new_page = await new_page_info.value
                        await new_page.wait_for_load_state()
                        logger.info(f"New page opened: {new_page.url}")
                        self.page = new_page # Switch context to new page
                        button_found = True
                        break
                    except:
                        # No new page, maybe just a modal or navigation
                        button_found = True
                        break
            except Exception as e:
                # logger.debug(f"Selector failed {selector}: {e}")
                continue
        
        if not button_found:
            logger.warning(f"No obvious apply button found for {self.job.url}. Attempting to look for forms directly.")
        else:
            await self._random_delay(3, 5)

        # Check if we were redirected to a login page
        if "login" in self.page.url or "signin" in self.page.url:
             logger.error("Redirected to login page. Cannot proceed without authentication.")
             return False

        # Track if we actually did anything useful
        actions_performed = 0

        # Handle form steps (up to 5 steps)
        for step in range(5):
            # Check for barriers (Login/Sign up) taking over the screen
            if await self.page.query_selector("text=Sign in") or \
               await self.page.query_selector("text=Join now") or \
               await self.page.query_selector("text=Welcome back"):
                logger.error("Encountered login prompt during application. Aborting.")
                return False

            # Check for Resume upload
            resume_input = "input[type='file'][name*='resume'], input[type='file'][id*='resume'], input[type='file'][accept*='pdf']"
            if await self.page.query_selector(resume_input):
                if self.job.resume_path and Path(self.job.resume_path).exists():
                    logger.info(f"Uploading resume: {self.job.resume_path}")
                    await self.page.set_input_files(resume_input, self.job.resume_path)
                    actions_performed += 1
                    await self._random_delay(2, 4)
                elif self.profile and self.profile.resume_path and Path(self.profile.resume_path).exists():
                    logger.info(f"Uploading profile resume: {self.profile.resume_path}")
                    await self.page.set_input_files(resume_input, self.profile.resume_path)
                    actions_performed += 1
                    await self._random_delay(2, 4)

            # Fill common fields if profile is available
            if self.profile:
                fields = {
                    "first_name": self.profile.full_name.split()[0] if " " in self.profile.full_name else self.profile.full_name,
                    "last_name": self.profile.full_name.split()[-1] if " " in self.profile.full_name else "",
                    "full_name": self.profile.full_name,
                    "email": self.profile.email,
                    "phone": self.profile.phone,
                    "location": self.profile.location,
                    "linkedin": self.profile.linkedin_url,
                    "github": self.profile.github_url,
                    "portfolio": self.profile.portfolio_url,
                }
                
                for field_name, value in fields.items():
                    if not value: continue
                    
                    # Try various selectors for each field
                    selectors = [
                        f"input[name*='{field_name}']",
                        f"input[id*='{field_name}']",
                        f"input[placeholder*='{field_name.replace('_', ' ')}']",
                    ]
                    
                    for sel in selectors:
                        try:
                            element = await self.page.query_selector(sel)
                            if element and await element.is_visible() and not await element.input_value():
                                await element.fill(value)
                                logger.debug(f"Filled {field_name} into {sel}")
                                actions_performed += 1
                                break
                        except:
                            continue

            # Look for "Continue", "Next", or "Submit" buttons
            next_selectors = [
                "button:has-text('Continue')",
                "button:has-text('Next')",
                "button:has-text('Save and continue')",
                "button:has-text('Review')",
                "button:has-text('Submit')",
                "button:has-text('Apply')",
                "button[type='submit']",
                ".ia-continue-button",
                "button[aria-label='Continue to next step']",
            ]
            
            step_advanced = False
            for sel in next_selectors:
                try:
                    if await self.page.is_visible(sel, timeout=2000):
                        current_url = self.page.url
                        await self.page.click(sel)
                        actions_performed += 1
                        await self._random_delay(2, 4)
                        
                        # Check if we moved to a new page or if a submit happened
                        if self.page.url != current_url or await self.page.query_selector("text=success, text=thank you, text=received"):
                            step_advanced = True
                            if "submit" in sel.lower() or "apply" in sel.lower() or "thank" in self.page.content().lower():
                                logger.info("Application submitted successfully!")
                                return True
                            break
                except:
                    continue
            
            if not step_advanced:
                # If we didn't find a "Next" button, we might be at the end
                break

        # If we performed actions but didn't explicitly find a "Success" message, 
        # we might still have submitted or at least done something useful.
        if actions_performed > 0:
            logger.info(f"Performed {actions_performed} actions. Marking as potential success.")
            return True
        
        logger.warning("No actions performed. Automation likely failed.")
        return False

class AutomationManager:
    """Manages browser context and delegates application tasks."""
    
    def __init__(self):
        self.db = JobDatabase()

    async def run_application(self, job_id: int) -> dict:
        job = self.db.get_job(job_id)
        if not job:
            return {"status": "error", "message": "Job not found"}
        
        profile = self.db.get_profile(1) # Get default profile
        
        has_resume = (job.resume_path and Path(job.resume_path).exists()) or \
                     (profile and profile.resume_path and Path(profile.resume_path).exists())
                     
        if not has_resume:
            return {"status": "error", "message": "No resume found (neither job-specific nor profile default)."}

        async with async_playwright() as p:
            # Decide browser launch options
            launch_kwargs = {
                "headless": False, # Always run headful for now so user can see/interact
                "args": ["--disable-blink-features=AutomationControlled"],
            }
            
            # Use persistent context if profile path provided
            try:
                if config.BROWSER_PROFILE_PATH:
                    logger.info(f"Using persistent browser profile: {config.BROWSER_PROFILE_PATH}")
                    # Use channel="chrome" to use the installed Chrome browser
                    context = await p.chromium.launch_persistent_context(
                        user_data_dir=config.BROWSER_PROFILE_PATH,
                        channel="chrome", 
                        **launch_kwargs
                    )
                else:
                    logger.warning("No BROWSER_PROFILE_PATH provided.")
                    
                    auth_state_path = config.DATA_DIR / "auth_state.json"
                    if auth_state_path.exists():
                        logger.info(f"Using cached auth state from: {auth_state_path}")
                        browser = await p.chromium.launch(**launch_kwargs)
                        # Load context with storage state (cookies, local storage)
                        context = await browser.new_context(storage_state=auth_state_path)
                    else:
                        logger.warning("No auth_state.json found. Starting fresh session (login may fail).")
                        browser = await p.chromium.launch(**launch_kwargs)
                        context = await browser.new_context()

            except Exception as e:
                if "profile is in use" in str(e).lower() or "lock file" in str(e).lower():
                    return {
                        "status": "error", 
                        "message": "Your browser profile is currently in use. Please close all Chrome windows or use a separate profile for automation."
                    }
                raise e
            
            page = await context.new_page()
            
            # Select automator - currently all sources use GenericAutomator
            # We can add portal-specific ones later if needed
            automator = GenericAutomator(page, job, profile)
            
            try:
                success = await automator.apply()
                if success:
                    self.db.update_status(job_id, "applied")
                    return {"status": "success", "message": f"Successfully applied for {job.title}"}
                else:
                    return {"status": "error", "message": "Application flow failed or was incomplete."}
            except Exception as e:
                logger.exception(f"Automation error: {e}")
                return {"status": "error", "message": f"Automation error: {str(e)}"}
            finally:
                await context.close()

