import argparse, base64, getpass, hashlib, hmac, json, os, secrets, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "Brain" / "Security" / "security_state.json"
VERSION = 1
ITERATIONS = 600000

def save(obj, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def hash_password(password, salt, iterations=ITERATIONS):
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, iterations, dklen=32
    )

def token_binding(secret, brain_id):
    return hmac.new(secret, brain_id.encode("utf-8"), hashlib.sha256).hexdigest()

def init(usb):
    usb = Path(usb)
    usb.mkdir(parents=True, exist_ok=True)

    brain_id = secrets.token_hex(16)
    token_id = secrets.token_hex(12)
    secret = secrets.token_bytes(32)

    p1 = getpass.getpass("Create BPFCo recovery password: ")
    p2 = getpass.getpass("Repeat recovery password: ")
    if not p1 or p1 != p2:
        raise SystemExit("Recovery password mismatch.")

    salt = secrets.token_bytes(16)
    pwd_hash = hash_password(p1, salt)

    save({
        "version": VERSION,
        "brain_id": brain_id,
        "token_id": token_id,
        "token_binding": token_binding(secret, brain_id),
        "recovery": {
            "salt": base64.b64encode(salt).decode(),
            "iterations": ITERATIONS,
            "hash": base64.b64encode(pwd_hash).decode()
        },
        "normal_approval": "USB_REQUIRED",
        "recovery_mode": "REKEY_ONLY",
        "created_utc": time.time()
    }, STATE)

    save({
        "version": VERSION,
        "brain_id": brain_id,
        "token_id": token_id,
        "secret": base64.b64encode(secret).decode()
    }, usb / "BPFCo-Key" / "token.json")

    (usb / "BPFCo-Key" / "README.txt").write_text(
        "BPFCo Brain approval token. Do not copy, rename, or edit this directory.\n",
        encoding="utf-8"
    )

    print("BPFCo Brain security identity created.")
    print("USB token:", usb / "BPFCo-Key")
    print("Normal approvals: USB REQUIRED")
    print("Recovery mode: password -> re-key ONLY")

def recover(usb):
    if not STATE.exists():
        raise SystemExit("No BPFCo security state exists.")
    state = load(STATE)

    p = getpass.getpass("BPFCo recovery password: ")
    r = state["recovery"]
    salt = base64.b64decode(r["salt"])
    test = hash_password(p, salt, int(r["iterations"]))

    if not hmac.compare_digest(test, base64.b64decode(r["hash"])):
        raise SystemExit("RECOVERY REJECTED.")

    usb = Path(usb)
    usb.mkdir(parents=True, exist_ok=True)

    old = state["token_id"]
    token_id = secrets.token_hex(12)
    secret = secrets.token_bytes(32)

    state["token_id"] = token_id
    state["token_binding"] = token_binding(secret, state["brain_id"])
    state["rotated_from"] = old
    state["rotated_utc"] = time.time()

    save(state, STATE)
    save({
        "version": VERSION,
        "brain_id": state["brain_id"],
        "token_id": token_id,
        "secret": base64.b64encode(secret).decode()
    }, usb / "BPFCo-Key" / "token.json")

    print("RECOVERY ACCEPTED.")
    print("Old token revoked by state rotation.")
    print("New BPFCo token:", usb / "BPFCo-Key")
    print("Normal approval requirement remains: USB REQUIRED")

def verify(usb):
    state = load(STATE)
    token = load(Path(usb) / "BPFCo-Key" / "token.json")
    secret = base64.b64decode(token["secret"])

    ok = (
        token["version"] == state["version"] and
        token["brain_id"] == state["brain_id"] and
        token["token_id"] == state["token_id"] and
        hmac.compare_digest(
            token_binding(secret, token["brain_id"]),
            state["token_binding"]
        )
    )
    print("BPFCo USB KEY:", "VALID" if ok else "REJECTED")
    return 0 if ok else 1

ap = argparse.ArgumentParser()
ap.add_argument("command", choices=["init","recover","verify"])
ap.add_argument("--usb", required=True)
a = ap.parse_args()

if a.command == "init":
    init(a.usb)
elif a.command == "recover":
    recover(a.usb)
else:
    raise SystemExit(verify(a.usb))
