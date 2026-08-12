#!/usr/bin/env python3
"""
Brain Desktop App - Standalone GUI for your Obsidian knowledge vault
Uses PySimpleGUI for native desktop window
"""

import sys
import os
import json
import re
import shutil
from pathlib import Path

# Windows UTF-8 fix
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    import PySimpleGUI as sg
except ImportError:
    print("Installing PySimpleGUI...")
    os.system("pip install PySimpleGUI -q")
    import PySimpleGUI as sg

# Set theme
sg.theme('DarkBlue3')

# Vault path
APP_PATH = Path(__file__).parent
VAULT_PATH = APP_PATH
INDEX_FILE = VAULT_PATH / '.vault-index.json'
IMPORT_FILE = VAULT_PATH / '.imports.json'


def resolve_credentials_path():
    """Ensure a local credentials.json exists, auto-installing it from common secret locations."""
    target = APP_PATH / 'credentials.json'
    if target.exists():
        return target

    # Direct env override: either a path or raw JSON payload.
    env_path = os.environ.get('BRAIN_CREDENTIALS_PATH') or os.environ.get('CREDENTIALS_PATH')
    if env_path:
        src = Path(env_path).expanduser()
        if src.exists() and src.is_file():
            shutil.copy2(src, target)
            return target
        raw_json = os.environ.get('BRAIN_CREDENTIALS_JSON') or os.environ.get('CREDENTIALS_JSON')
        if raw_json:
            try:
                payload = json.loads(raw_json)
                if isinstance(payload, dict):
                    target.write_text(json.dumps(payload, indent=2), encoding='utf-8')
                    return target
            except Exception:
                pass

    candidate_paths = [
        APP_PATH / 'credentials.json',
        VAULT_PATH / 'credentials.json',
        Path.home() / 'credentials.json',
        Path.home() / 'Documents' / 'credentials.json',
        Path.home() / 'AppData' / 'Local' / 'BPFCoBrain' / 'credentials.json',
        Path.home() / 'AppData' / 'Roaming' / 'BPFCoBrain' / 'credentials.json',
    ]
    for candidate in candidate_paths:
        if candidate.exists() and candidate.is_file() and candidate != target:
            try:
                shutil.copy2(candidate, target)
                return target
            except Exception:
                continue

    try:
        prompt_result = sg.popup_yes_no(
            'No local credentials.json was found. Do you want the app to keep the secret on this machine and create it manually now?',
            title='Credentials Required',
            default_button='Yes',
            cancel_button='No',
        )
    except TypeError:
        prompt_result = sg.popup_yes_no(
            'No local credentials.json was found. Do you want the app to keep the secret on this machine and create it manually now?',
            title='Credentials Required',
        )

    if not prompt_result:
        return None

    sample = '{\n  "web": {\n    "client_id": "...",\n    "project_id": "...",\n    "auth_uri": "https://accounts.google.com/o/oauth2/auth",\n    "token_uri": "https://oauth2.googleapis.com/token",\n    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",\n    "client_secret": "..."\n  },\n  "anthropic_api_key": "sk-..."\n}'
    try:
        raw = sg.popup_get_text(
            'Paste your local credentials JSON. It will be saved next to the app and ignored by git.',
            default_text=sample,
            multiline=True,
            size=(80, 18),
            title='Install Local Credentials',
        )
    except TypeError:
        raw = sg.popup_get_text(
            'Paste your local credentials JSON. It will be saved next to the app and ignored by git.',
            default_text=sample,
            size=(80, 18),
            title='Install Local Credentials',
        )
    if raw is None or not raw.strip():
        return None

    try:
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError('Expected a JSON object.')
        target.write_text(json.dumps(payload, indent=2), encoding='utf-8')
        return target
    except Exception as exc:
        sg.popup(f'Invalid JSON: {exc}\n\nPlease paste a valid credentials object.', title='Credentials Error')
        return None


