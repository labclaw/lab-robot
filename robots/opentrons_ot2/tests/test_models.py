"""Tests for Opentrons OT-2 models."""

from __future__ import annotations

import pytest

from robots.opentrons_ot2.models import (
    DeckSlot,
    LabwareConfig,
    OT2DeckConfig,
    PipetteConfig,
    PipetteMount,
)


class TestPipetteConfig:
    def test_p300_single(self) -> None:
        pipette = PipetteConfig(
            name="p300_single",
            mount=PipetteMount.LEFT,
            max_volume_ul=300.0,
        )
        assert pipette.name == "p300_single"
        assert pipette.max_volume_ul == 300.0

    def test_rejects_invalid_mount(self) -> None:
        with pytest.raises(ValueError):
            PipetteConfig(name="p300_single", mount="middle", max_volume_ul=300)


class TestDeckConfig:
    def test_default_deck(self) -> None:
        deck = OT2DeckConfig()
        assert len(deck.slots) == 0

    def test_add_labware(self) -> None:
        deck = OT2DeckConfig(
            slots={
                "1": LabwareConfig(labware_type="opentrons_96_tiprack_300ul", label="tips"),
                "2": LabwareConfig(labware_type="corning_96_wellplate_360ul_flat", label="plate"),
            }
        )
        assert "1" in deck.slots
        assert deck.slots["2"].label == "plate"

    def test_slot_validation(self) -> None:
        with pytest.raises(ValueError, match="Invalid slot"):
            DeckSlot.validate_slot("13")
