"""Locate installed offline OCR tools without downloading dependencies."""

import os
import shutil
from pathlib import Path


def installed_tools():
    tesseract = os.environ.get("BPFCO_TESSERACT_PATH")
    if not tesseract and os.name == "nt":
        for variable in ("ProgramFiles", "ProgramFiles(x86)"):
            base = os.environ.get(variable)
            candidate = Path(base) / "Tesseract-OCR" / "tesseract.exe" if base else None
            if candidate and candidate.is_file():
                tesseract = str(candidate)
                break
    tesseract = tesseract or shutil.which("tesseract")
    renderer = os.environ.get("BPFCO_PDFTOPPM_PATH") or shutil.which("pdftoppm")
    if not tesseract or not renderer:
        return None
    if not (Path(tesseract).is_file() or shutil.which(tesseract)):
        return None
    if not (Path(renderer).is_file() or shutil.which(renderer)):
        return None
    return tesseract, renderer
