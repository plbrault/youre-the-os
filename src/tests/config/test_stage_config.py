import pytest

from config.stage_config import StageConfig
from config.cpu_config import CpuConfig

class TestStageConfig:
    def test_priority_process_io_probability_defaults_to_io_probability(self):
        config = StageConfig()

        assert config.priority_process_io_probability == config.io_probability

    def test_priority_process_io_probability_default_value(self):
        config = StageConfig()

        assert config.priority_process_io_probability == 0.01

    def test_priority_process_io_probability_explicit_value(self):
        config = StageConfig(
            io_probability=0.05,
            priority_process_io_probability=0.1,
        )

        assert config.priority_process_io_probability == 0.1
        assert config.io_probability == 0.05

    def test_priority_process_io_probability_none_defaults_to_io_probability(self):
        config = StageConfig(
            io_probability=0.05,
            priority_process_io_probability=None,
        )

        assert config.priority_process_io_probability == 0.05