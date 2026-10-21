"""Spin up page + verifier containers and run Playwright tests for a task."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCKER_DIR = ROOT / "docker"

def _run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    print("+" , " ".join(cmd))
    return subprocess.run(cmd, check=check)

def ensure_images() -> None:
    """Build the shared page and verifier images if they don't exist."""
    _run(["docker", "build", "-t", "rl-page", str(DOCKER_DIR / "page")])
    _run(["docker", "build", "-t", "rl-verifier", str(DOCKER_DIR / "verifier")])

def evaluate_task(task_dir: Path) -> int:
    """Run tests for one task. Returns 0 if reward=1, else 1."""
    task_dir = task_dir.resolve()
    submission = task_dir / "submission"
    tests = task_dir / "tests"

    if not (submission / "index.html").exists():
        print(f"No submission found at {submission / 'index.html'}")
        print("Drop an index.html there first (or use generate-page).")
        return 1

    network = f"rl-net-{task_dir.name}"
    page_name = f"rl-page-{task_dir.name}"
    verifier_name = f"rl-verifier-{task_dir.name}"

    # Clean up any previous run
    subprocess.run(["docker", "rm", "-f", page_name, verifier_name], capture_output=True)
    subprocess.run(["docker", "network", "rm", network], capture_output=True)

    try:
        _run(["docker", "network", "create", network])

        # Page container — serve the submission
        _run([
            "docker", "run", "-d",
            "--name", page_name,
            "--network", network,
            "-v", f"{submission}:/usr/share/nginx/html:ro",
            "rl-page",
        ])

        # Verifier container — run tests
        result = _run([
            "docker", "run", "--rm",
            "--name", verifier_name,
            "--network", network,
            "-v", f"{tests}:/tests:ro",
            "-v", f"{DOCKER_DIR / 'verifier' / 'test.sh'}:/work/test.sh:ro",
            "-e", "BASE_URL=http://page:80",
            "--entrypoint", "bash",
            "rl-verifier",
            "/work/test.sh",
        ], check=False)

        # Try to read reward if the script wrote it (it exits 0 always)
        # For local feedback we just report the playwright exit via the script
        print(f"\nVerifier finished (docker exit {result.returncode})")
        return 0 if result.returncode == 0 else 1

    finally:
        subprocess.run(["docker", "rm", "-f", page_name], capture_output=True)
        subprocess.run(["docker", "network", "rm", network], capture_output=True)

def main(task_path: str) -> None:
    ensure_images()
    code = evaluate_task(Path(task_path))
    sys.exit(code)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m pipeline.evaluate <task-dir>")
        sys.exit(1)
    main(sys.argv[1])
