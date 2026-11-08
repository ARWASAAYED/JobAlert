"""
Resume Extractor & Persona Builder for JobAlert.
Extracts text from PDF resumes, hashes them, and builds or updates master_cv.json.
"""

import os
import sys
import json
import hashlib
from pathlib import Path

def extract_pdf(pdf_path: str) -> dict:
    """Extracts text and SHA-256 hash from a PDF file."""
    import pypdf

    p = Path(pdf_path)
    if not p.is_file():
        raise FileNotFoundError(f"Resume not found at {pdf_path}")

    with open(p, "rb") as f:
        data = f.read()

    sha256 = hashlib.sha256(data).hexdigest()

    reader = pypdf.PdfReader(p)
    pages_text = []
    for idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        pages_text.append(text)

    full_text = "\n".join(pages_text)
    lines = [line.strip() for line in full_text.splitlines() if line.strip()]

    return {
        "slug": p.stem,
        "path": str(p),
        "sha256": sha256,
        "char_count": len(full_text),
        "line_count": len(lines),
        "text": full_text,
        "lines": lines
    }

def update_master_cv(pdf_path: str, master_cv_path: str = None) -> dict:
    """Extracts resume text and ensures master_cv.json is in sync."""
    if master_cv_path is None:
        master_cv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "master_cv.json")

    res = extract_pdf(pdf_path)

    # Load existing or default
    if os.path.exists(master_cv_path):
        with open(master_cv_path, "r", encoding="utf-8") as f:
            cv = json.load(f)
    else:
        cv = {}

    cv["_resume_meta"] = {
        "source_file": res["path"],
        "sha256": res["sha256"],
        "char_count": res["char_count"]
    }

    with open(master_cv_path, "w", encoding="utf-8") as f:
        json.dump(cv, f, indent=2, ensure_ascii=False)

    return res

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python resume_extractor.py <path-to-resume.pdf>")
        sys.exit(1)
    target = sys.argv[1]
    res = update_master_cv(target)
    print(f"Extracted {res['slug']} ({res['char_count']} chars, {res['line_count']} lines). Hash: {res['sha256'][:12]}...")

