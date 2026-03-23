"""lab-robot — Physical Execution Interface for science labs."""

from __future__ import annotations

from lab_robot.base import RobotDriver, RobotExecutor
from lab_robot.safety import SafetyVerdict, WorkspaceBounds, validate_workspace_bounds
from lab_robot.schema import RobotCapabilities, RobotCategory, RobotManifest, RobotSafetyLevel
from lab_robot.types import (
    ActionResult,
    ActionStatus,
    ActionType,
    MoveAction,
    PipetteAction,
    RobotAction,
    RobotState,
    TransferLabwareAction,
)

__version__ = "0.1.0"

__all__ = [
    "ActionResult",
    "ActionStatus",
    "ActionType",
    "MoveAction",
    "PipetteAction",
    "RobotAction",
    "RobotCapabilities",
    "RobotCategory",
    "RobotDriver",
    "RobotExecutor",
    "RobotManifest",
    "RobotSafetyLevel",
    "RobotState",
    "SafetyVerdict",
    "TransferLabwareAction",
    "WorkspaceBounds",
    "validate_workspace_bounds",
]
