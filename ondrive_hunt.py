"""Read-only OneDrive source for BPFCoBrain using Microsoft Graph API."""

import json
import os
from pathlib import Path
from typing import Dict, Optional
import requests

try:
    import msal
    MSAL_AVAILABLE = True
except ImportError:
    MSAL_AVAILABLE = False


class OneDriveAuth:
    """Shared OAuth for Microsoft Graph OneDrive access."""
    
    AUTHORITY = "https://login.microsoftonline.com/common"
    SCOPES = ["https://graph.microsoft.com/.default"]
    GRAPH_ENDPOINT = "https://graph.microsoft.com/v1.0"
    
    @staticmethod
    def get_credentials(token_file: str = "onedrive_token.json", client_id: str = None) -> str:
        """Load or create durable Microsoft OAuth credentials.
        
        The access token is cached in token_file. Requires:
        - AZURE_CLIENT_ID environment variable or client_id parameter
        - AZURE_CLIENT_SECRET environment variable
        
        Args:
            token_file: Path to cache token
            client_id: Azure app client ID (uses AZURE_CLIENT_ID env var if not provided)
        
        Returns:
            Access token string
            
        Raises:
            RuntimeError: If credentials cannot be obtained
        """
        token_path = Path(token_file).expanduser().resolve()
        
        # Get client ID from parameter or environment
        if not client_id:
            client_id = os.getenv("AZURE_CLIENT_ID")
        
        if not client_id:
            raise RuntimeError(
                "AZURE_CLIENT_ID not set. Set environment variable or pass client_id parameter."
            )
        
        # Try to load cached token
        if token_path.exists():
            try:
                with open(token_path, 'r') as f:
                    data = json.load(f)
                    token = data.get("access_token")
                    if token:
                        # Basic validation - check if token still valid
                        if data.get("expires_in", 0) > 300:  # > 5 minutes left
                            return token
            except (ValueError, OSError, KeyError):
                pass
        
        # Check if MSAL is available for interactive auth
        if not MSAL_AVAILABLE:
            raise RuntimeError(
                "MSAL not installed. Run: pip install msal\n"
                "Or use refresh token: export AZURE_REFRESH_TOKEN=<token>"
            )
        
        # Authenticate interactively with MSAL
        client_secret = os.getenv("AZURE_CLIENT_SECRET")
        tenant = os.getenv("AZURE_TENANT_ID", "common")
        
        app = msal.PublicClientApplication(
            client_id=client_id,
            authority=f"https://login.microsoftonline.com/{tenant}"
        )
        
        try:
            # Try device flow (better for scripts)
            flow = app.initiate_device_flow(scopes=OneDriveAuth.SCOPES)
            if "user_code" not in flow:
                raise RuntimeError("Device flow failed: no user code")
            
            print(f"\n🔐 Microsoft Graph Authentication")
            print(f"─────────────────────────────────")
            print(f"1. Go to: {flow['verification_uri']}")
            print(f"2. Enter code: {flow['user_code']}")
            print(f"3. Waiting for authentication...\n")
            
            result = app.acquire_token_by_device_flow(flow)
            
            if "error" in result:
                raise RuntimeError(f"Auth failed: {result.get('error_description')}")
            
            # Cache token
            token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(token_path, 'w') as f:
                json.dump({
                    "access_token": result.get("access_token"),
                    "expires_in": result.get("expires_in", 3600)
                }, f)
            
            print(f"✅ Authentication successful. Token cached to {token_path}\n")
            return result["access_token"]
            
        except Exception as e:
            raise RuntimeError(f"Cannot authenticate with OneDrive: {e}")


