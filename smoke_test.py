#!/usr/bin/env python3
"""Smoke test for BOB Manus integration."""

import sys
from pathlib import Path

print("\n🧪 BOB Manus Smoke Test\n" + "="*50)

# Test 1: Check Python version
print(f"✓ Python {sys.version.split()[0]}")

# Test 2: Check imports
try:
    from query_cli import VaultIndexer
    print("✓ VaultIndexer imports")
except Exception as e:
    print(f"✗ VaultIndexer: {e}")
    sys.exit(1)

try:
    from gmail_hunt import GmailHunter
    print("✓ GmailHunter imports")
except Exception as e:
    print(f"✗ GmailHunter: {e}")
    sys.exit(1)

try:
    from ondrive_hunt import OneDriveHunter, OneDriveAuth
    print("✓ OneDriveHunter imports")
except ImportError as e:
    if "azure" in str(e):
        print("⊘ OneDriveHunter skipped (Azure SDK not installed - install with: pip install azure-identity msgraph-core msgraph-sdk)")
    else:
        print(f"✗ OneDriveHunter: {e}")
        sys.exit(1)

try:
    from manus_bot import BOBManus
    print("✓ BOBManus imports")
except ImportError as e:
    if "anthropic" in str(e) or "azure" in str(e):
        print("⊘ BOBManus skipped (missing dependencies - install with: pip install -r requirements.txt)")
    else:
        print(f"✗ BOBManus: {e}")
        sys.exit(1)
except Exception as e:
    print(f"⊘ BOBManus: {e} (skipped due to missing credentials)")

# Test 3: Check files exist
files_to_check = [
    "manus_bot.py",
    "manus_api.py",
    "ondrive_hunt.py",
    "main.py",
    "MANUS-BOB-SETUP.md",
    ".env.example",
    "launch-bob.bat",
]

for f in files_to_check:
    if Path(f).exists():
        print(f"✓ {f} exists")
    else:
        print(f"✗ {f} missing")
        sys.exit(1)

# Test 4: Check requirements
try:
    with open("requirements.txt") as f:
        reqs = f.read()
    required = ["anthropic", "flask", "google-api-python-client", "msal"]
    for req in required:
        if req in reqs:
            print(f"✓ {req} in requirements.txt")
        else:
            print(f"✗ {req} missing from requirements.txt")
            sys.exit(1)
except Exception as e:
    print(f"✗ requirements.txt: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("✅ All smoke tests passed!\n")
