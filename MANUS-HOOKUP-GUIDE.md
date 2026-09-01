# Hooking Up BOB with Manus Platform

**Status:** Ready for integration with evidportal-fvptvdpk.manus.space

---

## 1. Quick Start

### 1.1 Prerequisites
- Python 3.9+
- Dependencies installed: `pip install -r requirements.txt`
- Google OAuth credentials (Gmail/Drive)
- Anthropic API key
- Azure credentials for OneDrive (optional)

### 1.2 Start BOB Server

```bash
cd c:\BPFCo\BPFCoBrain

# Set environment variables
$env:ANTHROPIC_API_KEY = "sk-ant-your-key"
$env:FLASK_ENV = "production"
$env:MANUS_API_URL = "https://evidportal-fvptvdpk.manus.space"

# Start API server (port 5000)
python manus_api.py
```

Server is now available at `http://localhost:5000` with the following Manus endpoints:

- `POST /manus/webhook` - Main query endpoint
- `POST /manus/case/<case_id>/search` - Case-specific search
- `POST /manus/case/<case_id>/evidence` - Evidence search
- `GET /manus/status` - Health check

---

## 2. Manus Platform Integration

### 2.1 Register Webhook in Manus

1. Go to **Settings** → **Integrations** in Manus
2. Click **Add Bot Integration**
3. Fill in:
   - **Bot Name:** BOB Manus
   - **Webhook URL:** `http://your-server:5000/manus/webhook`
   - **Method:** POST
   - **Headers:** 
     ```
     Content-Type: application/json
     ```
   - **Authentication:** (optional) Set MANUS_API_KEY environment variable

4. Click **Test Connection**
   - Should see: `{"status": "success"}`

5. Click **Enable** to activate

### 2.2 Configure for Each Case

1. Go to **Case Settings** → **Cas-125/07/2025**
2. Click **AI Assistant** tab
3. Select **BOB Manus** from dropdown
4. Enable:
   - ✅ Query mode (contextual answers)
   - ✅ Evidence search
   - ✅ Document linking
5. Save

---

## 3. Webhook Request/Response Format

### 3.1 Basic Query (from Manus)

**Request:**
```json
{
  "event": "query_bot",
  "query": "What happened with the property sale?",
  "case_id": "Cas-125/07/2025",
  "chapter": "Property Dispute",
  "user_id": "investigator@case.gov",
  "session_id": "sess_abc123"
}
```

**Response:**
```json
{
  "status": "success",
  "answer": "According to the sale agreement...",
  "sources": ["Property Dispute", "Gmail: Payment Status"],
  "confidence": 0.95,
  "action_items": [
    "Resolve title deed location",
    "Follow up on payment frustration"
  ],
  "session_id": "sess_abc123",
  "context_used": {
    "brain_notes": 5,
    "gmail_messages": 2,
    "ondrive_files": 1
  }
}
```

### 3.2 Case Search

**Request:**
```json
{
  "query": "fraud evidence",
  "chapters": ["Fraud Unit", "Banks"],
  "case_id": "Cas-125/07/2025"
}
```

**Response:**
```json
{
  "case_id": "Cas-125/07/2025",
  "query": "fraud evidence",
  "answer": "The fraud indicators include...",
  "sources": ["Fraud Unit: Investigation", "Banks: Capitec Fraud"],
  "context_used": {...}
}
```

### 3.3 Evidence Search

**Request:**
```json
{
  "query": "What evidence supports fraud?",
  "evidence_type": "financial",
  "min_confidence": 0.8,
  "case_id": "Cas-125/07/2025"
}
```

**Response:**
```json
{
  "case_id": "Cas-125/07/2025",
  "evidence_found": true,
  "answer": "Financial evidence includes...",
  "sources": ["Transaction Records", "Bank Statements"],
  "confidence": 0.95
}
```

---

## 4. Deployment Options

### 4.1 Local Development (Testing)

```bash
# On your machine
python manus_api.py

# Share tunnel (for Manus to reach you)
# Use ngrok: ngrok http 5000
# Then use ngrok URL in Manus settings
```

### 4.2 Deploy to Server (Production)

#### Option A: Python WSGI Server (Gunicorn)

```bash
# Install
pip install gunicorn

# Run
gunicorn -w 4 -b 0.0.0.0:5000 manus_api:app
```

#### Option B: Docker

```dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Copy credentials and tokens (if using secrets)
COPY credentials.json .
COPY token.json .
COPY onedrive_token.json .

ENV FLASK_ENV=production
ENV ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
ENV AZURE_CLIENT_ID=${AZURE_CLIENT_ID}

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "manus_api:app"]
```

Build and run:
```bash
docker build -t bob-manus .
docker run -e ANTHROPIC_API_KEY=sk-ant-... -p 5000:5000 bob-manus
```

#### Option C: Cloud Deployment

**Google Cloud Run:**
```bash
gcloud run deploy bob-manus \
  --source . \
  --platform managed \
  --region us-central1 \
  --set-env-vars ANTHROPIC_API_KEY=sk-ant-...
```

**AWS Lambda:**
```bash
# Use Zappa
pip install zappa
zappa init
zappa deploy production
```

---

## 5. Environment Variables

Create `.env` file or set in deployment:

