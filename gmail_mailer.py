"""Outbound Gmail mailer for BPFCoBrain.

Drafts messages locally. Sending is an explicit action.
"""

import base64
from email.message import EmailMessage
from pathlib import Path

from googleapiclient.discovery import build

from google_auth import get_credentials


class GmailMailer:
    def __init__(self, creds_file="credentials.json", token_file="token.json"):
        self.service = build(
            "gmail",
            "v1",
            credentials=get_credentials(creds_file, token_file),
        )

    def create_message(self, to, subject, body):
        message = EmailMessage()
        message["To"] = to
        message["Subject"] = subject
        message.set_content(body)

        encoded = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

        return {
            "raw": encoded,
            "to": to,
            "subject": subject,
            "body": body,
        }

    def send_message(self, to, subject, body):
        message = self.create_message(to, subject, body)

        return self.service.users().messages().send(
            userId="me",
            body={"raw": message["raw"]},
        ).execute()


__all__ = ["GmailMailer"]
