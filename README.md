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
from lab_robot.types import PipetteAction
from robots.opentrons_ot2.driver import OT2Driver

driver = OT2Driver(simulate=True)
await driver.connect()
result = await driver.execute(PipetteAction(
    volume_ul=30.0,
    source_well="A1",
    dest_well="B1",
))
print(result)  # ActionResult(success=True, ...)
await driver.disconnect()
```

## Architecture

See [PEI Specification](docs/pei-spec.md) for the full protocol design.

## License

Apache 2.0
