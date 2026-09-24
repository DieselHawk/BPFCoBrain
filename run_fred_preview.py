"""Start the isolated Fred preview on loopback port 5002."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from boot_network import configure_environment

print("Fred preview network mode:", configure_environment(), flush=True)
from ceo_dashboard import app

app.run(host="127.0.0.1", port=5002, debug=False, use_reloader=False)
