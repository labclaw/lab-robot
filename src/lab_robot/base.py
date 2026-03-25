"""RobotDriver protocol and executor.

RobotDriver is the core async interface for all robot hardware.
Unlike device-skills' BaseDriver (read-oriented), RobotDriver is
action-oriented: execute() returns rich ActionResult, not just bool.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from lab_robot.types import ActionResult, ActionStatus, ActionType, RobotAction, RobotState


@runtime_checkable
class RobotDriver(Protocol):
    """Async protocol for robot hardware drivers.

    Every robot driver must implement this interface. The key difference
    from device-skills' BaseDriver: execute() returns ActionResult with
    measurements and state, not just bool.
    """

    async def connect(self, config: dict[str, Any] | None = None) -> bool:
        """Connect to the robot. Returns True on success."""
        ...

    async def disconnect(self) -> None:
        """Disconnect from the robot."""
        ...

    async def execute(self, action: RobotAction) -> ActionResult:
        """Execute a physical action. Returns rich result with state."""
        ...

    async def stop(self) -> None:
        """Emergency stop — must be fast, no cleanup."""
        ...

    async def get_state(self) -> RobotState:
        """Get current robot state (position, tip, errors)."""
        ...

    def capabilities(self) -> list[ActionType]:
        """Return list of action types this robot supports."""
        ...


class RobotExecutor:
    """Validates capabilities then delegates to driver.

    Sits between the caller and the driver to enforce that only
    supported actions reach the hardware.
    """

    def __init__(self, driver: RobotDriver) -> None:
        self._driver = driver

    async def execute(self, action: RobotAction) -> ActionResult:
        """Check capability, then delegate to driver."""
        supported = self._driver.capabilities()
        if action.action_type not in supported:
            return ActionResult(
                success=False,
                status=ActionStatus.FAILED,
                action_type=action.action_type,
                error=f"Action {action.action_type} not supported. "
                f"Supported: {[s.value for s in supported]}",
            )
        return await self._driver.execute(action)
