"""Resumable local text catalog for the existing document lattice."""

import os
import sqlite3
from pathlib import Path

from Brain.Executive.source_registry import documents_root
from Brain.Executive.ocr_runtime import installed_tools

ROOT = Path(__file__).resolve().parents[2]
DATABASE = Path(os.environ.get("BPFCO_DOCUMENT_CATALOG", str(ROOT / "Brain" / "cache" / "document_text.sqlite3")))
EXTENSIONS = {".md", ".txt", ".docx", ".pdf"}


def connect():
    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DATABASE)
    db.execute("CREATE TABLE IF NOT EXISTS documents (path TEXT PRIMARY KEY, mtime INTEGER, size INTEGER, text TEXT)")
    db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS document_search USING fts5(path UNINDEXED, title, text)")
    db.execute("CREATE TABLE IF NOT EXISTS failed_documents "
               "(path TEXT PRIMARY KEY, mtime INTEGER, size INTEGER, pipeline TEXT, reason TEXT)")
    return db


def refresh(batch=20):
    """Process at most batch changed files; re-running resumes the same catalog."""
    folder = documents_root()
    if folder is None:
        return {"error": "Document folder unavailable", "updated": 0}
    from Dashboard.adapters.document_edges import _docx_text, _pdf_text
    ocr_ready = installed_tools() is not None
    pipeline = "tesseract-v1" if ocr_ready else "plain-v1"
    updated = 0
    examined = 0
    with connect() as db:
        for current, directories, names in os.walk(folder, followlinks=False):
            depth = len(Path(current).relative_to(folder).parts)
            directories[:] = sorted(d for d in directories if not d.startswith(".") and
                                    not (Path(current) / d).is_symlink()) if depth < 5 else []
            for name in sorted(names):
                path = Path(current) / name
                if path.suffix.lower() not in EXTENSIONS or path.is_symlink():
                    continue
                examined += 1
                stat = None
                try:
                    if not path.resolve().is_relative_to(folder):
                        continue
                    stat = path.stat()
                    if stat.st_size > 20_000_000:
                        continue
                    key = str(path.resolve())
                    previous = db.execute("SELECT mtime,size,text FROM documents WHERE path=?", (key,)).fetchone()
                    unchanged = previous and previous[:2] == (stat.st_mtime_ns, stat.st_size)
                    if unchanged and not (path.suffix.lower() == ".pdf" and ocr_ready
                                          and previous[2] != "tesseract-v1"):
                        continue
                    failure = db.execute("SELECT mtime,size,pipeline FROM failed_documents WHERE path=?",
                                         (key,)).fetchone()
                    if failure == (stat.st_mtime_ns, stat.st_size, pipeline):
                        continue
                    if updated >= batch:
                        continue
                    if path.suffix.lower() == ".docx":
                        content = _docx_text(path)
                    elif path.suffix.lower() == ".pdf":
                        content = _pdf_text(path, ocr=ocr_ready)
                    else:
                        content = path.read_text(encoding="utf-8-sig", errors="replace")[:150_000]
                    if content is None:
                        raise ValueError("No extractable text")
                    db.execute("DELETE FROM document_search WHERE path=?", (key,))
                    db.execute("INSERT INTO document_search(path,title,text) VALUES (?,?,?)",
                               (key, path.stem, content[:150_000]))
                    marker = "tesseract-v1" if path.suffix.lower() == ".pdf" and ocr_ready else "plain-v1"
                    db.execute("INSERT OR REPLACE INTO documents VALUES (?,?,?,?)",
                               (key, stat.st_mtime_ns, stat.st_size, marker))
                    db.execute("DELETE FROM failed_documents WHERE path=?", (key,))
                    db.commit()
                    updated += 1
                except Exception as exc:
                    if stat is not None:
                        db.execute("INSERT OR REPLACE INTO failed_documents VALUES (?,?,?,?,?)",
                                   (key, stat.st_mtime_ns, stat.st_size,
                                    pipeline, type(exc).__name__))
                        db.commit()
                    continue
        total = db.execute("SELECT count(*) FROM documents").fetchone()[0]
        failures = db.execute("SELECT path,reason FROM failed_documents ORDER BY path LIMIT 50").fetchall()
        failed_count = db.execute("SELECT count(*) FROM failed_documents").fetchone()[0]
    return {"updated": updated, "indexed": total, "examined": examined,
            "failed_count": failed_count,
            "failed": [{"path": path, "reason": reason} for path, reason in failures]}


def search(terms, limit=4):
    if not DATABASE.is_file() or not terms:
        return []
    query = " OR ".join('"' + term.replace('"', '') + '"' for term in sorted(terms))
    with sqlite3.connect(DATABASE) as db:
        rows = db.execute(
            "SELECT path,title,snippet(document_search,2,'','','…',16) "
            "FROM document_search WHERE document_search MATCH ? "
            "ORDER BY bm25(document_search) LIMIT ?", (query, limit)
        ).fetchall()
    return [{"path": path, "title": title, "excerpt": excerpt} for path, title, excerpt in rows]


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Update the offline document lattice in small batches")
    parser.add_argument("--batch", type=int, default=20)
    args = parser.parse_args()
    print(refresh(batch=max(1, min(args.batch, 100))))
