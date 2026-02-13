import sys
import os
from pathlib import Path

# CWD is backend
# Add project root
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))
print(f"Project root added: {project_root}")

try:
    from app.api.routers import jobs
    print("✅ import app.api.routers.jobs worked")
except ImportError as e:
    print(f"❌ import app.api.routers.jobs failed: {e}")

try:
    from backend.app.api.routers import jobs
    print("✅ import backend.app.api.routers.jobs worked")
except ImportError as e:
    print(f"❌ import backend.app.api.routers.jobs failed: {e}")