```bash
# Flask
FLASK_ENV=production
DEBUG=False

# BOB
BRAIN_VAULT=./Brain
ANTHROPIC_API_KEY=sk-ant-your-key-here
GOOGLE_CREDENTIALS=credentials.json
GOOGLE_TOKEN=token.json
ONEDRIVE_TOKEN=onedrive_token.json

# Azure (OneDrive)
AZURE_CLIENT_ID=your-azure-client-id
AZURE_CLIENT_SECRET=your-azure-client-secret
AZURE_TENANT_ID=common

# Manus
MANUS_API_URL=https://evidportal-fvptvdpk.manus.space
MANUS_API_KEY=your-manus-api-key

# Server
PORT=5000
HOST=0.0.0.0
```

---

## 6. API Endpoints Reference

### Health & Status

**GET `/health`**
- Check if BOB is running
- Response: `{"status": "healthy", "service": "BOB Manus..."}`

**GET `/manus/status`**
- Check if Manus connector is ready
- Response: `{"status": "ready", "components": {...}}`

### Query Endpoints

**POST `/answer`**
- General query (no case context)
- Body: `{"query": "...", "include_gmail": true, "include_ondrive": true}`

**POST `/manus/webhook`**
- Manus case-aware query
- Body: `{"event": "query_bot", "query": "...", "case_id": "..."}`

**POST `/manus/case/<case_id>/search`**
- Search within specific case
- Body: `{"query": "...", "chapters": [...]}`

**POST `/manus/case/<case_id>/evidence`**
- Search for evidence
- Body: `{"query": "...", "evidence_type": "..."}`

**POST `/answer/batch`**
- Multiple queries
- Body: `{"queries": ["q1", "q2", ...]}`

### Sync & Search

**POST `/sync`**
- Trigger Gmail/Drive/OneDrive sync
- Body: `{"keywords": ["keyword1", "keyword2", ...]}`

**GET `/brain/search`**
- Search vault
- Params: `?q=searchterm&depth=2`

---

## 7. Testing the Integration

### 7.1 Test BOB Locally

```bash
# Terminal 1: Start API
python manus_api.py

# Terminal 2: Test health
curl http://localhost:5000/health

# Test Manus connector status
curl http://localhost:5000/manus/status

# Test query
curl -X POST http://localhost:5000/answer \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Cas-125?"}'

# Test Manus webhook
curl -X POST http://localhost:5000/manus/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "event": "query_bot",
    "query": "What is the status?",
    "case_id": "Cas-125/07/2025",
    "chapter": "Fraud Unit",
    "session_id": "test123"
  }'
```

### 7.2 Test in Manus UI

1. Go to **Cas-125/07/2025** case
2. Click **Ask BOB**
3. Enter query: "What is the fraud investigation status?"
4. Should see:
   - Answer synthesized from vault + Gmail + OneDrive
   - Sources cited
   - Action items if applicable

### 7.3 Troubleshooting

**"Connection refused"**
- Ensure API server is running: `python manus_api.py`
- Check firewall/port access

**"ANTHROPIC_API_KEY not set"**
- Set: `$env:ANTHROPIC_API_KEY = "sk-ant-xxx"`

**"Vault path not found"**
- Ensure `Brain/` folder exists in BPFCoBrain directory
- Or set `BRAIN_VAULT` env var to correct path

**"OneDrive auth failed"**
- Set `AZURE_CLIENT_ID` environment variable
- First run will prompt for auth
- Token is cached in `onedrive_token.json`

**"No Gmail results"**
- Ensure `credentials.json` exists
- Check Gmail API is enabled in Google Cloud Console
- Delete `token.json` and re-authenticate

---

## 8. Monitoring & Logging

### View Logs

**Local:**
```bash
# Check console output from python manus_api.py
```

**Production (Gunicorn):**
```bash
# Gunicorn logs to stderr
gunicorn -w 4 --log-level debug manus_api:app
```

**Cloud:**
- Google Cloud Run: Check Cloud Logging
- AWS Lambda: Check CloudWatch Logs

### Metrics to Monitor

- Response time (should be <2 seconds)
- Error rate (should be <1%)
- Token usage (track Claude API costs)
- Vault indexing time

---

## 9. Security Considerations

### API Security

- ✅ Use HTTPS in production (not HTTP)
- ✅ Set strong MANUS_API_KEY if using auth
- ✅ Don't expose credentials in URLs
- ✅ Use environment variables for secrets
- ✅ Implement rate limiting for production

### Data Privacy

- Gmail: Read-only access via official API
- OneDrive: Read-only, encrypted token storage
- Claude: Respects Anthropic data policies
- Vault: Local storage, not synchronized

---

## 10. Support & Debugging

**Test Commands:**
```bash
# 1. Verify all components
python smoke_test.py

# 2. Check Manus connector
python -c "from manus_connector import manus_bp; print('✅ Connector OK')"

# 3. Test BOB directly
python manus_bot.py "Your question here"

# 4. Test API
python manus_api.py  # Visit http://localhost:5000/health
```

**Logs:**
- BOB responses logged to console
- API errors in response JSON
- Debug mode: Set `FLASK_ENV=development`

**Contact:**
- BPFCo.Trust case management: https://evidportal-fvptvdpk.manus.space
- BOB GitHub: https://github.com/DieselHawk/BPFCoBrain

---

**Version:** 1.0  
**Created:** 2026-09-01  
**Status:** Production Ready ✅
