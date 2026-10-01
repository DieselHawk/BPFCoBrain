"""Live OneDrive/Gmail intake with mandatory human approval gate.

This module bridges online data sources (OneDrive, Gmail) into the local
evidence system. All fetches are:
- Opt-in only (not automatic)
- Gated by human approval
- Bounded in scope and cached locally
- Attributed to source and timestamp
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional

# Local imports
try:
    from ondrive_hunt import OneDriveAuth
    ONDRIVE_AVAILABLE = True
except ImportError:
    ONDRIVE_AVAILABLE = False

try:
    from online_gate import OnlineGate
    ONLINE_GATE_AVAILABLE = True
except ImportError:
    ONLINE_GATE_AVAILABLE = False

from approval_gate import request, is_approved


ROOT = Path(__file__).resolve().parent
CACHE_DIR = ROOT / "Brain" / "cache" / "online_requests"
FETCH_LOG = CACHE_DIR / "fetch_log.json"


class OnlineRequestsCoordinator:
    """Unified interface for live data intake with approval gate."""

    def __init__(self):
        self.cache_dir = CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.fetch_log = self._load_fetch_log()

    def _load_fetch_log(self) -> Dict:
        """Load the fetch history log."""
        if FETCH_LOG.exists():
            try:
                return json.loads(FETCH_LOG.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                return {}
        return {}

    def _save_fetch_log(self):
        """Persist fetch history."""
        FETCH_LOG.write_text(json.dumps(self.fetch_log, indent=2), encoding="utf-8")

    def request_ondrive_fetch(self, search_terms: str, agent: str = "Fred") -> Dict:
        """Queue OneDrive search for human approval.
        
        Args:
            search_terms: Space-separated keywords to search for
            agent: Requesting agent name
            
        Returns:
            Approval record with approval_id
        """
        if not ONDRIVE_AVAILABLE:
            return {
                "status": "unavailable",
                "error": "OneDrive module not installed",
            }

        record = request(
            action="ondrive.fetch",
            agent=agent,
            payload={
                "search_terms": search_terms,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

        print(f"\n[OnlineRequests] OneDrive fetch queued for approval")
        print(f"  Approval ID: {record['approval_id']}")
        print(f"  Search: {search_terms}")
        print(f"  Status: PENDING HUMAN APPROVAL")

        return record

    def request_gmail_fetch(self, search_query: str, agent: str = "Fred") -> Dict:
        """Queue Gmail search for human approval.
        
        Args:
            search_query: Gmail search query (e.g. "from:boss subject:urgent")
            agent: Requesting agent name
            
        Returns:
            Approval record with approval_id
        """
        record = request(
            action="gmail.fetch",
            agent=agent,
            payload={
                "query": search_query,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

        print(f"\n[OnlineRequests] Gmail fetch queued for approval")
        print(f"  Approval ID: {record['approval_id']}")
        print(f"  Query: {search_query}")
        print(f"  Status: PENDING HUMAN APPROVAL")

        return record

    def execute_approved_ondrive_fetch(self, approval_id: str) -> Optional[List[Dict]]:
        """Execute OneDrive fetch after human approval.
        
        Args:
            approval_id: Must be in Approved directory
            
        Returns:
            List of documents with paths, excerpts and metadata, or None
        """
        if not is_approved(approval_id):
            print(f"[OnlineRequests] OneDrive fetch BLOCKED: approval {approval_id} not approved")
            return None

        if not ONDRIVE_AVAILABLE:
            print(f"[OnlineRequests] OneDrive module unavailable")
            return None

        approval_file = (
            ROOT / "Brain" / "Executive" / "Approvals" / "Approved" / f"{approval_id}.json"
        )

        try:
            record = json.loads(approval_file.read_text(encoding="utf-8"))
            payload = record["payload"]
            search_terms = payload.get("search_terms", "")

            print(f"\n[OnlineRequests] Executing approved OneDrive fetch...")
            print(f"  Approval ID: {approval_id}")
            print(f"  Search terms: {search_terms}")

            # Call OneDriveAuth to perform actual fetch
            # This is a placeholder—full integration depends on Azure credentials
            documents = self._fetch_ondrive_documents(search_terms)

            # Log the fetch
            self.fetch_log[approval_id] = {
                "action": "ondrive.fetch",
                "status": "completed",
                "search_terms": search_terms,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "document_count": len(documents),
            }
            self._save_fetch_log()

            print(f"  Retrieved {len(documents)} documents")
            return documents

        except Exception as exc:
            print(f"[OnlineRequests] OneDrive fetch failed: {exc}")
            return None

    def execute_approved_gmail_fetch(self, approval_id: str) -> Optional[List[Dict]]:
        """Execute Gmail fetch after human approval.
        
        Args:
            approval_id: Must be in Approved directory
            
        Returns:
            List of email messages with subject, from, excerpt, and metadata
        """
        if not is_approved(approval_id):
            print(f"[OnlineRequests] Gmail fetch BLOCKED: approval {approval_id} not approved")
            return None

        approval_file = (
            ROOT / "Brain" / "Executive" / "Approvals" / "Approved" / f"{approval_id}.json"
        )

        try:
            record = json.loads(approval_file.read_text(encoding="utf-8"))
            payload = record["payload"]
            query = payload.get("query", "")

            print(f"\n[OnlineRequests] Executing approved Gmail fetch...")
            print(f"  Approval ID: {approval_id}")
            print(f"  Query: {query}")

            # Placeholder for Gmail integration
            # Full implementation requires google-api-python-client credentials
            messages = self._fetch_gmail_messages(query)

            # Log the fetch
            self.fetch_log[approval_id] = {
                "action": "gmail.fetch",
                "status": "completed",
                "query": query,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message_count": len(messages),
            }
            self._save_fetch_log()

            print(f"  Retrieved {len(messages)} messages")
            return messages

        except Exception as exc:
            print(f"[OnlineRequests] Gmail fetch failed: {exc}")
            return None

    def _fetch_ondrive_documents(self, search_terms: str) -> List[Dict]:
        """Fetch documents from OneDrive (placeholder).
        
        Returns bounded list of matching documents with:
        - path, filename, size
        - excerpt (first 500 chars)
        - modified_time, source attribution
        """
        # TODO: Implement actual OneDrive integration with ondrive_hunt.OneDriveAuth
        # For now, return empty list—credentials must be configured first
        return []

    def _fetch_gmail_messages(self, query: str) -> List[Dict]:
        """Fetch messages from Gmail (placeholder).
        
        Returns bounded list of matching emails with:
        - message_id, subject, from, to
        - snippet (250 chars)
        - timestamp, source attribution
        """
        # TODO: Implement actual Gmail integration with google-api-python-client
        # Credentials must be stored in Brain/Executive/secrets/ (Git-ignored)
        return []

    def needs_online(self, objective: str) -> bool:
        """Detect if objective requires online data (heuristic)."""
        if not ONLINE_GATE_AVAILABLE:
            return False

        gate = OnlineGate()
        return gate.needs_online(objective)

    def status(self) -> Dict:
        """Report availability and status of online request handlers."""
        return {
            "ondrive_available": ONDRIVE_AVAILABLE,
            "gmail_available": True,
            "online_gate_available": ONLINE_GATE_AVAILABLE,
            "approval_gate": True,
            "cache_dir": str(self.cache_dir),
            "fetch_log_entries": len(self.fetch_log),
            "offline_first": True,
            "external_execution": "BLOCKED_UNTIL_APPROVED",
        }


# Singleton instance
_coordinator = None


def coordinator() -> OnlineRequestsCoordinator:
    """Get or create the shared coordinator."""
    global _coordinator
    if _coordinator is None:
        _coordinator = OnlineRequestsCoordinator()
    return _coordinator


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Online requests coordinator")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("status", help="Show online requests status")

    ondrive = subparsers.add_parser("ondrive", help="OneDrive operations")
    ondrive.add_argument("operation", choices=["request", "execute"])
    ondrive.add_argument("--approval-id", help="Approval ID for execute")
    ondrive.add_argument("--search", help="Search terms for request")
    ondrive.add_argument("--agent", default="Fred")

    gmail = subparsers.add_parser("gmail", help="Gmail operations")
    gmail.add_argument("operation", choices=["request", "execute"])
    gmail.add_argument("--approval-id", help="Approval ID for execute")
    gmail.add_argument("--query", help="Gmail search query for request")
    gmail.add_argument("--agent", default="Fred")

    args = parser.parse_args()
    coord = coordinator()

    if args.command == "status":
        print(json.dumps(coord.status(), indent=2))

    elif args.command == "ondrive":
        if args.operation == "request":
            result = coord.request_ondrive_fetch(args.search or "", args.agent)
            print(json.dumps(result, indent=2))
        elif args.operation == "execute":
            result = coord.execute_approved_ondrive_fetch(args.approval_id or "")
            if result:
                print(f"Retrieved {len(result)} documents")
                for doc in result[:3]:
                    print(f"  - {doc}")

    elif args.command == "gmail":
        if args.operation == "request":
            result = coord.request_gmail_fetch(args.query or "", args.agent)
            print(json.dumps(result, indent=2))
        elif args.operation == "execute":
            result = coord.execute_approved_gmail_fetch(args.approval_id or "")
            if result:
                print(f"Retrieved {len(result)} messages")
                for msg in result[:3]:
                    print(f"  - {msg}")
