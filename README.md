# lab-robot

Physical Execution Interface for science labs — connect AI brains to robot bodies.

Part of the [LabClaw](https://github.com/labclaw/labclaw) ecosystem.

## Install

```bash
pip install lab-robot                    # core only
pip install lab-robot[opentrons]         # + Opentrons OT-2 driver
```

## Quick Start

```python
import asyncio
from lab_robot.types import PipetteAction
from robots.opentrons_ot2 import OT2Driver
from robots.opentrons_ot2.models import OT2DeckConfig, PipetteConfig, PipetteMount, LabwareConfig

# Configure the OT-2 deck layout
deck = OT2DeckConfig(
    slots={"1": LabwareConfig(labware_type="nest_96_wellplate_200ul_flat")},
    pipette_left=PipetteConfig(
        name="p300_single", mount=PipetteMount.LEFT, max_volume_ul=300,
        tip_rack_slots=["2"],
    ),
)

async def main():
    driver = OT2Driver(deck_config=deck, simulate=True)
    await driver.connect()
    result = await driver.execute(PipetteAction(
        volume_ul=30.0,
        source_well="A1",
        dest_well="B1",
    ))
    print(result)  # ActionResult(success=True, ...)
    await driver.disconnect()

asyncio.run(main())
```

## Architecture

See [PEI Specification](docs/pei-spec.md) for the full protocol design.

## License

Apache 2.0
