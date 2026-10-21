#!/bin/bash
# Harbor verifier entrypoint.
# Expects:
#   - page container reachable at $BASE_URL (default http://page:80)
#   - tests mounted at /tests
# Writes binary reward to /logs/verifier/reward.txt

set -e
mkdir -p /logs/verifier

# Fail-safe 0 before anything else
echo 0 > /logs/verifier/reward.txt

cd /work
npx playwright test --config=/work/playwright.config.ts --reporter=line || TEST_EXIT=$?

if [ "${TEST_EXIT:-0}" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

# Also emit a simple CTRF-like summary
cat > /logs/verifier/ctrf.json << EOF
{
  "results": {
    "tool": { "name": "playwright" },
    "summary": { "tests": 0, "passed": 0, "failed": 0 },
    "reward": $(cat /logs/verifier/reward.txt)
  }
}
EOF

exit 0
