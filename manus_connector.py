"""Manus Webhook Connector - Integrates BOB with Manus platform.

Handles incoming requests from Manus and formats responses for the UI.
"""

from flask import Blueprint, request, jsonify
from manus_bot import BOBManus
import os
from pathlib import Path

# Create blueprint for Manus endpoints
manus_bp = Blueprint('manus', __name__, url_prefix='/manus')

# Initialize BOB once
_bob_instance = None

def get_bob():
    """Lazy-load BOB instance."""
    global _bob_instance
    if _bob_instance is None:
        vault_path = Path(os.getenv("BRAIN_VAULT", Path.cwd() / "Brain"))
        _bob_instance = BOBManus(
            vault_path=str(vault_path),
            credentials_file=os.getenv("GOOGLE_CREDENTIALS", "credentials.json"),
            token_file=os.getenv("GOOGLE_TOKEN", "token.json"),
            onedrive_token_file=os.getenv("ONEDRIVE_TOKEN", "onedrive_token.json"),
            onedrive_client_id=os.getenv("AZURE_CLIENT_ID"),
        )
    return _bob_instance


@manus_bp.route('/webhook', methods=['POST'])
def manus_webhook():
    """Webhook endpoint for Manus platform.
    
    Manus sends query with case context and expects formatted response.
    
    Request format from Manus:
    {
        "event": "query_bot",
        "query": "What is the status?",
        "case_id": "Cas-125/07/2025",
        "chapter": "Fraud Unit",
        "user_id": "investigator@case.gov",
        "session_id": "uuid"
    }
    
    Response format for Manus:
    {
        "status": "success",
        "answer": "...",
        "sources": [...],
        "confidence": 0.95,
        "action_items": [...],
        "session_id": "uuid"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"status": "error", "message": "No data"}), 400
        
        event = data.get("event")
        query = data.get("query", "").strip()
        case_id = data.get("case_id")
        chapter = data.get("chapter")
        session_id = data.get("session_id")
        
        if not query:
            return jsonify({
                "status": "error",
                "message": "Query required",
                "session_id": session_id
            }), 400
        
        # Add case context to query
        full_query = f"[Case: {case_id}, Chapter: {chapter}] {query}"
        
        # Get BOB response
        bob = get_bob()
        result = bob.answer(
            query=full_query,
            include_gmail=True,
            include_ondrive=True,
            context_depth=2
        )
        
        if result.get("errors"):
            # BOB had errors but still answered
            return jsonify({
                "status": "partial",
                "answer": result.get("answer", "No answer available"),
                "sources": result.get("sources", []),
                "warnings": result.get("errors", []),
                "confidence": 0.7,
                "session_id": session_id,
                "context_used": result.get("context_used", {})
            }), 200
        
        # Parse answer to extract action items
        action_items = _extract_action_items(result.get("answer", ""))
        
        return jsonify({
            "status": "success",
            "answer": result.get("answer", ""),
            "sources": result.get("sources", []),
            "confidence": 0.95,
            "action_items": action_items,
            "context_used": result.get("context_used", {}),
            "session_id": session_id,
            "usage": result.get("usage", {})
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "session_id": data.get("session_id") if data else None
        }), 500


@manus_bp.route('/case/<path:case_id>/search', methods=['POST'])
def case_search(case_id):
    """Search within a specific case.
    
    Request:
    {
        "query": "fraud evidence",
        "chapters": ["Fraud Unit", "Banks"]
    }
    """
    try:
        data = request.get_json()
        query = data.get("query", "").strip()
        chapters = data.get("chapters", [])
        
        if not query:
            return jsonify({"error": "Query required"}), 400
        
        # Enhance query with chapter context
        if chapters:
            chapter_str = ", ".join(chapters)
            query = f"[Case: {case_id}, Chapters: {chapter_str}] {query}"
        else:
            query = f"[Case: {case_id}] {query}"
        
        bob = get_bob()
        result = bob.answer(query=query, context_depth=3)
        
        return jsonify({
            "case_id": case_id,
            "query": data.get("query"),
            "answer": result.get("answer", ""),
            "sources": result.get("sources", []),
            "context_used": result.get("context_used", {}),
            "usage": result.get("usage", {})
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manus_bp.route('/case/<path:case_id>/evidence', methods=['POST'])
def case_evidence(case_id):
    """Search evidence specifically.
    
    Request:
    {
        "query": "What evidence supports fraud?",
        "evidence_type": "financial",
        "min_confidence": 0.8
    }
    """
    try:
        data = request.get_json()
        query = data.get("query", "").strip()
        evidence_type = data.get("evidence_type")
        
        if not query:
            return jsonify({"error": "Query required"}), 400
        
        # Enhance query for evidence
        if evidence_type:
            query = f"[Case: {case_id}, Evidence Type: {evidence_type}] {query}"
        else:
            query = f"[Case: {case_id}] {query}"
        
        bob = get_bob()
        result = bob.answer(query=query, context_depth=3)
        
        # Filter sources by confidence
        min_conf = data.get("min_confidence", 0.7)
        confidence = 0.95 if result.get("answer") else 0.5
        
        if confidence >= min_conf:
            return jsonify({
                "case_id": case_id,
                "evidence_found": True,
                "answer": result.get("answer", ""),
                "sources": result.get("sources", []),
                "confidence": confidence,
                "context_used": result.get("context_used", {})
            }), 200
        else:
            return jsonify({
                "case_id": case_id,
                "evidence_found": False,
                "message": "Insufficient evidence in sources",
                "confidence": confidence
            }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@manus_bp.route('/status', methods=['GET'])
def status():
    """Check BOB status for Manus."""
    bob = get_bob()
    return jsonify({
        "service": "BOB Manus Connector",
        "status": "ready" if bob.is_ready() else "degraded",
        "components": {
            "vault": bool(bob.indexer),
            "claude": bool(bob.client),
            "gmail": bool(bob.gmail),
            "ondrive": bool(bob.ondrive)
        },
        "errors": bob.errors if not bob.is_ready() else []
    }), 200


def _extract_action_items(answer_text: str) -> list:
    """Extract action items from answer using simple heuristics."""
    items = []
    lines = answer_text.split('\n')
    
    for line in lines:
        line = line.strip()
        # Look for common action indicators
        if any(prefix in line.lower() for prefix in ['action:', 'need', 'must', 'should', 'recommend']):
            items.append(line)
    
    return items[:3]  # Return top 3 action items


__all__ = ['manus_bp', 'get_bob']
