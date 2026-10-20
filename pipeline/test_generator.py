"""Generate Playwright tests from a ConstraintSpec.

Three stages:
1. Structure — nesting matches the sampled tree
2. Component — presence + attribute behaviors from test_mappings.yaml
3. Content — required_copy text appears inside the matching component
"""

from pathlib import Path
import yaml
from .models import ComponentSpec, ConstraintSpec

MAPPINGS_PATH = Path(__file__).parent / "test_mappings.yaml"

def load_mappings(path: Path = MAPPINGS_PATH) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)

def _selector(comp_type: str, mappings: dict) -> str:
    template = mappings.get("selector", '[data-component="{type}"]')
    return template.format(type=comp_type)

def _walk(components: list[ComponentSpec], parent: str = "page"):
    """Yield (component, parent_type) pairs."""
    for comp in components:
        yield comp, parent
        yield from _walk(comp.children, comp.type)

def generate_playwright_ts(spec: ConstraintSpec, mappings: dict | None = None) -> str:
    """Return a Playwright TypeScript test file as a string."""
    if mappings is None:
        mappings = load_mappings()

    lines = [
        "import { test, expect } from '@playwright/test';",
        "",
        f"test.describe('task {spec.template_id} / {spec.topic}', () => {{",
        "  test.beforeEach(async ({ page }) => {",
        "    await page.goto('/');  // adjust to the served page",
        "  });",
        "",
    ]

    # --- Stage 1: Structure ---
    lines.append("  test.describe('structure', () => {")
    for comp, parent in _walk(spec.components):
        sel = _selector(comp.type, mappings)
        if parent == "page":
            lines.append(f"    test('{comp.type} exists', async ({{ page }}) => {{")
            lines.append(f"      await expect(page.locator('{sel}')).toHaveCount(1); // or >= 1")
            lines.append("    });")
        else:
            parent_sel = _selector(parent, mappings)
            lines.append(f"    test('{parent} contains {comp.type}', async ({{ page }}) => {{")
            lines.append(f"      const parent = page.locator('{parent_sel}');")
            lines.append(f"      await expect(parent.locator('{sel}')).toHaveCount(1); // or >= 1")
            lines.append("    });")
    lines.append("  });")
    lines.append("")

    # --- Stage 2: Component behaviors ---
    lines.append("  test.describe('components', () => {")
    comp_mappings = mappings.get("components", {})
    for comp, _ in _walk(spec.components):
        sel = _selector(comp.type, mappings)
        cmap = comp_mappings.get(comp.type, {})
        if cmap.get("presence"):
            lines.append(f"    test('{comp.type} is present', async ({{ page }}) => {{")
            lines.append(f"      await expect(page.locator('{sel}')).toBeVisible();")
            lines.append("    });")

        attr_map = cmap.get("attributes", {})
        for attr_name, value in comp.attributes.items():
            if attr_name in attr_map and value in attr_map[attr_name]:
                info = attr_map[attr_name][value]
                action = info.get("action", "interact")
                note = info.get("note", "")
                lines.append(f"    test('{comp.type} {attr_name}={value}', async ({{ page }}) => {{")
                lines.append(f"      const el = page.locator('{sel}').first();")
                if action == "hover":
                    lines.append("      await el.hover();")
                elif action == "click":
                    lines.append("      await el.click();")
                elif action == "right-click":
                    lines.append("      await el.click({ button: 'right' });")
                elif action == "drag":
                    lines.append("      // TODO: simulate drag")
                    lines.append("      await el.hover();")
                elif action == "wheel":
                    lines.append("      // TODO: simulate wheel")
                    lines.append("      await el.hover();")
                else:
                    lines.append("      await el.hover();")
                lines.append(f"      // assert: {note}")
                lines.append("      await expect(el).toBeVisible();  // replace with real assertion")
                lines.append("    });")
    lines.append("  });")
    lines.append("")

    # --- Stage 3: Content ---
    lines.append("  test.describe('content', () => {")
    for comp_type, text in spec.required_copy.items():
        sel = _selector(comp_type, mappings)
        # escape quotes in text
        safe_text = text.replace("'", "\\'")
        lines.append(f"    test('{comp_type} contains required copy', async ({{ page }}) => {{")
        lines.append(f"      const el = page.locator('{sel}').first();")
        lines.append(f"      await expect(el).toContainText('{safe_text}');")
        lines.append("    });")
    lines.append("  });")
    lines.append("});")
    lines.append("")

    return "\n".join(lines)

def write_tests(spec: ConstraintSpec, out_path: Path) -> None:
    """Write the generated Playwright file to disk."""
    content = generate_playwright_ts(spec)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content)

if __name__ == "__main__":
    from .sampler import sample_spec
    spec = sample_spec(42)
    print(generate_playwright_ts(spec))
