import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
UPLOADS, OUTPUTS = DATA / "uploads", DATA / "outputs"
MAX_UPLOAD_BYTES = int(os.getenv("PDFVISUAL_MAX_UPLOAD_MB", "25")) * 1024 * 1024
for directory in (UPLOADS, OUTPUTS):
    directory.mkdir(parents=True, exist_ok=True)
