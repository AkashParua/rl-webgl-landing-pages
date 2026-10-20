.PHONY: install pipeline quality score test lint

# --- Environment (uv) ---
install:
	uv sync

# --- Pipeline targets ---
pipeline:
	uv run python -m pipeline.generate --count 50 --seed 42

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
