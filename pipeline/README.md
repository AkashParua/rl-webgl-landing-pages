# Pipeline

Brief synthesis, grader synthesis, and instruction rendering.

## LLM usage

Brief expansion uses the pluggable client in `llm/`.

- Default: local Ollama (`qwen3.5:4b`)
- Switch to any OpenAI-compatible API via environment variables

See `llm/README.md` for setup.

Taxonomy definition, combinatorial sampling, and the rest of the generation logic live here.
LLM prompts for brief expansion go in `prompts/`.
