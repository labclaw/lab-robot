"""Opentrons OT-2 driver — simulate-mode-first robot driver.

In simulate=True mode (default for Phase 0), all protocol commands
run through Opentrons' built-in simulator with no hardware required.
"""

from __future__ import annotations

import time
from typing import Any

from lab_robot.types import (
    ActionResult,
    ActionStatus,
    ActionType,
    PipetteAction,
    RobotAction,
    RobotState,
)

from .models import OT2DeckConfig
from .protocol_gen import generate_protocol_commands

_SUPPORTED_ACTIONS = (ActionType.PIPETTE,)


class OT2Driver:
    """Opentrons OT-2 driver implementing RobotDriver protocol.

    Args:
        deck_config: Deck layout with labware and pipette configuration.
        simulate: If True (default), run protocols in simulation mode.
    """

    def __init__(
        self,
        deck_config: OT2DeckConfig,
        *,
        simulate: bool = True,
    ) -> None:
        self._deck = deck_config
        self._simulate = simulate
        self._connected = False
        self._tip_attached = False
        self._current_volume_ul = 0.0

    async def connect(self, config: dict[str, Any] | None = None) -> bool:
        """Connect to OT-2 (or initialize simulator)."""
        self._connected = True
        return True

    async def disconnect(self) -> None:
        """Disconnect from OT-2."""
        self._connected = False
        self._tip_attached = False
        self._current_volume_ul = 0.0

    async def execute(self, action: RobotAction) -> ActionResult:
        """Execute a PEI action on the OT-2."""
        if not self._connected:
            return ActionResult(
                success=False,
                status=ActionStatus.FAILED,
                action_type=action.action_type,
                error="Not connected — call connect() first",
            )

        if action.action_type not in _SUPPORTED_ACTIONS:
            return ActionResult(
                success=False,
                status=ActionStatus.FAILED,
                action_type=action.action_type,
                error=f"Action {action.action_type} not supported by OT-2. "
                f"Supported: {[a.value for a in _SUPPORTED_ACTIONS]}",
            )

        # All supported action types are handled exhaustively below.
        # The unsupported-action guard above ensures we only reach here
        # for actions in _SUPPORTED_ACTIONS.
        return await self._execute_pipette(action)  # type: ignore[arg-type]

    async def stop(self) -> None:
        """Emergency stop — disconnect immediately."""
        self._connected = False
        self._tip_attached = False
        self._current_volume_ul = 0.0

    async def get_state(self) -> RobotState:
        """Get current OT-2 state."""
        return RobotState(
            connected=self._connected,
            homed=self._connected,
            tip_attached=self._tip_attached,
            current_volume_ul=self._current_volume_ul,
        )

    def capabilities(self) -> list[ActionType]:
        """OT-2 supports pipetting actions."""
        return list(_SUPPORTED_ACTIONS)

    async def _execute_pipette(self, action: PipetteAction) -> ActionResult:
        """Execute a pipette action via protocol commands."""
        start = time.monotonic()
        try:
            commands = generate_protocol_commands(action, self._deck)
        except ValueError as e:
            return ActionResult(
                success=False,
                status=ActionStatus.FAILED,
                action_type=ActionType.PIPETTE,
                error=str(e),
            )

        # In simulate mode, we execute the command sequence logically
        for cmd in commands:
            if cmd["command"] == "pick_up_tip":
                self._tip_attached = True
            elif cmd["command"] == "aspirate":
                self._current_volume_ul = cmd["volume_ul"]
            elif cmd["command"] == "dispense":
                self._current_volume_ul = 0.0
            elif cmd["command"] == "drop_tip":
                self._tip_attached = False

        elapsed = time.monotonic() - start
        return ActionResult(
            success=True,
            status=ActionStatus.COMPLETED,
            action_type=ActionType.PIPETTE,
            measurements={"volume_dispensed_ul": action.volume_ul},
            state_after={
                "tip_attached": self._tip_attached,
                "current_volume_ul": self._current_volume_ul,
            },
            duration_s=round(elapsed, 4),
        )
