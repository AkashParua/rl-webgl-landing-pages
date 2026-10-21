"""Generate Playwright tests from a ConstraintSpec.

Three stages:
1. Structure — nesting matches the sampled tree
2. Component — presence + attribute behaviors with real assertions
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
    for comp in components:
        yield comp, parent
        yield from _walk(comp.children, comp.type)

def _emit_action(lines: list[str], action: str, indent: str = "      ") -> None:
    if action == "hover":
        lines.append(f"{indent}await el.hover();")
    elif action == "click":
        lines.append(f"{indent}await el.click();")
    elif action == "right-click":
        lines.append(f"{indent}await el.click({{ button: 'right' }});")
    elif action == "drag":
        lines.append(f"{indent}await el.hover();")
        lines.append(f"{indent}// drag simulation")
        lines.append(f"{indent}await page.mouse.down();")
        lines.append(f"{indent}await page.mouse.move(100, 50);")
        lines.append(f"{indent}await page.mouse.up();")
    elif action == "wheel":
        lines.append(f"{indent}await el.hover();")
        lines.append(f"{indent}await page.mouse.wheel(0, -200);")
    elif action == "scroll":
        lines.append(f"{indent}await el.scrollIntoViewIfNeeded();")
    else:
        lines.append(f"{indent}await el.hover();")

def _emit_assert(lines: list[str], assert_def: dict, indent: str = "      ") -> None:
    kind = assert_def.get("type", "visible")

    if kind == "style_changes":
        prop = assert_def.get("property", "transform")
        contains = assert_def.get("contains")
        lines.append(f"{indent}const before = await el.evaluate(el => getComputedStyle(el).getPropertyValue('{prop}'));")
        # action already emitted by caller before this
        lines.append(f"{indent}const after = await el.evaluate(el => getComputedStyle(el).getPropertyValue('{prop}'));")
        lines.append(f"{indent}expect(after).not.toBe(before);")
        if contains:
            lines.append(f"{indent}expect(after).toContain('{contains}');")

    elif kind == "attribute_toggles":
        name = assert_def.get("name", "aria-pressed")
        lines.append(f"{indent}const before = await el.getAttribute('{name}');")
        lines.append(f"{indent}const after = await el.getAttribute('{name}');")
        lines.append(f"{indent}expect(after).not.toBe(before);")

    elif kind == "element_appears":
        sel = assert_def.get("selector", ".appeared")
        lines.append(f"{indent}await expect(page.locator('{sel}').first()).toBeVisible({{ timeout: 2000 }});")

    elif kind == "class_added":
        cls = assert_def.get("class", "active")
        lines.append(f"{indent}await expect(el).toHaveClass(/{cls}/);")

    else:  # visible fallback
        lines.append(f"{indent}await expect(el).toBeVisible();")

def generate_playwright_ts(spec: ConstraintSpec, mappings: dict | None = None) -> str:
    if mappings is None:
        mappings = load_mappings()

    lines = [
        "import { test, expect } from '@playwright/test';",
        "",
        f"test.describe('task {spec.template_id} / {spec.topic}', () => {{",
        "  test.beforeEach(async ({ page }) => {",
        "    await page.goto('/');",
        "  });",
        "",
    ]

    # Stage 1: Structure
    lines.append("  test.describe('structure', () => {")
    for comp, parent in _walk(spec.components):
        sel = _selector(comp.type, mappings)
        if parent == "page":
            lines.append(f"    test('{comp.type} exists', async ({{ page }}) => {{")
            lines.append(f"      await expect(page.locator('{sel}').first()).toBeVisible();")
            lines.append("    });")
        else:
            parent_sel = _selector(parent, mappings)
            lines.append(f"    test('{parent} contains {comp.type}', async ({{ page }}) => {{")
            lines.append(f"      const parent = page.locator('{parent_sel}').first();")
            lines.append(f"      await expect(parent.locator('{sel}').first()).toBeVisible();")
            lines.append("    });")
    lines.append("  });")
    lines.append("")

    # Stage 2: Components with real assertions
    lines.append("  test.describe('components', () => {")
    comp_mappings = mappings.get("components", {})
    for comp, _ in _walk(spec.components):
        sel = _selector(comp.type, mappings)
        cmap = comp_mappings.get(comp.type, {})
        if cmap.get("presence"):
            lines.append(f"    test('{comp.type} is present', async ({{ page }}) => {{")
            lines.append(f"      await expect(page.locator('{sel}').first()).toBeVisible();")
            lines.append("    });")

        attr_map = cmap.get("attributes", {})
        for attr_name, value in comp.attributes.items():
            if attr_name not in attr_map or value not in attr_map[attr_name]:
                continue
            info = attr_map[attr_name][value]
            action = info.get("action", "hover")
            assert_def = info.get("assert", {"type": "visible"})

            # For style_changes we need before-measurement, so special-case the order
            lines.append(f"    test('{comp.type} {attr_name}={value}', async ({{ page }}) => {{")
            lines.append(f"      const el = page.locator('{sel}').first();")

            if assert_def.get("type") == "style_changes":
                prop = assert_def.get("property", "transform")
                contains = assert_def.get("contains")
                lines.append(f"      const before = await el.evaluate(el => getComputedStyle(el).getPropertyValue('{prop}'));")
                _emit_action(lines, action)
                lines.append(f"      const after = await el.evaluate(el => getComputedStyle(el).getPropertyValue('{prop}'));")
                lines.append(f"      expect(after).not.toBe(before);")
                if contains:
                    lines.append(f"      expect(after).toContain('{contains}');")
            elif assert_def.get("type") == "attribute_toggles":
                name = assert_def.get("name", "aria-pressed")
                lines.append(f"      const before = await el.getAttribute('{name}');")
                _emit_action(lines, action)
                lines.append(f"      const after = await el.getAttribute('{name}');")
                lines.append(f"      expect(after).not.toBe(before);")
            else:
                _emit_action(lines, action)
                _emit_assert(lines, assert_def)

            lines.append("    });")
    lines.append("  });")
    lines.append("")

    # Stage 3: Content
    lines.append("  test.describe('content', () => {")
    for comp_type, text in spec.required_copy.items():
        sel = _selector(comp_type, mappings)
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
    content = generate_playwright_ts(spec)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content)

if __name__ == "__main__":
    from .sampler import sample_spec
    spec = sample_spec(42)
    print(generate_playwright_ts(spec))
