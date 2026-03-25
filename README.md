[![CI](https://github.com/labclaw/lab-robot/actions/workflows/ci.yml/badge.svg)](https://github.com/labclaw/lab-robot/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](https://github.com/labclaw/lab-robot)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

# lab-robot

Physical Execution Interface for science labs — connect AI brains to robot bodies.

Part of the [LabClaw](https://github.com/labclaw/labclaw) ecosystem.

## Why lab-robot?

Science labs need to run experiments physically, not just plan them in software. lab-robot
provides a unified driver layer that lets AI agents execute real-world lab operations —
pipetting, plate handling, incubation — across different robot hardware through a single
protocol. No more writing throwaway scripts for each new machine.

## Features

- **Unified PEI Protocol** — abstract robot actions into hardware-agnostic primitives (motion, lab-ops, perception, system)
- **Rich ActionResult** — every action returns structured results with measurements, state changes, and error details
- **Safety-First** — chain-of-responsibility safety guards (force limits, workspace bounds, collision detection) at CRITICAL level by default
- **Async-Native** — built on Python async for concurrent robot orchestration
- **Typed & Validated** — full Pydantic 2.x schemas and PEP 561 type markers
- **Extensible** — add new robots by implementing the `RobotDriver` protocol

## Supported Robots

| Robot | Status | Mode |
|-------|--------|------|
| Opentrons OT-2 | Active development | Simulate |

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

## Adding a New Robot

1. Copy `robots/_robot_template/` to `robots/<your_robot>/`
2. Implement the `RobotDriver` protocol (`connect`, `disconnect`, `execute`, `stop`, `capabilities`)
3. Add your package to `pyproject.toml` optional dependencies

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide.

## Ecosystem

```
labclaw (orchestration)
├── lab-robot   ← you are here (physical execution)
├── device-use  (GUI & visual interaction)
└── device-skills (device drivers & skills)
```

lab-robot is the **Physical Execution Interface (PEI)** — Layer 1 of the LabClaw stack.
It translates high-level lab operations into hardware-specific commands.

## Architecture

See [PEI Specification](docs/pei-spec.md) for the full protocol design.

## Roadmap

- **Phase 0** — Opentrons OT-2 simulate mode (current)
- **Phase 1** — OT-2 real hardware + safety guards
- **Phase 2** — Multi-robot orchestration + perception layer

## Citation

If you use lab-robot in your research, please cite:

```bibtex
@software{labclaw_lab_robot,
  author    = {LabClaw Team},
  title     = {lab-robot: Physical Execution Interface for Science Labs},
  year      = {2026},
  url       = {https://github.com/labclaw/lab-robot},
  license   = {Apache-2.0}
}
```

## License

Apache 2.0
