#!/bin/bash
# Harbor verifier entrypoint.
# - Fail-safe 0 written first
# - Runs Playwright
# - Emits CTRF JSON
# - Writes final 0/1 reward

set -u
mkdir -p /logs/verifier /tmp/pw

# Fail-safe before anything else
echo 0 > /logs/verifier/reward.txt

cd /work
export PLAYWRIGHT_JSON_OUTPUT_NAME=/tmp/pw/results.json

npx playwright test \
  --config=/work/playwright.config.ts \
  --reporter=json \
  --reporter=line \
  > /tmp/pw/stdout.txt 2>&1 || true

# Convert Playwright JSON → minimal CTRF
python3 - << 'PY'
import json, time, os
from pathlib import Path

pw_path = Path("/tmp/pw/results.json")
reward_path = Path("/logs/verifier/reward.txt")
ctrf_path = Path("/logs/verifier/ctrf.json")

passed = failed = 0
tests_out = []

if pw_path.exists():
    try:
        data = json.loads(pw_path.read_text())
        for suite in data.get("suites", []):
            for spec in suite.get("specs", []):
                for test in spec.get("tests", []):
                    status = "passed"
                    for r in test.get("results", []):
                        if r.get("status") != "passed":
                            status = "failed"
                    if status == "passed":
                        passed += 1
                    else:
                        failed += 1
                    tests_out.append({
                        "name": spec.get("title", "unknown"),
                        "status": status,
                        "duration": 0,
                    })
    except Exception:
        pass

total = passed + failed
reward = 1 if failed == 0 and total > 0 else 0
reward_path.write_text(str(reward))

ctrf = {
    "results": {
        "tool": {"name": "playwright"},
        "summary": {
            "tests": total,
            "passed": passed,
            "failed": failed,
            "skipped": 0,
            "pending": 0,
            "other": 0,
            "start": int(time.time()),
            "stop": int(time.time()),
        },
        "tests": tests_out,
    }
}
ctrf_path.write_text(json.dumps(ctrf, indent=2))
print(f"reward={reward} passed={passed} failed={failed}")
PY

exit 0
