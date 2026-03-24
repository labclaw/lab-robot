# CLAUDE.md — lab-robot

## Project Overview

Physical Execution Interface (PEI) for science labs. Connects LabClaw's AI brain
to physical robot hardware. Phase 0: Opentrons OT-2 driver (simulate mode).

**Tech stack:** Python 3.11+, Pydantic 2.x, opentrons SDK, hatchling
**Ecosystem role:** LabClaw Layer 1 — physical execution (alongside device-use for GUI)

## Build & Test

pip install -e ".[dev,opentrons]"
make test
make lint

## Architecture

- `src/lab_robot/` — core library (PEI protocol, types, safety)
- `robots/` — per-robot driver packages (like device-skills' devices/)
- RobotDriver Protocol: connect, disconnect, execute, stop, capabilities
- Actions return rich ActionResult (not just bool)
- Safety level defaults to CRITICAL for all robots

## Code Style

Same as device-skills: ruff (E,F,I,N,W,UP), line-length 100, type hints required,
`from __future__ import annotations` in every module, Pydantic for all schemas.
100% test coverage enforced.

## Key Abstractions

- `RobotDriver` — async Protocol for robot hardware (execute actions, not read data)
- `RobotManifest` — extends SkillManifest with robot-specific fields
- `ActionResult` — rich result with success, state, measurements, error detail
- `RobotSafetyGuard` — chain-of-responsibility safety (planned: force, workspace, collision)
- PEI primitives: Layer 0 (motion), Layer 1 (lab-ops), Layer 2 (perception), Layer 3 (system)
