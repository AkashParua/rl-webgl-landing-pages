"""Pipeline CLI.

Stage 1: generate-tasks
  Samples ConstraintSpecs and writes, for each task:
    - spec.json
    - instruction.md   (agent-facing prompt)
    - tests/generated.spec.ts
    - minimal task.toml
"""

import argparse
import json
from pathlib import Path

from .sampler import sample_spec
from .instruction import render_instruction
from .test_generator import generate_playwright_ts

def _kebab(template_id: str, topic: str, seed: int) -> str:
    raw = f"{template_id}-{topic}-{seed}"
    return raw.replace("_", "-").lower()

def _write_task(spec, seed: int, out_dir: Path) -> Path:
    name = _kebab(spec.template_id, spec.topic, seed)
    task_dir = out_dir / name
    task_dir.mkdir(parents=True, exist_ok=True)

    # spec
    (task_dir / "spec.json").write_text(spec.model_dump_json(indent=2))

    # instruction / prompt
    (task_dir / "instruction.md").write_text(render_instruction(spec))

    # Playwright tests
    tests_dir = task_dir / "tests"
    tests_dir.mkdir(exist_ok=True)
    (tests_dir / "generated.spec.ts").write_text(generate_playwright_ts(spec))

    # minimal task.toml
    toml = f"""schema_version = "2.0"

[task]
name = "{name}"
description = "Generated WebGL landing page task ({spec.template_id} / {spec.topic})"

[metadata]
seed = {seed}
template_id = "{spec.template_id}"
topic = "{spec.topic}"

[environment]
cpus = 1
memory_mb = 2048
network_mode = "no-network"

[agent]
timeout_sec = 600

[verifier]
timeout_sec = 180
environment_mode = "separate"
"""
    (task_dir / "task.toml").write_text(toml)

    # placeholder dirs
    (task_dir / "environment").mkdir(exist_ok=True)
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

def main() -> None:
    parser = argparse.ArgumentParser(prog="pipeline")
    sub = parser.add_subparsers(dest="command", required=True)

    p_gen = sub.add_parser("generate-tasks", help="Sample specs and emit prompts + Playwright tests")
    p_gen.add_argument("--count", "-n", type=int, default=1)
    p_gen.add_argument("--seed", type=int, default=42)
    p_gen.add_argument("--out-dir", default="tasks")
    p_gen.set_defaults(func=cmd_generate_tasks)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
