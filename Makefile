# Placeholder targets. Implement the real logic in the respective directories.

.PHONY: pipeline quality score

pipeline:
	@echo "TODO: generate 50 Harbor bundles from count + seed"
	@echo "Deterministic. Write to tasks/"

quality:
	@echo "TODO: run the six quality gates on generated tasks"
	@echo "Write yield report and reject log to quality/"

score:
	@echo "TODO: score a submission against a bundle"
	@echo "Usage: make score BUNDLE=tasks/foo SUBMISSION=path/to/scene.html"
