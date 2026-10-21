"""Pipeline CLI.

generate-tasks  – sample specs, write Harbor bundles
generate-page   – print prompt (manual) or call LLM to write index.html
evaluate        – run Playwright tests against a submission
"""

import argparse
import json
import shutil
from pathlib import Path

from .sampler import sample_spec
from .instruction import render_instruction
from .test_generator import generate_playwright_ts
from .evaluate import ensure_images, evaluate_task
from .generate_page import generate_manual, generate_llm

ROOT = Path(__file__).resolve().parent.parent
TEST_SH_SRC = ROOT / "docker" / "verifier" / "test.sh"

def _kebab(template_id: str, topic: str, seed: int) -> str:
    raw = f"{template_id}-{topic}-{seed}"
    return raw.replace("_", "-").lower()

def _resolve_task(task_dir: str) -> Path:
    p = Path(task_dir)
    if p.exists():
        return p
    alt = Path("tasks") / task_dir
    if alt.exists():
        return alt
    raise SystemExit(f"Task not found: {task_dir}")

def _write_task(spec, seed: int, out_dir: Path) -> Path:
    name = _kebab(spec.template_id, spec.topic, seed)
    task_dir = out_dir / name
    task_dir.mkdir(parents=True, exist_ok=True)

    (task_dir / "spec.json").write_text(spec.model_dump_json(indent=2))
    (task_dir / "instruction.md").write_text(render_instruction(spec))

    tests_dir = task_dir / "tests"
    tests_dir.mkdir(exist_ok=True)
    (tests_dir / "generated.spec.ts").write_text(generate_playwright_ts(spec))
    if TEST_SH_SRC.exists():
        shutil.copy(TEST_SH_SRC, tests_dir / "test.sh")
        (tests_dir / "test.sh").chmod(0o755)

    env_dir = task_dir / "environment"
    env_dir.mkdir(exist_ok=True)
    (env_dir / "Dockerfile").write_text(
        "# Shared image is used at runtime (rl-page).\n"
        "# This file exists only to satisfy the Harbor layout.\n"
        "FROM nginx:alpine\n"
        "COPY submission /usr/share/nginx/html\n"
    )
    (env_dir / "README.md").write_text(
        "This task uses the shared `rl-page` image.\n"
        "The harness mounts `submission/` over the web root.\n"
        "No per-task image build is required.\n"
    )

    toml = f"""schema_version = "2.0"

[task]
name = "{name}"
description = "Generated WebGL landing page task ({spec.template_id} / {spec.topic})"

[metadata]
seed = {seed}
template_id = "{spec.template_id}"
topic = "{spec.topic}"

do_not_modify = [
  "tests/",
  "task.toml",
  "spec.json",
  "environment/",
]

[environment]
docker_image = "rl-page"
cpus = 1
memory_mb = 2048
network_mode = "no-network"

[agent]
timeout_sec = 600

[verifier]
timeout_sec = 180
environment_mode = "separate"

[verifier.environment]
docker_image = "rl-verifier"
cpus = 1
memory_mb = 2048
network_mode = "no-network"
"""
    (task_dir / "task.toml").write_text(toml)

    (task_dir / "solution").mkdir(exist_ok=True)
    (task_dir / "submission").mkdir(exist_ok=True)

    return task_dir

def cmd_generate_tasks(args: argparse.Namespace) -> None:
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    created = []
    for i in range(args.count):
        seed = args.seed + i
        spec = sample_spec(seed)
        task_dir = _write_task(spec, seed, out_dir)
        created.append(task_dir.name)
        print(f"created {task_dir}")

    index = out_dir / "index.json"
    index.write_text(json.dumps({"count": len(created), "tasks": created}, indent=2))
    print(f"\nWrote {len(created)} tasks to {out_dir}")

def cmd_generate_page(args: argparse.Namespace) -> None:
    task_dir = _resolve_task(args.task_dir)
    mode = args.mode

    if mode == "manual":
        print(generate_manual(task_dir))
        print("\n---\nCopy the above into Claude (or any chat).")
        print(f"Save the resulting HTML to: {task_dir / 'submission' / 'index.html'}")
    elif mode == "llm":
        out = generate_llm(task_dir)
        print(f"Wrote {out}")
    else:
        raise SystemExit(f"Unknown mode: {mode}")

def cmd_evaluate(args: argparse.Namespace) -> None:
    ensure_images()
    task_dir = _resolve_task(args.task_dir)
    code = evaluate_task(task_dir)
    raise SystemExit(code)

def main() -> None:
    parser = argparse.ArgumentParser(prog="pipeline")
    sub = parser.add_subparsers(dest="command", required=True)

    p_gen = sub.add_parser("generate-tasks", help="Sample specs and emit Harbor bundles")
    p_gen.add_argument("--count", "-n", type=int, default=1)
    p_gen.add_argument("--seed", type=int, default=42)
    p_gen.add_argument("--out-dir", default="tasks")
    p_gen.set_defaults(func=cmd_generate_tasks)

    p_page = sub.add_parser("generate-page", help="Produce index.html via LLM or print prompt")
    p_page.add_argument("task_dir", help="Task directory or name under tasks/")
    p_page.add_argument("--mode", choices=["manual", "llm"], default="manual")
    p_page.set_defaults(func=cmd_generate_page)

    p_eval = sub.add_parser("evaluate", help="Run Playwright tests against a submission")
    p_eval.add_argument("task_dir", help="Task directory or name under tasks/")
    p_eval.set_defaults(func=cmd_evaluate)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
