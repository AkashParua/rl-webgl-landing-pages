"""Seeded hierarchical sampler for ConstraintSpec.

Generates deterministic task specifications from a taxonomy definition
and an integer seed. The same seed always produces the identical
component tree and attribute values.
"""

import random
from pathlib import Path
import yaml
from .models import ComponentSpec, ConstraintSpec

TAXONOMY_PATH = Path(__file__).parent / "taxonomy.yaml"

def load_taxonomy(path: Path = TAXONOMY_PATH) -> dict:
    """Load the taxonomy definition from YAML.

    Args:
        path: Path to the taxonomy YAML file. Defaults to taxonomy.yaml
            next to this module.

    Returns:
        Parsed taxonomy dictionary containing component_types,
        global_attributes, and page_templates.
    """
    with open(path) as f:
        return yaml.safe_load(f)

def _sample_attributes(rng: random.Random, attr_def: dict) -> dict:
    """Sample one value for each attribute from its list of choices.

    Args:
        rng: Seeded random number generator.
        attr_def: Mapping of attribute name to list of allowed values.

    Returns:
        Dictionary of sampled attribute values. Attributes whose value
        is not a non-empty list are skipped.
    """
    sampled = {}
    for key, choices in attr_def.items():
        if isinstance(choices, list) and choices:
            sampled[key] = rng.choice(choices)
    return sampled

def _build_component(
    rng: random.Random,
    comp_type: str,
    taxonomy: dict,
    children_slots: list[str] | None = None,
) -> ComponentSpec:
    """Recursively build a component and its children.

    Args:
        rng: Seeded random number generator.
        comp_type: Component type name (must exist in taxonomy).
        taxonomy: Full taxonomy dictionary.
        children_slots: Optional list of child component type names to
            instantiate under this component.

    Returns:
        A fully populated ComponentSpec with sampled attributes and
        recursively built children.
    """
    comp_def = taxonomy["component_types"].get(comp_type, {})
    attributes = _sample_attributes(rng, comp_def.get("attributes", {}))

    children = []
    slots = children_slots or []
    for slot in slots:
        children.append(_build_component(rng, slot, taxonomy))

    return ComponentSpec(type=comp_type, attributes=attributes, children=children)

def sample_spec(seed: int, taxonomy: dict | None = None) -> ConstraintSpec:
    """Generate a deterministic ConstraintSpec from a seed.

    Args:
        seed: Integer seed controlling all random choices. The same seed
            always yields the identical specification.
        taxonomy: Optional pre-loaded taxonomy dict. If None, the default
            taxonomy.yaml is loaded.

    Returns:
        A ConstraintSpec containing global attributes and a tree of
        components matching one of the page templates.
    """
    if taxonomy is None:
        taxonomy = load_taxonomy()

    rng = random.Random(seed)

    # Global attributes
    mood = rng.choice(taxonomy["global_attributes"]["mood"])
    palette = rng.choice(taxonomy["global_attributes"]["palette"])
    required_copy = rng.choice(taxonomy["global_attributes"]["required_copy_sets"])
    performance = rng.choice(taxonomy["global_attributes"]["performance_constraint"])

    # Pick a page template
    template = rng.choice(taxonomy["page_templates"])

    components = []
    for item in template["structure"]:
        comp = _build_component(
            rng,
            item["type"],
            taxonomy,
            children_slots=item.get("children_slots"),
        )
        components.append(comp)

    return ConstraintSpec(
        template_id=template["id"],
        mood=mood,
        palette=palette,
        required_copy=required_copy,
        performance_constraint=performance,
        components=components,
    )

if __name__ == "__main__":
    spec = sample_spec(seed=42)
    print(spec.model_dump_json(indent=2))
