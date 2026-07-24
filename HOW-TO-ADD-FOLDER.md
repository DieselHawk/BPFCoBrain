# 📂 How to Add a Folder to the Brain

## 🚀 Quick Start (3 Methods)

---

## **Method 1: Using Brain Dashboard (Easiest)** ⭐

### Step 1: Launch Brain Desktop
```
Double-click the Brain icon on your Desktop
```

### Step 2: Choose "Import Files"
```
In the menu:
  1. Search Brain
  2. View Graph
  3. Import Files  ← Click this
  4. Show Context
  5. Check Tokens
  6. List Notes
  7. Help
  8. Exit
```

### Step 3: Paste Folder Path
```
When prompted:
  Enter folder path: C:\Users\Jaques\Documents\MyFolder
  
The brain will:
  ✅ Import all files
  ✅ Auto-organize by type
  ✅ Index everything
  ✅ Create connections
```

---

## **Method 2: Using Python Script (Most Control)**

### One Command:
```powershell
cd "C:\Users\Jaques\Documents\Obsidian Vault"
python omniroute.py --import "C:\path\to\your\folder"
```

### Example:
```powershell
python omniroute.py --import "C:\Users\Jaques\Documents\Projects\MyCode"
```

### Output:
```
📂 Importing: C:\Users\Jaques\Documents\Projects\MyCode
  ✅ Found 45 files
  ✅ Importing batch 1 (50 files)...
  ✅ All imported!
  
📊 Results:
  - Python files: 30 → 03-References
  - Markdown files: 10 → 01-Concepts
  - Text files: 5 → 04-Fleeting-Notes
  
🔄 Indexing...
✅ Done! Brain updated.
```

---

## **Method 3: Direct Copy (Manual)**

### Step 1: Decide Which Folder
```
Your vault has these folders:

📁 00-Inbox           ← Temporary/new stuff
📁 01-Concepts        ← Ideas and topics
📁 02-Projects        ← Active projects
📁 03-References      ← Code and docs (819 files already here!)
📁 04-Fleeting-Notes  ← Temporary thoughts
📁 05-Atomic          ← Single-idea notes
📁 06-Maps-of-Content ← Knowledge hierarchies
```

### Step 2: Copy Files There
```
1. Open: C:\Users\Jaques\Documents\Obsidian Vault
2. Drag-drop files into the folder you want
3. Or copy-paste manually
```

### Step 3: Refresh Index
```powershell
cd "C:\Users\Jaques\Documents\Obsidian Vault"
python vault-indexer.py
```

---

## 📋 File Type Organization

When you import, files go here:

| File Type | Goes To | Purpose |
|-----------|---------|---------|
| `.py`, `.js`, `.ts` | `03-References` | Code files |
| `.md` | `01-Concepts` | Documentation |
| `.txt` | `04-Fleeting-Notes` | Text/notes |
| `.json`, `.yaml` | `03-References` | Data configs |
| Everything else | `00-Inbox` | Sort manually |

---

## 🎯 Recommended Workflow

### For Code Folders:
```powershell
# Import entire project
python omniroute.py --import "C:\Projects\MyApp"

# Files automatically:
# ✅ Get organized by type
# ✅ Get indexed
# ✅ Get connected via links
```

### For Document Folders:
```powershell
# Import documentation
python omniroute.py --import "C:\Docs\MyDocs"

# Everything indexed and searchable
```

### For Mixed Folders:
```powershell
# Import anything
python omniroute.py --import "C:\Random\Stuff"

# Brain auto-sorts by file type
```

---

## ⚙️ Advanced: Import Options

### Import with Specific Folder
```powershell
python omniroute.py --import "C:\path\to\folder" --target "02-Projects"
```
→ Everything goes to `02-Projects` instead of auto-sorting

### Import Single File
```powershell
python omniroute.py --import "C:\path\to\file.py"
```
→ Works with single files too

### Check What Will Import
```powershell
python omniroute.py --import "C:\path" --dry-run
```
→ Shows what would happen (without actually importing)

---

## 🔄 Auto-Sync (Keep Folder Updated)

Coming soon: File watcher that auto-imports new files

For now, re-run import command whenever folder changes:
```powershell
# Run this whenever you update the source folder
python omniroute.py --import "C:\path\to\folder"

# Smart import skips duplicates using hashes ✅
```

---

## 📂 Before & After

### Before Import:
```
Your Computer
├─ Documents
│  ├─ MyProject
│  │  ├─ main.py
│  │  ├─ utils.py
│  │  ├─ README.md
│  │  └─ config.json
│  └─ (isolated files)
```

### After Import:
```
Brain Vault
├─ 03-References
│  ├─ main-a1b2c3.md
│  ├─ utils-d4e5f6.md
│  └─ config-g7h8i9.md
├─ 01-Concepts
│  └─ README-j0k1l2.md
└─ [All indexed + connected] ✅
```

---

## ✅ Your Current Setup

Right now your brain has:
- ✅ 793 notes
- ✅ 719 Python files (in 03-References)
- ✅ 34 text files
- ✅ 10 markdown files

### To Add More:

**Option A: Use Brain Dashboard**
```
python brain-dashboard.py
→ Select "3. Import Files"
→ Paste folder path
→ Done!
```

**Option B: One-liner**
```powershell
python omniroute.py --import "C:\path\to\folder"
```

**Option C: Manual copy**
```
Drag files to appropriate folder
python vault-indexer.py
```

---

## 🚀 Try It Now

### Add Your Documents Folder:
```powershell
cd "C:\Users\Jaques\Documents\Obsidian Vault"

# Import a specific folder
python omniroute.py --import "C:\Users\Jaques\Documents\MyFolder"

# Check results
python brain-dashboard.py
# Select "6. List Notes" to see updates
```

---

## ❓ FAQ

**Q: Will it duplicate files?**
A: No! Uses hash-based deduplication. Same file = skipped.

**Q: Can I import from Google Drive / Dropbox?**
A: Copy to local folder first, then import.

**Q: What if I import wrong folder?**
A: No problem. Duplicates are skipped. Delete wrong notes manually in Obsidian.

**Q: Does it update when I change source?**
A: Not automatically yet. Re-run import command to update.

**Q: How many files can I import?**
A: Unlimited! (Currently 793 notes, can scale to 10,000+)

---

**Ready to expand your brain?** 🧠📂
