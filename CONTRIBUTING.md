# Contributing to lab-robot

## Setup

```bash
git clone https://github.com/labclaw/lab-robot.git
cd lab-robot
pip install -e ".[dev,opentrons]"
```

Run tests and lint:

```bash
make test
make lint
```

## Adding a New Robot

1. Copy `robots/_robot_template/` to `robots/<robot_name>/`
2. Implement `RobotDriver` protocol methods: `connect`, `disconnect`, `execute`, `stop`
3. Define supported `ActionType`s and deck/hardware config models
4. Add tests in `robots/<robot_name>/tests/` — 100% coverage required
5. Export the driver class from `robots/<robot_name>/__init__.py`

## Code Style

- **Linter:** ruff with rules E, F, I, N, W, UP (line-length 100)
- **Type hints:** required on all public functions
- **Imports:** `from __future__ import annotations` in every module
- **Schemas:** Pydantic BaseModel for all data structures
- **Coverage:** 100% enforced — CI will fail otherwise

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(scope): add Hamilton STAR driver
fix(ot2): handle missing tip rack gracefully
test(core): add ActionResult edge case tests
docs: update CONTRIBUTING.md
```

Scope is the module or robot name. One logical change per commit.
