#!/usr/bin/env python3
"""BPFCoBrain desktop interface for the local Markdown vault."""

import json
import os
import subprocess
import sys
import webbrowser
from pathlib import Path

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

try:
    import PySimpleGUI as sg
except ImportError:
    print("PySimpleGUI is required. Install it with: python -m pip install PySimpleGUI")
    raise

sg.theme("DarkBlue3")
VAULT_PATH = Path(__file__).resolve().parent
INDEX_FILE = VAULT_PATH / ".vault-index.json"


class BrainDesktop:
    def __init__(self):
        self.index = self._load_index()
        self.window = None
        self.search_results = []
        self.http_process = None

    def _load_index(self):
        if not INDEX_FILE.exists():
            return {"notes": {}, "graph": {}, "stats": {}, "error": f"Missing {INDEX_FILE.name}"}
        try:
            index = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
            notes = index.get("notes", {})
            if isinstance(notes, list):
                notes = {n.get("name", n.get("title", str(i))): n for i, n in enumerate(notes)}
            index["notes"] = notes
            index["graph"] = {
                key: value.get("outgoing", []) if isinstance(value, dict) else value
                for key, value in index.get("graph", {}).items()
            }
            stats = index.get("stats") or {}
            index["stats"] = {
                "total_notes": stats.get("total_notes", index.get("note_count", len(notes))),
                "total_words": stats.get("total_words", sum(n.get("word_count", 0) for n in notes.values())),
                "connections": stats.get("connections", sum(len(v) for v in index["graph"].values())),
            }
            return index
        except Exception as exc:
            return {"notes": {}, "graph": {}, "stats": {}, "error": f"Index error: {exc}"}

    def _note(self, key, note):
        note = dict(note)
        note.setdefault("title", key)
        path = note.get("path", "")
        if not note.get("content") and path:
            try:
                note["content"] = (VAULT_PATH / Path(path)).read_text(encoding="utf-8", errors="replace")
            except OSError:
                note["content"] = ""
        note["key"] = key
        return note

    def connections(self, key):
        return self.index.get("graph", {}).get(key, []) or []

    def search_vault(self, query):
        query = query.strip().lower()
        if not query:
            return []
        results = []
        for key, raw_note in self.index.get("notes", {}).items():
            note = self._note(key, raw_note)
            title = note.get("title", key).lower()
            content = note.get("content", "").lower()
            path = note.get("path", "").lower()
            score = (6 if query in title else 0) + (2 if query in path else 0) + (1 if query in content else 0)
            if score:
                note["_score"] = score
                results.append(note)
        return sorted(results, key=lambda n: (-n["_score"], n.get("title", "").lower()))[:20]

    def format_note_preview(self, note):
        title = note.get("title", note.get("key", "Untitled"))
        links = self.connections(note.get("key", title))
        content = note.get("content", "")
        return (f"{title}\n{'-' * 54}\nPath: {note.get('path', 'N/A')}\n"
                f"Words: {note.get('word_count', 0):,}\nConnections: {len(links)}\n\n"
                f"{content[:1200]}{'...' if len(content) > 1200 else ''}")

    def create_window(self):
        stats = self.index.get("stats", {})
        left = [
            [sg.Text("Brain Search", font=("Arial", 16, "bold"))],
            [sg.Input(key="SEARCH", size=(30, 1)), sg.Button("Search"), sg.Button("Refresh")],
            [sg.Multiline(size=(42, 28), key="RESULTS", disabled=True, font=("Courier", 10))],
        ]
        right = [
            [sg.Text("Vault Stats", font=("Arial", 14, "bold"))],
            [sg.Text(f"Notes: {stats.get('total_notes', 0):,}", key="STAT_NOTES")],
            [sg.Text(f"Words: {stats.get('total_words', 0):,}", key="STAT_WORDS")],
            [sg.Text(f"Connections: {stats.get('connections', 0):,}", key="STAT_CONNECTIONS")],
            [sg.HorizontalSeparator()], [sg.Text("Preview", font=("Arial", 14, "bold"))],
            [sg.Multiline(size=(55, 24), key="PREVIEW", disabled=True, font=("Courier", 9))],
        ]
        return sg.Window("BPFCoBrain", [[sg.Column(left), sg.Column(right)],
            [sg.Button("Open Folder"), sg.Button("Web Dashboard"), sg.Button("Settings"), sg.Button("Exit")]],
            size=(1050, 720), finalize=True)

    def refresh(self):
        self.index = self._load_index()
        stats = self.index.get("stats", {})
        self.window["STAT_NOTES"].update(f"Notes: {stats.get('total_notes', 0):,}")
        self.window["STAT_WORDS"].update(f"Words: {stats.get('total_words', 0):,}")
        self.window["STAT_CONNECTIONS"].update(f"Connections: {stats.get('connections', 0):,}")

    def open_dashboard(self):
        if self.http_process is None or self.http_process.poll() is not None:
            self.http_process = subprocess.Popen([sys.executable, "-m", "http.server", "8765"], cwd=VAULT_PATH,
                                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        webbrowser.open("http://127.0.0.1:8765/dashboard.html")

    def run(self):
        self.window = self.create_window()
        while True:
            event, values = self.window.read()
            if event in (sg.WIN_CLOSED, "Exit"):
                break
            if event == "Search":
                self.search_results = self.search_vault(values.get("SEARCH", ""))
                if not self.search_results:
                    self.window["RESULTS"].update("No results found.")
                    self.window["PREVIEW"].update("")
                    continue
                lines = [f"Found {len(self.search_results)} results:\n"]
                for i, note in enumerate(self.search_results, 1):
                    key = note.get("key", note.get("title", ""))
                    lines.append(f"{i}. {note.get('title', key)} | {note.get('word_count', 0):,} words | {len(self.connections(key))} links")
                self.window["RESULTS"].update("\n".join(lines))
                self.window["PREVIEW"].update(self.format_note_preview(self.search_results[0]))
            elif event == "Refresh":
                self.refresh()
                sg.popup("Vault index refreshed.", title="BPFCoBrain")
            elif event == "Open Folder":
                if hasattr(os, "startfile"):
                    os.startfile(str(VAULT_PATH))
            elif event == "Web Dashboard":
                self.open_dashboard()
            elif event == "Settings":
                sg.popup(f"Vault: {VAULT_PATH}\nIndex: {INDEX_FILE.name}\nVersion: {self.index.get('index_version', 'legacy')}", title="Settings")
        if self.http_process and self.http_process.poll() is None:
            self.http_process.terminate()
        self.window.close()


if __name__ == "__main__":
    BrainDesktop().run()
