# PEI Protocol Specification

**Physical Execution Interface (PEI)** — the async protocol for connecting
AI orchestrators to physical robot hardware in science labs.

Version: 0.1.0 | Status: Draft

---

## 1. Layer Model

PEI organizes robot actions into four layers:

| Layer | Name       | Actions                              | Description                        |
|-------|------------|--------------------------------------|------------------------------------|
| 0     | Motion     | move, grip, release, home            | Raw kinematic primitives           |
| 1     | Lab-Ops    | pipette, transfer_labware, dispense  | Domain-specific lab operations     |
| 2     | Perception | detect_labware, verify_state, calibrate | Sensor and vision feedback      |
| 3     | System     | recover, emergency_stop, wait_condition | Error recovery and coordination |

Drivers implement only the layers they support. A liquid handler (OT-2) implements
Layer 1 actions but not Layer 0 motion primitives directly. A mobile manipulator
might implement all four layers.

## 2. RobotDriver Protocol

Every robot driver must implement this async interface:

```python
class RobotDriver(Protocol):
    async def connect(self, config: dict | None = None) -> bool
    async def disconnect(self) -> None
    async def execute(self, action: RobotAction) -> ActionResult
    async def stop(self) -> None
    async def get_state(self) -> RobotState
    def capabilities(self) -> list[ActionType]
```

### Method Contracts

- **connect()** — Initialize hardware or simulator. Returns `True` on success.
  Config dict is driver-specific (IP address, serial port, etc.).
- **disconnect()** — Release resources. Idempotent — safe to call multiple times.
- **execute()** — Run a single action. Must check `connected` state internally.
  Returns `ActionResult` with measurements, timing, and state snapshot.
- **stop()** — Emergency halt. Must be fast (no cleanup, no graceful shutdown).
  After stop, driver is in disconnected state.
- **get_state()** — Non-mutating query of current robot state.
- **capabilities()** — Synchronous. Returns the `ActionType` values this driver handles.

## 3. ActionResult Contract

Every `execute()` call returns an `ActionResult`:

```python
class ActionResult(BaseModel):
    success: bool
    status: ActionStatus          # COMPLETED | FAILED | CANCELLED
    action_type: ActionType
    measurements: dict[str, Any]  # e.g. {"volume_dispensed_ul": 100.0}
    state_after: dict[str, Any]   # robot state snapshot post-action
    error: str                    # REQUIRED when success=False
    duration_s: float             # wall-clock execution time
```

Key invariant: **if `success=False`, `error` must be non-empty.** This is enforced
by a Pydantic model validator at construction time.

## 4. Safety Requirements

All robots default to `safety_level: critical`. This is non-negotiable.

**SafetyVerdict** is the shared data contract between safety checkers and the executor:

```python
class SafetyVerdict(BaseModel):
    allowed: bool
    checker: str                  # which checker produced this
    reason: str                   # why it was blocked
    requires_confirmation: bool   # human-in-the-loop gate
```

Built-in safety checks:
- **WorkspaceBounds** — rejects move actions outside defined 3D bounds
- Future: force limits, collision detection, tip presence verification

Safety checkers are composable. The executor runs all applicable checkers before
delegating to the driver. Any single `allowed=False` verdict blocks execution.

## 5. RobotManifest

Each robot directory contains a `skill.yaml` manifest:

```yaml
name: "opentrons-ot2"
version: "0.1.0"
vendor: "Opentrons"
robot_category: "liquid-handling"    # liquid-handling | manipulation | transport | mobile-manipulator
safety_level: "critical"             # always critical for physical robots
robot_capabilities:
  degrees_of_freedom: 3
  repeatability_mm: 0.1
  end_effectors: [single_channel_p300]
  labware_types: [wellplate_96_flat, tiprack_300ul]
```

Parsed into `RobotManifest` (Pydantic model) for runtime validation.

## 6. Integration with LabClaw Orchestrator

lab-robot is one execution backend in the LabClaw ecosystem:

```
labclaw orchestrator
  ├── device-use    (GUI automation — reads instruments)
  ├── lab-robot     (physical execution — moves robots)
  └── lab-manager   (data + API layer)
```

**Boundary rules:**
- `device-use` and `lab-robot` never import each other
- Both register as tools with the orchestrator via capability descriptors
- The orchestrator decides which backend handles each task
- lab-robot actions are physical (pipette, move); device-use actions are digital (click, read)

**Tool registration pattern:**
```python
# Orchestrator registers robot capabilities
capabilities = driver.capabilities()  # [ActionType.PIPETTE]
# Routes PipetteAction to lab-robot, ClickAction to device-use
```

## 7. Reference Implementation: Opentrons OT-2

The OT-2 driver (`robots/opentrons_ot2/`) is the reference PEI implementation.

- Supports `ActionType.PIPETTE` (Layer 1)
- Translates PEI `PipetteAction` into OT-2 protocol commands
- `simulate=True` mode runs with no hardware (default for Phase 0)
- Deck config via `OT2DeckConfig` Pydantic model
- Protocol commands: pick_up_tip, aspirate, dispense, drop_tip

This driver demonstrates the pattern for all future robots:
1. Parse `skill.yaml` into `RobotManifest`
2. Implement `RobotDriver` protocol methods
3. Translate PEI actions into vendor-specific commands
4. Return rich `ActionResult` with measurements and state

## 8. Directory Convention

```
robots/
  _robot_template/     # copy this to start a new robot
    skill.yaml
    driver.py
    SOUL.md            # robot personality for AI context
    MEMORY.md          # calibration and usage history
    tests/
  opentrons_ot2/       # reference implementation
    skill.yaml
    driver.py
    models.py
    protocol_gen.py
    SOUL.md
    MEMORY.md
    tests/
```

Each robot is a self-contained package. The `SOUL.md` gives AI agents context
about the robot's personality and quirks. `MEMORY.md` tracks calibration history.
