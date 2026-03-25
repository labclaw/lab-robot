"""Tests for RobotDriver protocol and RobotExecutor."""

from __future__ import annotations

from typing import Any

from lab_robot.base import RobotDriver, RobotExecutor
from lab_robot.types import (
    ActionResult,
    ActionStatus,
    ActionType,
    PipetteAction,
    RobotAction,
    RobotState,
)


class FakeDriver:
    """Minimal RobotDriver implementation for testing."""

    def __init__(self, *, fail: bool = False) -> None:
        self._connected = False
        self._fail = fail

    async def connect(self, config: dict[str, Any] | None = None) -> bool:
        self._connected = True
        return True

    async def disconnect(self) -> None:
        self._connected = False

    async def execute(self, action: RobotAction) -> ActionResult:
        if self._fail:
            return ActionResult(
                success=False,
                status=ActionStatus.FAILED,
                action_type=action.action_type,
                error="Simulated failure",
            )
        return ActionResult(
            success=True,
            status=ActionStatus.COMPLETED,
            action_type=action.action_type,
            measurements={"volume_dispensed_ul": 30.0},
        )

    async def stop(self) -> None:
        self._connected = False

    async def get_state(self) -> RobotState:
        return RobotState(connected=self._connected)

    def capabilities(self) -> list[ActionType]:
        return [ActionType.PIPETTE]


class TestRobotDriverProtocol:
    def test_fake_driver_satisfies_protocol(self) -> None:
        driver = FakeDriver()
        assert isinstance(driver, RobotDriver)

    async def test_connect_and_execute(self) -> None:
        driver = FakeDriver()
        await driver.connect()
        action = PipetteAction(volume_ul=30.0, source_well="A1", dest_well="B1")
        result = await driver.execute(action)
        assert result.success

    async def test_stop(self) -> None:
        driver = FakeDriver()
        await driver.connect()
        await driver.stop()
        state = await driver.get_state()
        assert not state.connected


class TestRobotExecutor:
    async def test_execute_success(self) -> None:
        driver = FakeDriver()
        executor = RobotExecutor(driver=driver)
        await driver.connect()
        action = PipetteAction(volume_ul=30.0, source_well="A1", dest_well="B1")
        result = await executor.execute(action)
        assert result.success

    async def test_execute_rejects_unsupported_action(self) -> None:
        driver = FakeDriver()
        executor = RobotExecutor(driver=driver)
        await driver.connect()
        from lab_robot.types import MoveAction

        action = MoveAction(target_position={"x": 0, "y": 0, "z": 0})
        result = await executor.execute(action)
        assert not result.success
        assert "not supported" in result.error

    async def test_execute_propagates_driver_failure(self) -> None:
        driver = FakeDriver(fail=True)
        executor = RobotExecutor(driver=driver)
        await driver.connect()
        action = PipetteAction(volume_ul=30.0, source_well="A1", dest_well="B1")
        result = await executor.execute(action)
        assert not result.success


def test_version_fallback_on_missing_package() -> None:
    """When package metadata is unavailable, __version__ falls back to '0.1.0'."""
    import subprocess
    import sys

    code = (
        "import importlib.metadata, unittest.mock as m, sys\n"
        "with m.patch('importlib.metadata.version',\n"
        "              side_effect=importlib.metadata.PackageNotFoundError('x')):\n"
        "    sys.modules.pop('lab_robot', None)\n"
        "    import lab_robot\n"
        "    print(lab_robot.__version__)\n"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert result.stdout.strip() == "0.1.0"
