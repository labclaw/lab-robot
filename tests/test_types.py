"""Tests for PEI type definitions."""

from __future__ import annotations

from lab_robot.types import (
    ActionResult,
    ActionStatus,
    ActionType,
    MoveAction,
    PipetteAction,
    RobotState,
    TransferLabwareAction,
)


class TestActionTypes:
    def test_pipette_action_valid(self) -> None:
        action = PipetteAction(
            volume_ul=30.0,
            source_well="A1",
            dest_well="B1",
        )
        assert action.action_type == ActionType.PIPETTE
        assert action.volume_ul == 30.0

    def test_pipette_action_rejects_negative_volume(self) -> None:
        import pytest

        with pytest.raises(ValueError, match="greater than 0"):
            PipetteAction(volume_ul=-5.0, source_well="A1", dest_well="B1")

    def test_pipette_action_rejects_excessive_volume(self) -> None:
        import pytest

        with pytest.raises(ValueError, match="exceeds maximum"):
            PipetteAction(volume_ul=2000.0, source_well="A1", dest_well="B1")

    def test_move_action(self) -> None:
        action = MoveAction(target_position={"x": 100.0, "y": 200.0, "z": 50.0})
        assert action.action_type == ActionType.MOVE

    def test_transfer_labware_action(self) -> None:
        action = TransferLabwareAction(
            labware_id="plate_96_A",
            from_slot="1",
            to_slot="3",
        )
        assert action.action_type == ActionType.TRANSFER_LABWARE


class TestActionResult:
    def test_success_result(self) -> None:
        result = ActionResult(
            success=True,
            status=ActionStatus.COMPLETED,
            action_type=ActionType.PIPETTE,
            measurements={"volume_dispensed_ul": 30.0},
        )
        assert result.success
        assert result.status == ActionStatus.COMPLETED

    def test_failure_result_with_error(self) -> None:
        result = ActionResult(
            success=False,
            status=ActionStatus.FAILED,
            action_type=ActionType.PIPETTE,
            error="No tips available in rack",
        )
        assert not result.success
        assert "tips" in result.error

    def test_result_requires_error_on_failure(self) -> None:
        import pytest

        with pytest.raises(ValueError, match="error.*required"):
            ActionResult(
                success=False,
                status=ActionStatus.FAILED,
                action_type=ActionType.PIPETTE,
            )


class TestRobotState:
    def test_robot_state(self) -> None:
        state = RobotState(
            connected=True,
            homed=True,
            current_position={"x": 0.0, "y": 0.0, "z": 0.0},
        )
        assert state.connected
        assert state.homed
