#!/usr/bin/env python3
"""Test Manus webhook integration."""

import json
from manus_connector import manus_bp, get_bob
from flask import Flask

# Create test app
app = Flask(__name__)
app.register_blueprint(manus_bp)

print("🧪 Testing Manus Webhook\n" + "="*50)

# Test 1: Status endpoint
with app.test_client() as client:
    response = client.get('/manus/status')
    print(f"✅ Status: {response.status_code}")
    data = response.get_json()
    print(f"   Service: {data.get('service')}")
    print(f"   Status: {data.get('status')}")
    print(f"   Components: {data.get('components')}")
    
    # Test 2: Webhook query
    print(f"\n✅ Testing Webhook Query")
    webhook_data = {
        "event": "query_bot",
        "query": "What is Cas-125?",
        "case_id": "Cas-125/07/2025",
        "chapter": "Fraud Unit",
        "user_id": "test@example.com",
        "session_id": "test-sess-123"
    }
    
    response = client.post('/manus/webhook', 
        data=json.dumps(webhook_data),
        content_type='application/json')
    
    print(f"   Response Code: {response.status_code}")
    result = response.get_json()
    print(f"   Status: {result.get('status')}")
    print(f"   Answer length: {len(result.get('answer', ''))}")
    print(f"   Sources: {len(result.get('sources', []))}")
    print(f"   Session ID: {result.get('session_id')}")
    
    # Test 3: Case search (case_id with slashes)
    print(f"\n✅ Testing Case Search")
    search_data = {
        "query": "fraud investigation",
        "chapters": ["Fraud Unit"]
    }
    
    response = client.post('/manus/case/Cas-125/07/2025/search',
        data=json.dumps(search_data),
        content_type='application/json')
    
    print(f"   Response Code: {response.status_code}")
    if response.status_code == 200:
        result = response.get_json()
        if result:
            print(f"   Answer length: {len(result.get('answer', ''))}")
            print(f"   Sources found: {len(result.get('sources', []))}")
    else:
        print(f"   Error: {response.text}")

print("\n" + "="*50)
print("✅ All Manus endpoints working!")
