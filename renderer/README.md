# Headless capture harness

Deterministic headless Chromium (or equivalent) renderer:

- Pinned browser version
- Fixed viewport and device pixel ratio
- Stubbed clock
- Seeded randomness
- Scripted virtual-time sequence (not wall-clock)
- Per-episode time budget enforced

No GPU required.
