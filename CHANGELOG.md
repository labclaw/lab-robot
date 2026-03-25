# Changelog

All notable changes to lab-robot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-03-24

### Added

- PEI (Physical Execution Interface) protocol specification with 4-layer action hierarchy
- `RobotDriver` async protocol: connect, disconnect, execute, stop, capabilities
- `RobotManifest` extending SkillManifest with robot-specific metadata
- `ActionResult` rich result type with success, state, measurements, error detail
- `ActionType` enum with Layer 0 (motion), Layer 1 (lab-ops), Layer 2 (perception), Layer 3 (system)
- `RobotSafetyGuard` chain-of-responsibility safety framework
- `SafetyLevel` enum (CRITICAL, HIGH, MEDIUM, LOW)
- Opentrons OT-2 driver with simulate mode
- Robot driver template for bootstrapping new hardware
- Example usage and quick-start documentation
- Full public API exports in `__init__.py`
- 100% test coverage with pytest
- Ruff linting and formatting configuration
- GitHub Actions CI workflow (Python 3.11, 3.12, 3.13)
- Pre-commit hooks (ruff, check-yaml, check-toml, no-commit-to-branch)
- Security policy and responsible disclosure guidelines
- PR and issue templates
