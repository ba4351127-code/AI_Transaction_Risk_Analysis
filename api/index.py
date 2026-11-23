import sys
from pathlib import Path

# Add project root and backend directory to sys.path so all imports work seamlessly on Vercel
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Expose the FastAPI application instance for Vercel's serverless runtime
from backend.app.main import app

# Required for Vercel Python runtime discovery
__all__ = ["app"]
