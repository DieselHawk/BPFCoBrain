"""Verify queue handoff against temporary records; never touch the live queue."""
import ast
import json
import tempfile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import executive_controller as ec


def check_functions():
    dashboard = ast.parse((ROOT / "ceo_dashboard.py").read_text(encoding="utf-8-sig"))
    routes = ast.parse((ROOT / "Dashboard/agent_terminal_routes.py").read_text(encoding="utf-8-sig"))
    main = next(n for n in dashboard.body if isinstance(n, ast.If)
                and isinstance(n.test, ast.Compare) and isinstance(n.test.left, ast.Name)
                and n.test.left.id == "__name__")
    lines = [ast.unparse(node) for node in main.body]
    bound = next(i for i, line in enumerate(lines) if "make_server(" in line)
    started = next(i for i, line in enumerate(lines) if "Thread(" in line and ".start()" in line)
    assert bound < started, "Worker may start before dashboard owns its port"
    assert any(isinstance(n, ast.FunctionDef) and n.name == "run_queued_specialists"
               for n in dashboard.body)
    assert any(isinstance(n, ast.FunctionDef) and n.name == "run_next_specialist"
               for n in routes.body)
    print("Startup: port bound before automatic worker; manual endpoint present")


def check_dispatch():
    with tempfile.TemporaryDirectory(prefix="fred-queue-") as temp:
        root = Path(temp)
        queue_dir = root / "Brain" / "Executive"
        queue_dir.mkdir(parents=True)
        task_id = "test-internal-task"
        queue_file = queue_dir / "queue.json"
        queue_file.write_text(json.dumps([{"task_id": task_id,
                                           "agent": "Kai_Legal"}]), encoding="utf-8")
        worker = root / "fake_worker.py"
        worker.write_text("import sys\nfrom pathlib import Path\n"
                          "Path('completed.txt').write_text(sys.argv[1])\n",
                          encoding="utf-8")
        old = ec.ROOT, ec.EXECUTIVE_DIR, ec.QUEUE_FILE, ec.WORKERS
        try:
            ec.ROOT = root
            ec.EXECUTIVE_DIR = queue_dir
            ec.QUEUE_FILE = queue_file
            ec.WORKERS = {"Kai_Legal": worker}
            controller = ec.CEOController()
            first = controller.dispatch_one()
            assert first["status"] == "dispatched" and first["task_id"] == task_id
            assert (root / "completed.txt").read_text() == task_id
            assert json.loads(queue_file.read_text()) == []
            assert controller.dispatch_one()["status"] == "idle"
        finally:
            ec.ROOT, ec.EXECUTIVE_DIR, ec.QUEUE_FILE, ec.WORKERS = old
    print("Dispatch: fake specialist completed once; queue advanced; next call idle")


if __name__ == "__main__":
    check_functions()
    check_dispatch()
    print("QUEUE CHECK PASSED (temporary records only; no live tasks run)")
