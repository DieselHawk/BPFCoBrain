"""Read-only Google Drive source for BPFCoBrain."""

from googleapiclient.discovery import build

from google_auth import GoogleAuthError, get_credentials


class DriveHunter:
    def __init__(self, creds_file="credentials.json", token_file="token.json"):
        self.service = build("drive", "v3", credentials=get_credentials(creds_file, token_file))

    def hunt_files(self, keywords, max_results=50):
        """Return Drive metadata matching any keyword in the file name."""
        results = []
        for keyword in keywords:
            safe_keyword = keyword.replace("'", "\\'")
            query = f"name contains '{safe_keyword}' and trashed = false"
            response = self.service.files().list(
                q=query,
                pageSize=min(max_results, 100),
                orderBy="modifiedTime desc",
                fields="files(id,name,mimeType,modifiedTime,webViewLink,size)",
            ).execute()
            for item in response.get("files", []):
                item["matched_keyword"] = keyword
                results.append(item)
        return {item["id"]: item for item in results}

    def read_text(self, file_id, mime_type):
        """Read Google Docs text or downloadable plain text when supported."""
        if mime_type == "application/vnd.google-apps.document":
            response = self.service.files().export(
                fileId=file_id, mimeType="text/plain"
            ).execute()
            return response.decode("utf-8", errors="replace") if isinstance(response, bytes) else response
        response = self.service.files().get(fileId=file_id, alt="media").execute()
        return response.decode("utf-8", errors="replace") if isinstance(response, bytes) else str(response)


__all__ = ["DriveHunter", "GoogleAuthError"]
