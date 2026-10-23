import re
from pathlib import Path

import fitz

def _clean_line(value: str, limit: int = 110) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    return value[:limit].rstrip(" ,.;:")

def extract_document(pdf_path: Path) -> tuple[str, list[str], int]:
    """Extract a concise title and three presentation-friendly beats."""
    pdf = fitz.open(pdf_path)
    page_count = len(pdf)
    text = "\n".join(page.get_text("text") for page in pdf)
    pdf.close()
    lines = [line for line in (_clean_line(line) for line in text.splitlines()) if len(line) > 15]
    title = lines[0] if lines else pdf_path.stem.replace("_", " ")
    headings = [line for line in lines if re.match(r"^(\d+(?:\.\d+)*\s+)?[A-Z][A-Za-z -]{3,70}$", line)]
    beats: list[str] = []
    for line in headings + lines[1:]:
        if line.lower() != title.lower() and line not in beats:
            beats.append(line)
        if len(beats) == 3:
            break
    return title, beats or ["Read the document", "Identify the central idea", "Connect the key takeaways"], page_count
