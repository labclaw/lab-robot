"""RobotManifest — extended schema for robot drivers.

Extends device-skills' SkillManifest pattern but as a standalone model
(no import dependency on device-skills for now — keeps lab-robot
independently installable).
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class RobotCategory(StrEnum):
    """Robot type classification."""

    LIQUID_HANDLING = "liquid-handling"
    MANIPULATION = "manipulation"
    TRANSPORT = "transport"
    MOBILE_MANIPULATOR = "mobile-manipulator"


class RobotSafetyLevel(StrEnum):
    """Safety classification — defaults to CRITICAL for all robots."""

    NORMAL = "normal"
    STRICT = "strict"
    CRITICAL = "critical"


class RobotCapabilities(BaseModel):
    """Physical capabilities of a robot."""

    degrees_of_freedom: int = Field(default=0, ge=0)
    payload_kg: float = Field(default=0.0, ge=0)
    repeatability_mm: float = Field(default=0.0, ge=0)
    workspace_volume_mm: tuple[float, float, float] = (0, 0, 0)
    end_effectors: list[str] = Field(default_factory=list)
    safety_features: list[str] = Field(default_factory=list)
    labware_types: list[str] = Field(default_factory=list)


class RobotManifest(BaseModel):
    """Metadata for a robot driver — parsed from skill.yaml.

    Mirrors device-skills' SkillManifest but with robot-specific fields.
    Safety level defaults to CRITICAL (non-negotiable for physical robots).
    """

    name: str = Field(..., min_length=1)
    version: str = Field(...)
    vendor: str = Field(...)
    category: str = Field(...)
    robot_category: RobotCategory
    model: str = Field(default="")
    description: str = Field(default="")
    platform: str = Field(default="cross")
    control_modes: list[str] = Field(default_factory=lambda: ["api"])
    robot_capabilities: RobotCapabilities = Field(default_factory=RobotCapabilities)
    safety_level: RobotSafetyLevel = Field(default=RobotSafetyLevel.CRITICAL)
    dependencies: list[str] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name must not be empty")
        return v
