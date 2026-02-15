
import sys
import os
import asyncio
import uvicorn
import logging

try:
    from watchfiles import run_process
except ImportError:
    print("❌ watchfiles not installed. Run 'pip install watchfiles'")
    sys.exit(1)

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
    
    print(f"🚀 Starting Job Search Automation Backend (Custom Reloader + Proactor Loop)")
    print(f"📂 Watching: {current_dir}")

    # Use watchfiles to monitor changes and restart the process
    # This ensures a fresh process is spawned where we can set the event loop policy correctly
    run_process(current_dir, target=run_server)