class OneDriveHunter:
    """Read-only OneDrive search and retrieval for BPFCoBrain."""
    
    def __init__(self, token_file: str = "onedrive_token.json", client_id: str = None):
        """Initialize with cached or new credentials.
        
        Args:
            token_file: Path to token cache
            client_id: Azure client ID (uses AZURE_CLIENT_ID env var if not set)
        """
        self.token_file = token_file
        self.client_id = client_id
        self.token = None
        self.headers = {}
        self._authenticate()
    
    def _authenticate(self):
        """Get and cache authentication token."""
        try:
            self.token = OneDriveAuth.get_credentials(self.token_file, self.client_id)
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
        except RuntimeError as e:
            print(f"⚠️  OneDrive authentication failed: {e}")
            self.token = None
    
    def hunt_files(self, keywords: list, max_results: int = 50) -> Dict:
        """Search OneDrive for files matching keywords.
        
        Args:
            keywords: List of search terms
            max_results: Max results per keyword
            
        Returns:
            Dict of {file_id: file_info}
        """
        if not self.token:
            return {}
        
        results = {}
        
        for keyword in keywords:
            try:
                # Use Microsoft Graph search endpoint
                url = f"{OneDriveAuth.GRAPH_ENDPOINT}/me/drive/root/microsoft.graph.itemContainer/children"
                
                # Search using OData filter (filename contains keyword)
                params = {
                    "$filter": f"contains(name, '{keyword}')",
                    "$top": max_results,
                    "$select": "id,name,file,fileSystemInfo,webUrl,size"
                }
                
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
                response.raise_for_status()
                
                items = response.json().get("value", [])
                for item in items:
                    results[item["id"]] = {
                        "id": item["id"],
                        "name": item.get("name", ""),
                        "mimeType": item.get("file", {}).get("mimeType", "application/octet-stream"),
                        "modifiedTime": item.get("fileSystemInfo", {}).get("lastModifiedDateTime", ""),
                        "webViewLink": item.get("webUrl", ""),
                        "size": item.get("size", 0),
                    }
            
            except requests.exceptions.RequestException as e:
                print(f"⚠️  OneDrive search error for '{keyword}': {e}")
            except Exception as e:
                print(f"⚠️  OneDrive search error: {e}")
        
        return results
    
    def read_text(self, file_id: str, mime_type: Optional[str] = None) -> str:
        """Read text content from a OneDrive file.
        
        Supports: .txt, .md, .pdf, .docx, .xlsx
        
        Args:
            file_id: OneDrive file ID
            mime_type: File MIME type (optional)
            
        Returns:
            Text content or error message
        """
        if not self.token:
            return "[OneDrive not authenticated]"
        
        try:
            # Get file content via streaming download
            url = f"{OneDriveAuth.GRAPH_ENDPOINT}/me/drive/items/{file_id}/content"
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            content = response.content
            
            # Handle DOCX (Office Open XML)
            if mime_type and "word" in mime_type.lower():
                try:
                    import zipfile
                    import xml.etree.ElementTree as ET
                    with zipfile.ZipFile(content) as docx:
                        xml_content = docx.read('word/document.xml')
                        root = ET.fromstring(xml_content)
                        namespace = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                        texts = [t.text for t in root.findall('.//w:t', namespace) if t.text]
                        return '\n'.join(texts)
                except Exception as e:
                    return f"[Could not parse DOCX: {e}]"
            
            # Handle XLSX (Excel)
            elif mime_type and "sheet" in mime_type.lower():
                try:
                    import io
                    import openpyxl
                    workbook = openpyxl.load_workbook(io.BytesIO(content))
                    sheet = workbook.active
                    rows = []
                    for row in sheet.iter_rows(values_only=True):
                        rows.append(','.join(str(cell) if cell else '' for cell in row))
                    return '\n'.join(rows)
                except Exception as e:
                    return f"[Could not parse XLSX: {e}]"
            
            # Handle PDF
            elif mime_type and "pdf" in mime_type.lower():
                try:
                    import pypdf
                    reader = pypdf.PdfReader(io.BytesIO(content))
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    return text
                except Exception as e:
                    return f"[Could not parse PDF: {e}]"
            
            # Default: treat as text
            else:
                try:
                    return content.decode('utf-8', errors='replace')
                except Exception:
                    return f"[Binary file, {len(content)} bytes]"
        
        except requests.exceptions.RequestException as e:
            return f"[Error reading OneDrive file: {e}]"
        except Exception as e:
            return f"[Unexpected error: {e}]"


__all__ = ["OneDriveHunter", "OneDriveAuth"]
