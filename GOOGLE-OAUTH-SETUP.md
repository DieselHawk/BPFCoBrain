# Google Drive and Gmail OAuth Setup

BPFCoBrain uses one shared OAuth implementation for Google Drive and Gmail. The integration requests read-only access, stores a refreshable token locally, and reuses that token on future runs. Normal operation therefore does not require repeated browser login.

## One-time setup

1. In Google Cloud Console, create or select a project.
2. Enable the **Gmail API** and **Google Drive API**.
3. Configure the OAuth consent screen. For personal use, an External app in Testing status is sufficient; add the Google account that will authorize the brain as a test user.
4. Create an OAuth client with application type **Desktop app**.
5. Download the client JSON and save it as:

   ```text
   C:\BPFCo\BPFCoBrain\credentials.json
   ```

6. Open PowerShell in the brain folder and run the integration once. A browser window will request read-only Gmail and Drive consent:

   ```powershell
   cd "C:\BPFCo\BPFCoBrain"
   python -m pip install -r requirements.txt
   python main.py
   ```

After successful consent, Google writes `token.json` beside the scripts. Both credential files are excluded by `.gitignore` and must never be committed or uploaded.

## Long-term behavior

The shared `google_auth.py` module loads `token.json` first. If the access token has expired and a refresh token is available, it refreshes silently and saves the updated token. If refresh fails because access was revoked or the token became invalid, the program gives a recovery message: delete only the local `token.json` and run the command again to authorize.

The client secret in `credentials.json` is not printed. The integrations request only:

- `drive.readonly`, for Drive file metadata and text retrieval;
- `gmail.readonly`, for searching and reading message content.

No email is sent, no message is deleted, and no Drive file is modified.

## Recovery

If Google reports `access_denied`, confirm that the account is listed as a test user on the OAuth consent screen. If Google reports an invalid or revoked grant, close the application, delete `token.json`, and run the command again. If the OAuth client was deleted or replaced, download a new Desktop client JSON as `credentials.json`.

If this project is ever distributed to another Windows user, each user must authorize their own account and keep their own `credentials.json` and `token.json`. Do not share either file.

## Scope boundaries

Search results are metadata until the caller explicitly requests content. Drive and Gmail content should be imported into the brain only after applying a narrow keyword, folder, sender, or date filter. This prevents the vault from becoming an uncurated copy of an entire account.
