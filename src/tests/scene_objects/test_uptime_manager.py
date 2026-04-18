import pytest

from constants import ONE_SECOND
from scene_objects.uptime_manager import UptimeManager


class TestUptimeManager:
    def test_uptime_starts_at_zero(self):
        manager = UptimeManager()

        assert manager.uptime_ms == 0
        assert manager.uptime_text == '0:00:00'

    def test_first_update_does_not_increment_uptime(self):
        manager = UptimeManager()
        manager.update(5000, [])

        assert manager.uptime_ms == 0
        assert manager.uptime_text == '0:00:00'

    def test_uptime_increments_after_one_second(self):
        manager = UptimeManager()
        manager.update(0, [])
        manager.update(ONE_SECOND, [])

        assert manager.uptime_ms == ONE_SECOND

    def test_uptime_does_not_increment_before_one_second(self):
        manager = UptimeManager()
        manager.update(0, [])
        manager.update(500, [])

        assert manager.uptime_ms == 0

    def test_first_update_at_large_time_does_not_cause_spike(self):
        manager = UptimeManager()
        manager.update(100000, [])

        assert manager.uptime_ms == 0

    def test_uptime_after_first_update_increments_normally(self):
        manager = UptimeManager()
        manager.update(100000, [])
        manager.update(100000 + ONE_SECOND, [])

        assert manager.uptime_ms == ONE_SECOND

    def test_uptime_text_format(self):
        manager = UptimeManager()
        manager.update(0, [])
        manager.update(ONE_SECOND, [])

        assert manager.uptime_text == '0:00:01'

    def test_uptime_resets_with_new_instance(self):
        manager = UptimeManager()
        manager.update(0, [])
        manager.update(ONE_SECOND, [])

        assert manager.uptime_ms == ONE_SECOND

        new_manager = UptimeManager()
        new_manager.update(50000, [])

        assert new_manager.uptime_ms == 0