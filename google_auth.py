"""Shared OAuth authentication for the BPFCoBrain Google integrations."""

from pathlib import Path
from typing import Iterable

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


DEFAULT_SCOPES = (
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/gmail.readonly",
)


class GoogleAuthError(RuntimeError):
    """Raised when Google OAuth cannot be completed or refreshed."""


def get_credentials(
    credentials_file: str = "credentials.json",
    token_file: str = "token.json",
    scopes: Iterable[str] = DEFAULT_SCOPES,
) -> Credentials:
    """Load, refresh, or interactively create durable Google OAuth credentials.

    The refresh token is persisted in ``token_file`` so normal future runs do not
    require a browser login. The OAuth client secret is never written to output.
    """
    client_path = Path(credentials_file).expanduser().resolve()
    token_path = Path(token_file).expanduser().resolve()
    requested_scopes = list(scopes)
    credentials = None

    if token_path.exists():
        try:
            credentials = Credentials.from_authorized_user_file(str(token_path), requested_scopes)
        except (ValueError, OSError) as exc:
            raise GoogleAuthError(
                f"Cannot read {token_path}. Delete that token file and authenticate again."
            ) from exc

    if credentials and credentials.expired and credentials.refresh_token:
        try:
            credentials.refresh(Request())
        except Exception as exc:
            raise GoogleAuthError(
                "Google refresh failed. Delete token.json and run again to re-authorize."
            ) from exc

    if not credentials or not credentials.valid:
        if not client_path.exists():
            raise GoogleAuthError(
                f"Missing {client_path}. In Google Cloud Console create a Desktop OAuth client, "
                "download the JSON, and save it as credentials.json beside the brain scripts."
            )
        try:
            flow = InstalledAppFlow.from_client_secrets_file(str(client_path), requested_scopes)
            credentials = flow.run_local_server(port=0, access_type="offline", prompt="consent")
        except Exception as exc:
            raise GoogleAuthError(
                "Google OAuth could not complete. Check that the OAuth client is a Desktop app "
                "and that Gmail/Drive APIs are enabled."
            ) from exc

    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(credentials.to_json(), encoding="utf-8")
    return credentials
