"""Robot safety types and basic validators.

Shared types: SafetyVerdict is the common data contract across
device-use and lab-robot. Implementations are domain-specific.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from lab_robot.types import ActionType, MoveAction, RobotAction


class SafetyVerdict(BaseModel):
    """Result of a safety check — shared data contract."""

    allowed: bool
    checker: str = Field(..., description="Which checker produced this verdict")
    reason: str = Field(default="", description="Why it was blocked")
    requires_confirmation: bool = Field(default=False)


class WorkspaceBounds(BaseModel):
    """3D workspace boundary definition."""

    x_min: float = 0
    x_max: float = 400
    y_min: float = 0
    y_max: float = 400
    z_min: float = 0
    z_max: float = 200


def validate_workspace_bounds(action: RobotAction, bounds: WorkspaceBounds) -> SafetyVerdict:
    """Check if a move action stays within workspace bounds."""
    if action.action_type != ActionType.MOVE or not isinstance(action, MoveAction):
        return SafetyVerdict(allowed=True, checker="workspace_bounds")

    pos = action.target_position
    violations: list[str] = []

    for axis, (lo, hi) in [
        ("x", (bounds.x_min, bounds.x_max)),
        ("y", (bounds.y_min, bounds.y_max)),
        ("z", (bounds.z_min, bounds.z_max)),
    ]:
        val = pos.get(axis, 0.0)
        if val < lo or val > hi:
            violations.append(f"{axis}={val} outside [{lo}, {hi}]")

    if violations:
        return SafetyVerdict(
            allowed=False,
            checker="workspace_bounds",
            reason="; ".join(violations),
        )
    return SafetyVerdict(allowed=True, checker="workspace_bounds")
