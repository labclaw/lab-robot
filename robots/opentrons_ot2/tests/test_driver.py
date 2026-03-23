"""Tests for Opentrons OT-2 driver."""

from __future__ import annotations

from lab_robot.base import RobotDriver
from lab_robot.types import ActionType, PipetteAction
from robots.opentrons_ot2.driver import OT2Driver
from robots.opentrons_ot2.models import (
    LabwareConfig,
    OT2DeckConfig,
    PipetteConfig,
    PipetteMount,
)


def _default_deck() -> OT2DeckConfig:
    return OT2DeckConfig(
        slots={
            "1": LabwareConfig(labware_type="opentrons_96_tiprack_300ul", label="tips"),
            "2": LabwareConfig(labware_type="corning_96_wellplate_360ul_flat", label="source"),
            "3": LabwareConfig(labware_type="corning_96_wellplate_360ul_flat", label="dest"),
        },
        pipette_left=PipetteConfig(
            name="p300_single",
            mount=PipetteMount.LEFT,
            max_volume_ul=300.0,
            tip_rack_slots=["1"],
        ),
    )


class TestOT2Driver:
    def test_satisfies_robot_driver_protocol(self) -> None:
        driver = OT2Driver(deck_config=_default_deck(), simulate=True)
        assert isinstance(driver, RobotDriver)

    async def test_connect_simulate(self) -> None:
        driver = OT2Driver(deck_config=_default_deck(), simulate=True)
        result = await driver.connect()
        assert result is True
        state = await driver.get_state()
        assert state.connected

    async def test_execute_pipette(self) -> None:
        driver = OT2Driver(deck_config=_default_deck(), simulate=True)
        await driver.connect()
        action = PipetteAction(
            volume_ul=30.0,
            source_well="A1",
            dest_well="B1",
            source_labware="source",
            dest_labware="dest",
        )
        result = await driver.execute(action)
        assert result.success
        assert result.measurements.get("volume_dispensed_ul") == 30.0

    async def test_execute_without_connect_fails(self) -> None:
        driver = OT2Driver(deck_config=_default_deck(), simulate=True)
        action = PipetteAction(
            volume_ul=30.0,
            source_well="A1",
            dest_well="B1",
            source_labware="source",
            dest_labware="dest",
        )
        result = await driver.execute(action)
        assert not result.success
        assert "not connected" in result.error.lower()

    async def test_disconnect(self) -> None:
        driver = OT2Driver(deck_config=_default_deck(), simulate=True)
        await driver.connect()
        await driver.disconnect()
        state = await driver.get_state()
        assert not state.connected

    async def test_stop(self) -> None:
        driver = OT2Driver(deck_config=_default_deck(), simulate=True)
        await driver.connect()
        await driver.stop()
        state = await driver.get_state()
        assert not state.connected

    def test_capabilities(self) -> None:
        driver = OT2Driver(deck_config=_default_deck(), simulate=True)
        caps = driver.capabilities()
        assert ActionType.PIPETTE in caps

    async def test_unsupported_action(self) -> None:
        from lab_robot.types import MoveAction

        driver = OT2Driver(deck_config=_default_deck(), simulate=True)
        await driver.connect()
        action = MoveAction(target_position={"x": 0, "y": 0, "z": 0})
        result = await driver.execute(action)
        assert not result.success
        assert "not supported" in result.error.lower()

    async def test_execute_pipette_volume_exceeds_max(self) -> None:
        driver = OT2Driver(deck_config=_default_deck(), simulate=True)
        await driver.connect()
        action = PipetteAction(
            volume_ul=500.0,
            source_well="A1",
            dest_well="B1",
            source_labware="source",
            dest_labware="dest",
        )
        result = await driver.execute(action)
        assert not result.success
        assert "exceeds" in result.error.lower()
