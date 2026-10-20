# LLM Client

Pluggable abstraction so the pipeline can use either a local model (Ollama) or any OpenAI-compatible API (OpenAI, Groq, OpenRouter, Together, etc.).

## Setup

### Local (Ollama) — default
```bash
# Install Ollama from https://ollama.com
ollama pull qwen3.5:4b

export LLM_PROVIDER=ollama
export OLLAMA_MODEL=qwen3.5:4b
```

### Cloud / API
```bash
export LLM_PROVIDER=openai          # or groq, openrouter, custom, …
export LLM_API_KEY=sk-...
export LLM_MODEL=gpt-4o-mini
# optional:
export LLM_BASE_URL=https://api.groq.com/openai/v1
```

Copy `.env.example` to `.env` and fill in values. Never commit `.env`.

## Usage

```python
from pipeline.llm import get_client

client = get_client()
brief = client.generate(
    prompt="Expand this spec into a short landing-page brief: ...",
    system="You write concise, vivid product briefs.",
)
```

The rest of the pipeline only depends on the `LLMClient` interface.
