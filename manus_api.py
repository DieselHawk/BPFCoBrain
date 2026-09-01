"""Manus API - RESTful interface for BOB contextual answerer.

Provides HTTP endpoints for the Manus platform to query BOB.
"""

from flask import Flask, request, jsonify
from pathlib import Path
import os
from manus_bot import BOBManus

app = Flask(__name__)

# Initialize BOB
vault_path = Path(os.getenv("BRAIN_VAULT", Path.cwd() / "Brain"))
bob = BOBManus(
    vault_path=str(vault_path),
    credentials_file=os.getenv("GOOGLE_CREDENTIALS", "credentials.json"),
    token_file=os.getenv("GOOGLE_TOKEN", "token.json"),
    onedrive_token_file=os.getenv("ONEDRIVE_TOKEN", "onedrive_token.json"),
    anthropic_key=os.getenv("ANTHROPIC_API_KEY"),
)


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "BOB Manus Contextual Answerer",
        "vault": str(vault_path),
    }), 200


@app.route("/answer", methods=["POST"])
def answer_query():
    """Query BOB for contextual answers.
    
    Request body:
    {
        "query": "What happened in Cas-125/07/2025?",
        "include_gmail": true,
        "include_ondrive": true,
        "context_depth": 2
    }
    
    Response:
    {
        "query": "...",
        "answer": "...",
        "sources": [...],
        "context_used": {...},
        "model": "...",
        "usage": {...}
    }
    """
    try:
        data = request.get_json()
        query = data.get("query", "").strip()
        
        if not query:
            return jsonify({"error": "Query required"}), 400
        
        result = bob.answer(
            query=query,
            include_gmail=data.get("include_gmail", True),
            include_ondrive=data.get("include_ondrive", True),
            context_depth=data.get("context_depth", 2),
        )
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/answer/batch", methods=["POST"])
def answer_batch():
    """Answer multiple queries in batch.
    
    Request body:
    {
        "queries": ["query1", "query2", ...],
        "include_gmail": true,
        "include_ondrive": true
    }
    """
    try:
        data = request.get_json()
        queries = data.get("queries", [])
        
        if not queries:
            return jsonify({"error": "Queries required"}), 400
        
        results = bob.answer_batch(
            queries=queries,
            include_gmail=data.get("include_gmail", True),
            include_ondrive=data.get("include_ondrive", True),
        )
        
        return jsonify({"results": results}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/brain/search", methods=["GET"])
def brain_search():
    """Search the BPFCoBrain vault.
    
    Query parameters:
    - q: search query
    - depth: context depth (1-3)
    """
    try:
        query = request.args.get("q", "").strip()
        depth = int(request.args.get("depth", 2))
        
        if not query:
            return jsonify({"error": "Search query required"}), 400
        
        result = bob.indexer.query(query, depth=min(depth, 3))
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/sync", methods=["POST"])
def sync_evidence():
    """Trigger a sync of Gmail + Drive + OneDrive context into Evidence.md.
    
    Request body:
    {
        "keywords": ["keyword1", "keyword2", ...]
    }
    """
    try:
        data = request.get_json()
        keywords = data.get("keywords", [])
        
        if not keywords:
            return jsonify({"error": "Keywords required"}), 400
        
        # Import and run the sync
        from main import run_brain
        run_brain(
            vault_path=vault_path,
            credentials_file=os.getenv("GOOGLE_CREDENTIALS", "credentials.json"),
            token_file=os.getenv("GOOGLE_TOKEN", "token.json"),
            onedrive_token_file=os.getenv("ONEDRIVE_TOKEN", "onedrive_token.json"),
            keywords=keywords,
        )
        
        return jsonify({
            "status": "synced",
            "keywords": keywords,
            "evidence_file": str(vault_path / "Evidence.md"),
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    print(f"\n🤖 BOB Manus API Server")
    print(f"   Vault: {vault_path}")
    print(f"   Port: {port}")
    print(f"   Debug: {debug}\n")
    
    app.run(host="0.0.0.0", port=port, debug=debug)
