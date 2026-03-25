"""Opentrons OT-2 data models."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, field_validator

_VALID_SLOTS = {str(i) for i in range(1, 13)}


class PipetteMount(StrEnum):
    LEFT = "left"
    RIGHT = "right"


class DeckSlot:
    @staticmethod
    def validate_slot(slot: str) -> str:
        if slot not in _VALID_SLOTS:
            msg = f"Invalid slot '{slot}'. Must be 1-12."
            raise ValueError(msg)
        return slot


class PipetteConfig(BaseModel):
    name: str = Field(..., description="Pipette API name (e.g. p300_single)")
    mount: PipetteMount
    max_volume_ul: float = Field(..., gt=0)
    tip_rack_slots: list[str] = Field(default_factory=list)


class LabwareConfig(BaseModel):
    labware_type: str = Field(..., description="Opentrons labware API name")
    label: str = Field(default="")


class OT2DeckConfig(BaseModel):
    slots: dict[str, LabwareConfig] = Field(default_factory=dict)
    pipette_left: PipetteConfig | None = None
    pipette_right: PipetteConfig | None = None

    @field_validator("slots")
    @classmethod
    def validate_slot_numbers(cls, v: dict[str, LabwareConfig]) -> dict[str, LabwareConfig]:
        for slot in v:
            DeckSlot.validate_slot(slot)
        return v
