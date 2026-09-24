"""Resumable local text catalog for the existing document lattice."""

import os
import sqlite3
from pathlib import Path

from Brain.Executive.source_registry import documents_root

ROOT = Path(__file__).resolve().parents[2]
DATABASE = ROOT / "Brain" / "cache" / "document_text.sqlite3"
EXTENSIONS = {".md", ".txt", ".docx", ".pdf"}


def connect():
    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DATABASE)
    db.execute("CREATE TABLE IF NOT EXISTS documents (path TEXT PRIMARY KEY, mtime INTEGER, size INTEGER, text TEXT)")
    db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS document_search USING fts5(path UNINDEXED, title, text)")
    return db


def refresh(batch=20):
    """Process at most batch changed files; re-running resumes the same catalog."""
    folder = documents_root()
    if folder is None:
        return {"error": "Document folder unavailable", "updated": 0}
    from Dashboard.adapters.document_edges import _docx_text, _pdf_text
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
                try:
                    if not path.resolve().is_relative_to(folder):
                        continue
                    stat = path.stat()
                    if stat.st_size > 20_000_000:
                        continue
                    key = str(path.resolve())
                    previous = db.execute("SELECT mtime,size FROM documents WHERE path=?", (key,)).fetchone()
                    if previous == (stat.st_mtime_ns, stat.st_size):
                        continue
                    if updated >= batch:
                        continue
                    if path.suffix.lower() == ".docx":
                        content = _docx_text(path)
                    elif path.suffix.lower() == ".pdf":
                        content = _pdf_text(path)
                    else:
                        content = path.read_text(encoding="utf-8-sig", errors="replace")[:150_000]
                    if content is None:
                        continue
                    db.execute("DELETE FROM document_search WHERE path=?", (key,))
                    db.execute("INSERT INTO document_search(path,title,text) VALUES (?,?,?)",
                               (key, path.stem, content[:150_000]))
                    db.execute("INSERT OR REPLACE INTO documents VALUES (?,?,?,?)",
                               (key, stat.st_mtime_ns, stat.st_size, ""))
                    db.commit()
                    updated += 1
                except Exception:
                    continue
        total = db.execute("SELECT count(*) FROM documents").fetchone()[0]
    return {"updated": updated, "indexed": total, "examined": examined}


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
