# BOB Manus Integration Guide

**BOB** is the contextual answerer for the Manus platform. It queries the BPFCoBrain vault and returns intelligent, context-aware answers using Claude AI, enriched with Gmail and OneDrive evidence.

---

## 1. Prerequisites

- Python 3.9+
- Google OAuth credentials (Gmail + Drive access)
- Microsoft Azure app registration (OneDrive access)
- Anthropic API key (Claude)

---

## 2. Setup Steps

### 2.1 Install Dependencies

```bash
cd c:\BPFCo\BPFCoBrain
pip install -r requirements.txt
```

### 2.2 Google OAuth Setup (Gmail + Google Drive)

Already configured if you have `credentials.json`. If not:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **Gmail API** and **Google Drive API**
4. Create an **OAuth 2.0 Desktop Client**
5. Download JSON and save as `credentials.json` in the BPFCoBrain folder

See `GOOGLE-OAUTH-SETUP.md` for detailed steps.

### 2.3 Microsoft Azure Setup (OneDrive)

1. Go to [Azure Portal](https://portal.azure.com/)
2. Create an **App Registration** with:
   - **Name:** BPFCo Brain
   - **Supported account types:** Accounts in any organizational directory
   - **Redirect URI:** `http://localhost`

3. Grant **API Permissions:**
   - Microsoft Graph → Files.Read.All
   - Microsoft Graph → Mail.Read (optional)
   - Microsoft Graph → Calendars.Read (optional)

4. Create a **Client Secret** (copy the value)

5. Create `.env` file in BPFCoBrain folder:
```env
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=common
```

First run of `ondrive_hunt.py` will prompt for authentication.

### 2.4 Anthropic API Key

Get your API key from [platform.anthropic.com](https://platform.anthropic.com/account/keys)

Set environment variable:
```bash
$env:ANTHROPIC_API_KEY = "sk-ant-xxx"
```

---

## 3. Usage

### 3.1 Sync Evidence from All Sources

Sync Gmail, Google Drive, and OneDrive into `Evidence.md`:

```bash
python main.py "case number" "property dispute" "fraud" --vault . --credentials credentials.json --token token.json --onedrive-token onedrive_token.json
```

This creates/updates `Evidence.md` with all matching documents from:
- **Gmail:** Keyword search in inbox
- **Google Drive:** Filename/content search
- **OneDrive:** File search across all folders

### 3.2 Use BOB CLI

Ask BOB a question directly:

```bash
python manus_bot.py "What is the status of Cas-125/07/2025?"
```

BOB will:
1. Search the BPFCoBrain vault for relevant notes
2. Query Gmail for matching messages
3. Query OneDrive for matching documents
4. Use Claude to synthesize a contextual answer

**Output:**
```
ANSWER:
────────────────────────────────────────────
Based on the brain vault and evidence:
Cas-125/07/2025 is an active criminal fraud investigation...
────────────────────────────────────────────

Sources: Cas-125/07/2025, Gmail: Investigation Update, OneDrive: Evidence-Summary.docx
Tokens used: 1245 input, 342 output
```

### 3.3 Start Manus API Server

Run the Flask API for integration with Manus platform:

```bash
python manus_api.py
```

Server runs on `http://localhost:5000`

**API Endpoints:**

#### Health Check
```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "service": "BOB Manus Contextual Answerer",
  "vault": "c:\\BPFCo\\BPFCoBrain\\Brain"
}
```

#### Ask BOB
```bash
POST /answer
Content-Type: application/json

{
  "query": "What happened with the property sale?",
  "include_gmail": true,
  "include_ondrive": true,
  "context_depth": 2
}
```

Response:
```json
{
  "query": "What happened with the property sale?",
  "answer": "According to the sale agreement...",
  "sources": ["Property Dispute", "Gmail: Payment Status", "OneDrive: Sale Agreement.pdf"],
  "context_used": {
    "brain_notes": 5,
    "gmail_messages": 3,
    "ondrive_files": 2
  },
  "model": "claude-3-5-sonnet-20241022",
  "usage": {
    "input_tokens": 2145,
    "output_tokens": 623
  }
}
```

#### Search Brain
```bash
GET /brain/search?q=trustees&depth=2
```

Response:
```json
{
  "status": "success",
  "primary": "Trustee Defalcation",
  "total_matches": 12,
  "context": {
    "Trustee Defalcation": {...},
    "Cas-125/07/2025": {...}
  }
}
```

#### Batch Query
```bash
POST /answer/batch
Content-Type: application/json

{
  "queries": ["Status?", "What about the property?", "Who are the parties?"],
  "include_gmail": true,
  "include_ondrive": true
}
```

#### Sync Evidence
```bash
POST /sync
Content-Type: application/json

{
  "keywords": ["case number", "property", "fraud investigation"]
}
```

---

## 4. Environment Variables

```bash
# Paths
BRAIN_VAULT = c:\BPFCo\BPFCoBrain\Brain  # Obsidian vault location
PORT = 5000                                # API server port
DEBUG = False                              # Enable debug mode

# Google
GOOGLE_CREDENTIALS = credentials.json      # Google OAuth file
GOOGLE_TOKEN = token.json                  # Cached Google token

# Microsoft
ONEDRIVE_TOKEN = onedrive_token.json       # Cached OneDrive token
AZURE_CLIENT_ID = xxx
AZURE_CLIENT_SECRET = xxx
AZURE_TENANT_ID = common

# AI
ANTHROPIC_API_KEY = sk-ant-xxx            # Claude API key
```

---

## 5. Architecture

```
BPFCoBrain/
├── main.py              # Sync orchestrator (Gmail + Drive + OneDrive)
├── manus_bot.py         # BOB logic (query brain + context synthesis)
├── manus_api.py         # Flask API for Manus platform
│
├── gmail_hunt.py        # Gmail integration
├── drive_hunt.py        # Google Drive integration
├── ondrive_hunt.py      # OneDrive integration
├── google_auth.py       # Google OAuth
│
├── query-cli.py         # Vault indexer & search
├── vault-indexer.py     # Vault indexing for Claude
├── obsidian_writer.py   # Write to Evidence.md
│
├── Brain/               # Obsidian vault (793+ notes)
│   ├── 02-Projects/
│   ├── 03-References/
│   ├── Evidence.md      # Gmail/Drive/OneDrive synced content
│   └── ...
│
└── requirements.txt
```

### Data Flow

```
Query → BOB Manus
  │
  ├─→ VaultIndexer.query()     [Brain notes]
  │
  ├─→ GmailHunter.hunt_keywords()    [Gmail evidence]
  │
  ├─→ OneDriveHunter.hunt_files()    [OneDrive files]
  │
  └─→ Claude API.messages.create()   [Synthesize answer]
        │
        └─→ Return contextual answer + sources
```

---

## 6. Troubleshooting

### "Cannot authenticate with OneDrive"
- Ensure Azure app registration is correct
- Delete `onedrive_token.json` and re-authenticate
- Check CLIENT_ID in `ondrive_hunt.py`

### "Gmail search returns no results"
- Verify Gmail API is enabled in Google Cloud Console
- Delete `token.json` and re-authorize
- Check keyword spelling

### "OneDrive files not found"
- OneDrive search is case-insensitive but requires exact filename match (substring)
- Ensure files are in personal OneDrive, not shared

### "Claude API errors"
- Check `ANTHROPIC_API_KEY` is set
- Verify key is valid at platform.anthropic.com
- Check token usage (may have hit rate limit)

### "Brain vault not found"
- Set `BRAIN_VAULT` environment variable
- Ensure `Brain/` folder exists with Obsidian notes

---

## 7. Integration with Manus Platform

To connect BOB to the Manus evidence portal:

1. **Start BOB API:**
   ```bash
   python manus_api.py
   ```

2. **Configure Manus webhook:**
   - Set webhook URL to `http://your-server:5000/answer`
   - Include query in POST request

3. **Test integration:**
   ```bash
   curl -X POST http://localhost:5000/answer \
     -H "Content-Type: application/json" \
     -d '{"query": "What is the evidence?"}'
   ```

4. **Deploy:**
   - Use production WSGI server (e.g., gunicorn)
   - Configure SSL/TLS
   - Set up authentication if needed

---

## 8. Example Queries for BOB

- "What is the status of Cas-125/07/2025?"
- "Who are the main parties involved?"
- "What is the timeline of events?"
- "What evidence is in the Gmail correspondence?"
- "Summarize the legal arguments"
- "What documents support the claim?"
- "Who is investigating this case?"
- "What is the property in dispute?"

---

**Created:** 2026-09-01  
**Version:** 1.0  
**Author:** BPFCoBrain System
