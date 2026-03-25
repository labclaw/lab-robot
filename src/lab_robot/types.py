"""PEI type definitions — actions, results, and robot state.

PEI primitives are layered:
  Layer 0 — Motion:     move_to, grip, release, home
  Layer 1 — Lab Ops:    pipette, transfer_labware, dispense
  Layer 2 — Perception: detect_labware, verify_state, calibrate
  Layer 3 — System:     recover, emergency_stop, wait_condition
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class ActionType(StrEnum):
    """PEI action types across all layers."""

    # Layer 0 — Motion
    MOVE = "move"
    GRIP = "grip"
    RELEASE = "release"
    HOME = "home"
    # Layer 1 — Lab Ops
    PIPETTE = "pipette"
    TRANSFER_LABWARE = "transfer_labware"
    DISPENSE = "dispense"
    # Layer 2 — Perception
    DETECT_LABWARE = "detect_labware"
    VERIFY_STATE = "verify_state"
    CALIBRATE = "calibrate"
    # Layer 3 — System
    RECOVER = "recover"
    EMERGENCY_STOP = "emergency_stop"
    WAIT_CONDITION = "wait_condition"


class ActionStatus(StrEnum):
    """Execution status of a robot action."""

    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ── Base Action ──────────────────────────────────────────────────────────────


class RobotAction(BaseModel):
    """Base class for all PEI actions."""

    action_type: ActionType

    model_config = {"frozen": True}


# ── Layer 0: Motion Primitives ───────────────────────────────────────────────


class MoveAction(RobotAction):
    """Move to a target position in robot coordinate space."""

    action_type: ActionType = ActionType.MOVE
    target_position: dict[str, float] = Field(..., description="Target pose {x, y, z} in mm")
    speed_mm_s: float = Field(default=50.0, gt=0, description="Movement speed")


# ── Layer 1: Lab Operations ──────────────────────────────────────────────────

_MAX_PIPETTE_VOLUME_UL = 1000.0


class PipetteAction(RobotAction):
    """Aspirate from source well and dispense to destination well."""

    action_type: ActionType = ActionType.PIPETTE
    volume_ul: float = Field(..., gt=0, description="Volume in microliters")
    source_well: str = Field(..., min_length=1, description="Source well ID (e.g. A1)")
    dest_well: str = Field(..., min_length=1, description="Destination well ID")
    source_labware: str = Field(default="source_plate", description="Source labware name")
    dest_labware: str = Field(default="dest_plate", description="Destination labware name")
    liquid_class: str = Field(default="default", description="Liquid handling profile")
    new_tip: bool = Field(default=True, description="Pick up a new tip before transfer")

    @model_validator(mode="after")
    def validate_volume(self) -> PipetteAction:
        if self.volume_ul > _MAX_PIPETTE_VOLUME_UL:
            msg = f"volume_ul={self.volume_ul} exceeds maximum {_MAX_PIPETTE_VOLUME_UL}"
            raise ValueError(msg)
        return self


class TransferLabwareAction(RobotAction):
    """Transfer labware between slots on the deck."""

    action_type: ActionType = ActionType.TRANSFER_LABWARE
    labware_id: str = Field(..., description="Labware identifier")
    from_slot: str = Field(..., description="Source deck slot")
    to_slot: str = Field(..., description="Destination deck slot")


# ── Action Result ────────────────────────────────────────────────────────────


class ActionResult(BaseModel):
    """Rich result from executing a robot action."""

    success: bool
    status: ActionStatus
    action_type: ActionType
    measurements: dict[str, Any] = Field(
        default_factory=dict, description="Measured values (e.g. volume_dispensed_ul)"
    )
    state_after: dict[str, Any] = Field(
        default_factory=dict, description="Robot state after action"
    )
    error: str = Field(default="", description="Error message if failed")
    duration_s: float = Field(default=0.0, ge=0, description="Action duration in seconds")

    @model_validator(mode="after")
    def require_error_on_failure(self) -> ActionResult:
        if not self.success and not self.error:
            msg = "error is required when success=False"
            raise ValueError(msg)
        return self


# ── Robot State ──────────────────────────────────────────────────────────────


class RobotState(BaseModel):
    """Current state of the robot."""

    connected: bool = False
    homed: bool = False
    current_position: dict[str, float] = Field(default_factory=dict)
    tip_attached: bool = False
    current_volume_ul: float = 0.0
    errors: list[str] = Field(default_factory=list)
