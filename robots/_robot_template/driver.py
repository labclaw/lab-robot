"""Template robot driver — copy this directory to start a new robot.

Replace TemplateRobotDriver with your robot name and implement each method.
Every method raises NotImplementedError until you implement it.
"""

from __future__ import annotations

from typing import Any

from lab_robot.types import ActionResult, ActionType, RobotAction, RobotState


class TemplateRobotDriver:
    """Skeleton driver implementing the RobotDriver protocol.

    Copy this file, rename the class, and implement each method.
    """

    async def connect(self, config: dict[str, Any] | None = None) -> bool:
        """Connect to the robot hardware."""
        raise NotImplementedError

    async def disconnect(self) -> None:
        """Disconnect from the robot."""
        raise NotImplementedError

    async def execute(self, action: RobotAction) -> ActionResult:
        """Execute a physical action."""
        raise NotImplementedError

    async def stop(self) -> None:
        """Emergency stop."""
        raise NotImplementedError

    async def get_state(self) -> RobotState:
        """Return current robot state."""
        raise NotImplementedError

    def capabilities(self) -> list[ActionType]:
        """Return supported action types."""
        raise NotImplementedError
