"""Translate PEI actions into Opentrons protocol commands.

This module converts high-level PipetteAction into a sequence of
Opentrons-compatible command dicts that the driver can execute.
"""

from __future__ import annotations

from typing import Any

from lab_robot.types import PipetteAction

from .models import OT2DeckConfig


def _find_pipette(deck: OT2DeckConfig) -> tuple[str, float]:
    """Find the first available pipette and its max volume."""
    for pipette in [deck.pipette_left, deck.pipette_right]:
        if pipette is not None:
            return pipette.name, pipette.max_volume_ul
    msg = "No pipette configured on deck"
    raise ValueError(msg)


def generate_protocol_commands(
    action: PipetteAction,
    deck: OT2DeckConfig,
) -> list[dict[str, Any]]:
    """Convert a PipetteAction into Opentrons protocol commands."""
    pipette_name, max_vol = _find_pipette(deck)

    if action.volume_ul > max_vol:
        msg = f"Volume {action.volume_ul}uL exceeds {pipette_name} max {max_vol}uL"
        raise ValueError(msg)

    commands: list[dict[str, Any]] = []

    if action.new_tip:
        commands.append(
            {
                "command": "pick_up_tip",
                "pipette": pipette_name,
            }
        )

    commands.append(
        {
            "command": "aspirate",
            "pipette": pipette_name,
            "volume_ul": action.volume_ul,
            "labware": action.source_labware,
            "well": action.source_well,
        }
    )

    commands.append(
        {
            "command": "dispense",
            "pipette": pipette_name,
            "volume_ul": action.volume_ul,
            "labware": action.dest_labware,
            "well": action.dest_well,
        }
    )

    if action.new_tip:
        commands.append(
            {
                "command": "drop_tip",
                "pipette": pipette_name,
            }
        )

    return commands
