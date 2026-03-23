"""Tests for PEI action -> Opentrons protocol translation."""

from __future__ import annotations

from lab_robot.types import PipetteAction
from robots.opentrons_ot2.models import (
    LabwareConfig,
    OT2DeckConfig,
    PipetteConfig,
    PipetteMount,
)
from robots.opentrons_ot2.protocol_gen import generate_protocol_commands


class TestProtocolGen:
    def _default_deck(self) -> OT2DeckConfig:
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

    def test_pipette_generates_commands(self) -> None:
        action = PipetteAction(
            volume_ul=30.0,
            source_well="A1",
            dest_well="B1",
            source_labware="source",
            dest_labware="dest",
        )
        deck = self._default_deck()
        commands = generate_protocol_commands(action, deck)
        assert len(commands) >= 3  # pick_up_tip, transfer, drop_tip
        assert commands[0]["command"] == "pick_up_tip"
        assert commands[-1]["command"] == "drop_tip"

    def test_pipette_no_new_tip(self) -> None:
        action = PipetteAction(
            volume_ul=30.0,
            source_well="A1",
            dest_well="B1",
            source_labware="source",
            dest_labware="dest",
            new_tip=False,
        )
        deck = self._default_deck()
        commands = generate_protocol_commands(action, deck)
        assert commands[0]["command"] != "pick_up_tip"

    def test_volume_exceeds_pipette_raises(self) -> None:
        import pytest

        action = PipetteAction(
            volume_ul=500.0,
            source_well="A1",
            dest_well="B1",
            source_labware="source",
            dest_labware="dest",
        )
        deck = self._default_deck()
        with pytest.raises(ValueError, match="exceeds.*300"):
            generate_protocol_commands(action, deck)

    def test_no_pipette_raises(self) -> None:
        import pytest

        deck = OT2DeckConfig()  # no pipettes configured
        action = PipetteAction(
            volume_ul=30.0,
            source_well="A1",
            dest_well="B1",
            source_labware="source",
            dest_labware="dest",
        )
        with pytest.raises(ValueError, match="No pipette"):
            generate_protocol_commands(action, deck)
