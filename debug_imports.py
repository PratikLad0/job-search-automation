import sys
import os
from pathlib import Path
import traceback

# Add project root to sys.path
root = Path(__file__).resolve().parent
sys.path.append(str(root))

routers = ["jobs", "stats", "scrapers", "chat", "generators", "profile"]

for r in routers:
    try:
        module_path = f"backend.app.api.routers.{r}"
        print(f"Attempting to import {module_path}...")
        __import__(module_path)
        print(f"✅ {r} imported successfully")
    except Exception as e:
        print(f"❌ Failed to import {r}:")
        traceback.print_exc()
        print("-" * 40)
