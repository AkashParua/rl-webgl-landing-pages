"""Render an agent-facing instruction.md from a ConstraintSpec.

Deterministic and leak-free: describes the desired page without mentioning
tests, thresholds, or grader internals.
"""

from .models import ComponentSpec, ConstraintSpec

def _describe_component(comp: ComponentSpec, indent: int = 0) -> list[str]:
    pad = "  " * indent
    lines = [f"{pad}- {comp.type}"]
    if comp.attributes:
        attrs = ", ".join(f"{k}: {v}" for k, v in comp.attributes.items())
        lines.append(f"{pad}  ({attrs})")
    for child in comp.children:
        lines.extend(_describe_component(child, indent + 1))
    return lines

def render_instruction(spec: ConstraintSpec) -> str:
    """Return a markdown instruction the agent can follow."""
    structure_lines = []
    for comp in spec.components:
        structure_lines.extend(_describe_component(comp))

    copy_lines = []
    for comp_type, text in spec.required_copy.items():
        copy_lines.append(f"- The {comp_type} must visibly contain: \"{text}\"")

    parts = [
        "# WebGL Landing Page Brief",
        "",
        f"Create a single-file WebGL / Three.js landing page.",
        "",
        f"**Topic:** {spec.topic}",
        f"**Mood:** {spec.mood}",
        f"**Palette:** {spec.palette}",
        f"**Template:** {spec.template_id}",
        f"**Performance:** {spec.performance_constraint}",
        "",
        "## Required structure",
        "Mark every major section and interactive element with",
        "`data-component=\"<type>\"` using the types below.",
        "",
        "\n".join(structure_lines),
        "",
        "## Required copy",
        "\n".join(copy_lines) if copy_lines else "- (none)",
        "",
        "## Interactions",
        "Implement the behaviors listed in the structure (hover, click,",
        "drag, zoom, etc.). Each interactive element should visibly react.",
        "",
        "## Deliverable",
        "A single HTML file (with embedded CSS/JS) that runs in a browser",
        "with no build step. Include a `<canvas>` or Three.js scene where",
        "a webgl_canvas component is required.",
        "",
    ]
    return "\n".join(parts)
