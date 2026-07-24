#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BrainDash - Simple visual dashboard for your brain"""

import sys, json, re, subprocess
from pathlib import Path
from typing import Dict, List

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class BrainDash:
    def __init__(self):
        self.vault = Path.home() / "Documents" / "Obsidian Vault"
        self.imports_log = self.vault / ".imports.json"
        self.index_file = self.vault / ".vault-index.json"
    
    def show_menu(self):
        """Show main dashboard"""
        print("\n" + "="*60)
        print("         🧠 BPFCoBrain Dashboard")
        print("="*60 + "\n")
        
        # Show stats
        self._show_stats()
        
        print("\nWhat do you want to do?\n")
        print("  [1] 📊 Search for a concept")
        print("  [2] 🔗 View graph visualization (open Obsidian)")
        print("  [3] 📁 Import new files")
        print("  [4] 💬 Get context for Claude")
        print("  [5] ⚡ Check token usage")
        print("  [6] 📖 View all available notes")
        print("  [7] 🚀 Open Obsidian vault")
        print("  [8] ❓ Help")
        print("  [0] Exit\n")
        
        choice = input("Choose (0-8): ").strip()
        return choice
    
    def _show_stats(self):
        """Show quick stats"""
        if self.index_file.exists():
            data = json.loads(self.index_file.read_text())
            notes = data.get('note_count', 0)
            print(f"  📚 Brain Size: {notes} notes")
            print(f"  🔗 Connections: {data.get('note_count', 0)} files")
            print(f"  💾 Location: {self.vault}\n")
    
    def search_brain(self):
        """Search for concept"""
        query = input("\nWhat would you like to search for? ").strip()
        if not query:
            return
        
        print(f"\n🔍 Searching for: '{query}'...")
        result = subprocess.run(
            ["python", "query-cli.py", query, "--format", "json"],
            cwd=str(self.vault),
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                if data.get("status") == "success":
                    print(f"\n✅ Found: {data['total_matches']} matches")
                    print(f"📄 Primary: {data['primary']}\n")
                    
                    print("Context found in:")
                    for note in data['context']:
                        print(f"  • {note}")
                    
                    copy = input("\nCopy context to clipboard? (y/n): ").strip().lower()
                    if copy == 'y':
                        self._get_full_context(query)
            except:
                print("Error parsing results")
        else:
            print("❌ No matches found")
    
    def _get_full_context(self, query):
        """Get and display full context"""
        result = subprocess.run(
            ["python", "query-cli.py", query, "--format", "claude"],
            cwd=str(self.vault),
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("\n" + "="*60)
            print("CONTEXT (Ready to paste into Claude):")
            print("="*60)
            print(result.stdout)
            print("="*60)
            print("\n✅ Copy the context above and paste into Claude!\n")
    
    def import_files(self):
        """Import new files"""
        print("\n📁 Import Files")
        print("-" * 40)
        
        files_input = input("Enter file path(s) to import\n(Use commas for multiple): ").strip()
        if not files_input:
            return
        
        files = [f.strip() for f in files_input.split(',')]
        
        category = input("\nCategory? (default: 03-References): ").strip() or "03-References"
        
        print(f"\nImporting {len(files)} file(s)...")
        
        for f in files:
            result = subprocess.run(
                ["python", "omniroute.py", "import", f, "--category", category],
                cwd=str(self.vault),
                capture_output=True,
                text=True
            )
            if "✓" in result.stdout:
                print(f"  ✅ {Path(f).name}")
            else:
                print(f"  ❌ {Path(f).name}")
        
        print("\n✅ Done!")
    
    def check_tokens(self):
        """Show token status"""
        result = subprocess.run(
            ["python", "omniroute.py", "status"],
            cwd=str(self.vault),
            capture_output=True,
            text=True
        )
        print("\n" + result.stdout)
    
    def open_obsidian(self):
        """Open Obsidian with vault"""
        print("\n🚀 Opening Obsidian...")
        try:
            # Try to open Obsidian with vault
            subprocess.Popen(["start", "obsidian://open?path=" + str(self.vault)], shell=True)
            print("✅ Obsidian should open in a moment")
            print("   Tip: Press Ctrl+G to see the graph!")
        except:
            print("❌ Could not open Obsidian")
            print(f"   Try manually opening: {self.vault}")
    
    def list_notes(self):
        """Show all notes"""
        if self.index_file.exists():
            data = json.loads(self.index_file.read_text())
            notes = data.get('notes', {})
            
            print(f"\n📚 All {len(notes)} Notes:\n")
            
            for i, (title, info) in enumerate(sorted(notes.items())[:50]):
                folder = info.get('folder', 'Unknown')
                print(f"  • {title} ({folder})")
            
            if len(notes) > 50:
                print(f"\n  ... and {len(notes) - 50} more")
        else:
            print("❌ Index not found")
    
    def show_help(self):
        """Show help"""
        print("""
🧠 BPFCoBrain - Quick Help

How it works:
1. All your files are imported into a searchable brain
2. Search for concepts → get context
3. Copy context → paste into Claude
4. Graph shows connections between ideas

Key commands:
• Search    → Find any concept in your brain
• Graph     → See visual connections in Obsidian
• Import    → Add new files to brain
• Tokens    → Check Claude model availability
• Obsidian  → Open vault in Obsidian app

Tips:
✨ Use Ctrl+G in Obsidian to see the graph
✨ Search for related terms to find connections
✨ Copy context into Claude for intelligent answers
✨ Brain auto-switches models when tokens run out
        """)

def main():
    dash = BrainDash()
    
    while True:
        choice = dash.show_menu()
        
        if choice == "1":
            dash.search_brain()
        elif choice == "2":
            dash.open_obsidian()
            print("   (Graph will appear when you press Ctrl+G)")
        elif choice == "3":
            dash.import_files()
        elif choice == "4":
            query = input("\nWhat should I find context for? ").strip()
            if query:
                dash._get_full_context(query)
        elif choice == "5":
            dash.check_tokens()
        elif choice == "6":
            dash.list_notes()
        elif choice == "8":
            dash.show_help()
        elif choice == "0":
            print("\n👋 Goodbye!\n")
            break
        else:
            print("Invalid choice")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
