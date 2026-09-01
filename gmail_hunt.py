"""Read-only Gmail source for BPFCoBrain."""

import base64

from googleapiclient.discovery import build

from google_auth import GoogleAuthError, get_credentials


class GmailHunter:
    def __init__(self, creds_file="credentials.json", token_file="token.json"):
        self.service = build("gmail", "v1", credentials=get_credentials(creds_file, token_file))

    def hunt_keywords(self, keywords, max_results=50):
        """Return message metadata matching any keyword."""
        results = {}
        for keyword in keywords:
            query = f'"{keyword.replace(chr(34), "")}"'
            response = self.service.users().messages().list(
                userId="me", q=query, maxResults=max_results
            ).execute()
            for message in response.get("messages", []):
                results[message["id"]] = {"id": message["id"], "matched_keyword": keyword}
        return results

    def read_message(self, message_id):
        """Return headers and decoded plain-text content for one message."""
        message = self.service.users().messages().get(
            userId="me", id=message_id, format="full"
        ).execute()
        headers = {h["name"].lower(): h["value"] for h in message.get("payload", {}).get("headers", [])}
        parts = [message.get("payload", {})]
        body = []
        while parts:
            part = parts.pop()
            if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
                body.append(base64.urlsafe_b64decode(part["body"]["data"] + "===").decode("utf-8", errors="replace"))
            parts.extend(part.get("parts", []))
        return {
            "id": message_id,
            "thread_id": message.get("threadId"),
            "subject": headers.get("subject", ""),
            "from": headers.get("from", ""),
            "to": headers.get("to", ""),
            "date": headers.get("date", ""),
            "body": "\n\n".join(body),
        }


__all__ = ["GmailHunter", "GoogleAuthError"]
