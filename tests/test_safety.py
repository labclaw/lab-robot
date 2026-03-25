"""Tests for robot safety types."""

from __future__ import annotations

from lab_robot.safety import SafetyVerdict, WorkspaceBounds, validate_workspace_bounds
from lab_robot.types import MoveAction


class TestSafetyVerdict:
    def test_allowed_verdict(self) -> None:
        verdict = SafetyVerdict(allowed=True, checker="workspace_bounds")
        assert verdict.allowed

    def test_blocked_verdict_with_reason(self) -> None:
        verdict = SafetyVerdict(
            allowed=False,
            checker="workspace_bounds",
            reason="Position x=500 exceeds max x=400",
        )
        assert not verdict.allowed
        assert "exceeds" in verdict.reason


class TestWorkspaceBounds:
    def test_non_move_action_allowed(self) -> None:
        """Non-move actions skip bounds checking entirely."""
        from lab_robot.types import PipetteAction

        bounds = WorkspaceBounds()
        action = PipetteAction(volume_ul=30.0, source_well="A1", dest_well="B1")
        verdict = validate_workspace_bounds(action, bounds)
        assert verdict.allowed

    def test_within_bounds(self) -> None:
        bounds = WorkspaceBounds(x_min=0, x_max=400, y_min=0, y_max=400, z_min=0, z_max=200)
        action = MoveAction(target_position={"x": 100, "y": 200, "z": 50})
        verdict = validate_workspace_bounds(action, bounds)
        assert verdict.allowed

    def test_out_of_bounds(self) -> None:
        bounds = WorkspaceBounds(x_min=0, x_max=400, y_min=0, y_max=400, z_min=0, z_max=200)
        action = MoveAction(target_position={"x": 500, "y": 200, "z": 50})
        verdict = validate_workspace_bounds(action, bounds)
        assert not verdict.allowed
        assert "x" in verdict.reason
