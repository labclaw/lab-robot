"""Tests for RobotManifest schema."""

from __future__ import annotations

from lab_robot.schema import RobotCapabilities, RobotCategory, RobotManifest, RobotSafetyLevel


class TestRobotManifest:
    def test_minimal_manifest(self) -> None:
        manifest = RobotManifest(
            name="opentrons-ot2",
            version="0.1.0",
            vendor="Opentrons",
            category="liquid-handling",
            robot_category=RobotCategory.LIQUID_HANDLING,
        )
        assert manifest.name == "opentrons-ot2"
        assert manifest.safety_level == RobotSafetyLevel.CRITICAL  # default for robots

    def test_safety_defaults_to_critical(self) -> None:
        manifest = RobotManifest(
            name="test-robot",
            version="0.1.0",
            vendor="Test",
            category="manipulation",
            robot_category=RobotCategory.MANIPULATION,
        )
        assert manifest.safety_level == RobotSafetyLevel.CRITICAL

    def test_robot_capabilities(self) -> None:
        caps = RobotCapabilities(
            degrees_of_freedom=6,
            payload_kg=0.5,
            repeatability_mm=0.1,
            end_effectors=["single_channel_p300", "single_channel_p20"],
            labware_types=["tiprack_300ul", "wellplate_96"],
        )
        assert caps.degrees_of_freedom == 6
        assert len(caps.end_effectors) == 2

    def test_manifest_with_capabilities(self) -> None:
        manifest = RobotManifest(
            name="arx5-lab",
            version="0.1.0",
            vendor="ARX Robotics",
            category="manipulation",
            robot_category=RobotCategory.MANIPULATION,
            robot_capabilities=RobotCapabilities(
                degrees_of_freedom=6,
                payload_kg=5.0,
            ),
        )
        assert manifest.robot_capabilities.degrees_of_freedom == 6
