"""Tests for template robot driver — placeholder.

Copy this file when creating a new robot driver and replace with real tests.
"""

from __future__ import annotations

import pytest

from robots._robot_template.driver import TemplateRobotDriver


class TestTemplateRobotDriver:
    def test_all_methods_raise_not_implemented(self) -> None:
        driver = TemplateRobotDriver()
        with pytest.raises(NotImplementedError):
            driver.capabilities()

    async def test_connect_raises_not_implemented(self) -> None:
        driver = TemplateRobotDriver()
        with pytest.raises(NotImplementedError):
            await driver.connect()

    async def test_disconnect_raises_not_implemented(self) -> None:
        driver = TemplateRobotDriver()
        with pytest.raises(NotImplementedError):
            await driver.disconnect()

    async def test_stop_raises_not_implemented(self) -> None:
        driver = TemplateRobotDriver()
        with pytest.raises(NotImplementedError):
            await driver.stop()

    async def test_get_state_raises_not_implemented(self) -> None:
        driver = TemplateRobotDriver()
        with pytest.raises(NotImplementedError):
            await driver.get_state()
