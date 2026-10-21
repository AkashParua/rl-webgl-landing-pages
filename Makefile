.PHONY: install pipeline quality score test lint generate-tasks generate-page evaluate

# --- Environment (uv) ---
install:
	uv sync

# --- Pipeline targets ---
generate-tasks:
	uv run python -m pipeline generate-tasks --count $(or $(COUNT),1) --seed $(or $(SEED),42)

generate-page:
	uv run python -m pipeline generate-page $(TASK) --mode $(or $(MODE),manual)

pipeline:
	uv run python -m pipeline generate-tasks --count 50 --seed 42

evaluate:
	uv run python -m pipeline evaluate $(TASK)

quality:
	uv run python -m quality.run_gates

score:
	uv run python -m reward.score $(BUNDLE) $(SUBMISSION)

# --- Dev ---
test:
	uv run pytest

lint:
	uv run ruff check .

# --- Helpers ---
env-example:
	@echo "Copy .env.example to .env and fill in values"
