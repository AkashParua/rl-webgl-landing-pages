"""Generate a submission page for a task.

Modes:
  manual – print the prompt so you can paste it into Claude / any chat
  llm    – call the configured LLM client and write submission/index.html
"""

from pathlib import Path
from .llm import get_client

SYSTEM = """You are an expert frontend developer who writes single-file WebGL / Three.js landing pages.

Rules:
- Output ONLY a complete HTML document. No markdown fences, no explanation.
- Use inline <style> and <script>. Three.js may be loaded from a CDN.
- Every major section and interactive element MUST have the exact data-component="<type>" attribute requested in the brief.
- Required copy must appear exactly as specified.
- Interactive behaviors (hover, click, drag, zoom, etc.) must produce a visible reaction.
- The page must work when opened as a static file served by a simple HTTP server.
"""

def build_prompt(instruction_md: str) -> str:
    return f"""Create a single-file HTML landing page that satisfies this brief.

{instruction_md}

Remember: output only the HTML document."""

def extract_html(text: str) -> str:
    """Pull HTML out of a model response (handles optional fences)."""
    text = text.strip()
    if "```html" in text:
        text = text.split("```html", 1)[1]
        text = text.split("```", 1)[0]
    elif "```" in text:
        text = text.split("```", 1)[1]
        text = text.split("```", 1)[0]
    # ensure it looks like HTML
    if "<html" not in text.lower() and "<!doctype" not in text.lower():
        # wrap if the model returned a fragment
        text = f"<!DOCTYPE html>\n<html>\n<body>\n{text}\n</body>\n</html>"
    return text.strip()

def generate_manual(task_dir: Path) -> str:
    instruction = (task_dir / "instruction.md").read_text()
    prompt = build_prompt(instruction)
    return f"SYSTEM:\n{SYSTEM}\n\nUSER:\n{prompt}"

def generate_llm(task_dir: Path) -> Path:
    instruction = (task_dir / "instruction.md").read_text()
    prompt = build_prompt(instruction)

    client = get_client()
    raw = client.generate(prompt, system=SYSTEM)
    html = extract_html(raw)

    out = task_dir / "submission" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    return out
