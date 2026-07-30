from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import base64

class GmailHunter:
    def __init__(self, creds_file, token_file):
        # Load credentials (OAuth flow already done)
        self.service = build("gmail", "v1", credentials=self._load_creds(creds_file, token_file))

    def _load_creds(self, creds_file, token_file):
        # TODO: implement proper OAuth loading
        pass

    def hunt_keywords(self, keywords):
        results = []
        for kw in keywords:
            query = f"subject:{kw} OR body:{kw}"
            messages = self.service.users().messages().list(userId="me", q=query).execute()
            if "messages" in messages:
                for msg in messages["messages"]:
                    results.append(f"Gmail hit: {kw} in {msg['id']}")
        return results
