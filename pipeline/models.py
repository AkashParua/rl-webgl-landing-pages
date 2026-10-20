from pydantic import BaseModel, Field
from typing import Any

class ComponentSpec(BaseModel):
    type: str
    attributes: dict[str, Any] = Field(default_factory=dict)
    children: list["ComponentSpec"] = Field(default_factory=list)

class ConstraintSpec(BaseModel):
    """Machine-readable constraint specification for one task."""
    template_id: str
    mood: str
    palette: str
    required_copy: list[str]
    performance_constraint: str
    components: list[ComponentSpec]

    model_config = {"extra": "forbid"}

# Resolve forward ref
ComponentSpec.model_rebuild()