class BrainDesktop:
    def __init__(self):
        self.credentials_path = resolve_credentials_path()
        self.index = self._load_index()
        self.window = None
        self.search_results = []
        
    def _load_index(self):
        """Load vault index"""
        if not INDEX_FILE.exists():
            return {"notes": [], "graph": {}, "stats": {}}
        try:
            with open(INDEX_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"notes": [], "graph": {}, "stats": {}}
    
    def search_vault(self, query):
        """Search vault notes"""
        if not query.strip():
            return []
        
        query_lower = query.lower()
        results = []
        
        for note in self.index.get('notes', []):
            name_match = query_lower in note.get('name', '').lower()
            content_match = query_lower in note.get('content', '').lower()
            tags_match = any(query_lower in tag.lower() for tag in note.get('tags', []))
            
            if name_match or content_match or tags_match:
                score = 0
                if name_match:
                    score += 3
                if tags_match:
                    score += 2
                if content_match:
                    score += 1
                results.append((note, score))
        
        # Sort by score
        results.sort(key=lambda x: x[1], reverse=True)
        return [r[0] for r in results[:20]]
    
    def get_note_connections(self, note_name):
        """Get connected notes"""
        graph = self.index.get('graph', {})
        connections = graph.get(note_name, {})
        return connections.get('outgoing', [])
    
    def format_note_preview(self, note):
        """Format note for display"""
        preview = f"📄 {note.get('name', 'Untitled')}\n"
        preview += f"─" * 50 + "\n"
        preview += f"Path: {note.get('path', 'N/A')}\n"
        preview += f"Type: {note.get('type', 'Unknown')}\n"
        preview += f"Words: {note.get('word_count', 0)}\n"
        
        tags = note.get('tags', [])
        if tags:
            preview += f"Tags: {', '.join(tags[:5])}\n"
        
        connections = note.get('connections', 0)
        preview += f"Connections: {connections}\n"
        
        content = note.get('content', '')
        if len(content) > 200:
            preview += f"\n{content[:200]}...\n"
        else:
            preview += f"\n{content}\n"
        
        return preview
    
    def create_window(self):
        """Create main window"""
        stats = self.index.get('stats', {})
        note_count = stats.get('total_notes', 0)
        word_count = stats.get('total_words', 0)
        connection_count = stats.get('connections', 0)
        
        # Left column - Search and results
        left_column = [
            [sg.Text('🧠 Brain Search', font=('Arial', 16, 'bold'))],
            [sg.InputText(key='SEARCH', size=(30, 1), font=('Arial', 12))],
            [sg.Button('🔍 Search', size=(10, 1)), sg.Button('🔄 Refresh', size=(10, 1))],
            [sg.Multiline(size=(35, 25), key='RESULTS', disabled=True, font=('Courier', 10))],
        ]
        
        # Right column - Preview and stats
        right_column = [
            [sg.Text('📊 Vault Stats', font=('Arial', 14, 'bold'))],
            [sg.Text(f'Notes: {note_count}', font=('Arial', 11))],
            [sg.Text(f'Words: {word_count:,}', font=('Arial', 11))],
            [sg.Text(f'Connections: {connection_count}', font=('Arial', 11))],
            [sg.Text('─' * 30)],
            [sg.Text('📝 Preview', font=('Arial', 14, 'bold'))],
            [sg.Multiline(size=(35, 20), key='PREVIEW', disabled=True, font=('Courier', 9))],
        ]
        
        # Layout
        layout = [
            [sg.Column(left_column), sg.Column(right_column)],
            [sg.Button('📂 Open Folder'), sg.Button('🌐 Web Dashboard'), sg.Button('⚙️ Settings'), sg.Button('❌ Exit')],
        ]
        
        window = sg.Window('🧠 Brain Desktop', layout, size=(900, 700), finalize=True)
        return window
    
    def run(self):
        """Run the app"""
        self.window = self.create_window()
        
        while True:
            event, values = self.window.read()
            
            if event in ('Exit', None, '❌ Exit'):
                break
            
            if event == '🔍 Search':
                query = values['SEARCH']
                self.search_results = self.search_vault(query)
                
                if not self.search_results:
                    self.window['RESULTS'].update('No results found.')
                    self.window['PREVIEW'].update('')
                else:
                    results_text = f"Found {len(self.search_results)} results:\n\n"
                    for i, note in enumerate(self.search_results[:10], 1):
                        results_text += f"{i}. {note.get('name', 'Untitled')} ({note.get('type', '?')})\n"
                        results_text += f"   Words: {note.get('word_count', 0)} | Connections: {note.get('connections', 0)}\n\n"
                    
                    self.window['RESULTS'].update(results_text)
                    
                    # Show first result preview
                    if self.search_results:
                        preview = self.format_note_preview(self.search_results[0])
                        self.window['PREVIEW'].update(preview)
            
            if event == '🔄 Refresh':
                self.index = self._load_index()
                sg.popup('✅ Vault refreshed!', title='Refreshed')
            
            if event == '📂 Open Folder':
                os.startfile(str(VAULT_PATH))
            
            if event == '🌐 Web Dashboard':
                dashboard_path = VAULT_PATH / 'dashboard.html'
                if dashboard_path.exists():
                    os.startfile(str(dashboard_path))
                else:
                    sg.popup('❌ dashboard.html not found', title='Error')
            
            if event == '⚙️ Settings':
                sg.popup(f'Vault Path: {VAULT_PATH}\n\nNotes: {len(self.index.get("notes", []))}\n\nVersion: 1.0', 
                        title='Settings')
        
        self.window.close()

if __name__ == '__main__':
    app = BrainDesktop()
    app.run()
