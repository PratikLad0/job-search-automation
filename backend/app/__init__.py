
import sys
import asyncio

# Ensure Windows uses the ProactorEventLoopPolicy by default
# This is crucial for Playwright to work correctly on Windows
if sys.platform == 'win32':
    try:
        import asyncio
        if not isinstance(asyncio.get_event_loop_policy(), asyncio.WindowsProactorEventLoopPolicy):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        pass
