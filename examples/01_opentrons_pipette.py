#!/usr/bin/env python3
"""Example: OT-2 pipette simulation.

Demonstrates the lab-robot PEI interface by running a simple pipette
transfer on the Opentrons OT-2 in simulate mode. No hardware required.

Usage:
    python examples/01_opentrons_pipette.py
"""

from __future__ import annotations

import asyncio

from lab_robot.types import PipetteAction
from robots.opentrons_ot2.driver import OT2Driver
from robots.opentrons_ot2.models import OT2DeckConfig, OT2PipetteConfig


async def main() -> None:
    """Run a simulated OT-2 pipette transfer."""
    # 1. Configure the deck
    deck = OT2DeckConfig(
        labware={
            "1": "opentrons_96_tiprack_300ul",
            "2": "corning_96_wellplate_360ul_flat",
            "3": "corning_96_wellplate_360ul_flat",
        },
        pipettes={"left": OT2PipetteConfig(name="p300_single", tip_rack_slot="1")},
        tip_rack_slot="1",
    )

    # 2. Create driver in simulate mode
    driver = OT2Driver(deck_config=deck, simulate=True)
    connected = await driver.connect()
    print(f"Connected: {connected}")

    # 3. Get initial state
    state = await driver.get_state()
    print(f"Initial state: connected={state.connected}, tip={state.tip_attached}")

    # 4. Execute a pipette transfer: 100uL from A1 -> B1
    action = PipetteAction(
        volume_ul=100.0,
        source_well="A1",
        dest_well="B1",
        source_labware="source_plate",
        dest_labware="dest_plate",
    )
    result = await driver.execute(action)
    print(f"Result: success={result.success}, status={result.status}")
    print(f"Measurements: {result.measurements}")
    print(f"Duration: {result.duration_s}s")

    # 5. Check state after
    state = await driver.get_state()
    print(f"After state: tip={state.tip_attached}, volume={state.current_volume_ul}uL")

    # 6. Disconnect
    await driver.disconnect()
    state = await driver.get_state()
    print(f"Disconnected: connected={state.connected}")


if __name__ == "__main__":
    asyncio.run(main())
