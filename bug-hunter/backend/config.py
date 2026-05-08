import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{DATA_DIR}/bughunter.db")
APP_VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

CORS_ORIGINS = [
    o.strip()
    for o in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
    if o.strip()
]

# Optional API key auth. When set all non-health endpoints require
# the X-API-Key header to match this value. Leave unset for local dev.
API_KEY = os.getenv("API_KEY", "")

# Maximum allowed code_content size in bytes (default 1 MB).
MAX_CODE_SIZE_BYTES = int(os.getenv("MAX_CODE_SIZE_BYTES", str(1 * 1024 * 1024)))

# Maximum seconds to allow for a single scan before marking it failed.
SCAN_TIMEOUT_SECONDS = int(os.getenv("SCAN_TIMEOUT_SECONDS", "300"))
