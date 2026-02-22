
import sys
import os
import traceback

try:
    with open("debug_log.txt", "w", encoding="utf-8") as f:
        # Add the project root to sys.path
        ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__)))
        if ROOT_PATH not in sys.path:
            sys.path.append(ROOT_PATH)

        f.write(f"sys.path: {sys.path}\n")

        routers = ["jobs", "stats", "scrapers", "chat", "generators", "profile", "assistant", "auth", "company"]

        for name in routers:
            f.write(f"\n--- Importing {name} router ---\n")
            try:
                module = __import__(f"backend.app.api.routers.{name}", fromlist=["router"])
                f.write(f"✅ {name} router imported\n")
            except Exception:
                f.write(f"❌ {name} router FAILED\n")
                traceback.print_exc(file=f)
except Exception as e:
    print(f"Failed to write log: {e}")
