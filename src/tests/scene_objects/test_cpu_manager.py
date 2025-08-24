import pytest

from config.cpu_config import CpuConfig
from scene_objects.cpu_manager import CpuManager

class TestCPUManager:
    @pytest.fixture
    def cpu_config_no_hyperthreading(self):
        return CpuConfig(
            num_cores=4,
            num_threads_per_core=1,
            process_happiness_ms=5000,
            penalty_ms=0,
        )

    @pytest.fixture
    def cpu_config_hyperthreading(self):
        return CpuConfig(
            num_cores=4,
            num_threads_per_core=2,
            process_happiness_ms=5000,
            penalty_ms=1000,
        )

    def test_get_cpu_no_hyperthreading(self, cpu_config_no_hyperthreading):
        cpu_manager = CpuManager(cpu_config_no_hyperthreading)
        cpu_manager.setup()

        assert cpu_manager.get_cpu_by_logical_id(1).physical_id == 1
        assert cpu_manager.get_cpu_by_logical_id(1).logical_id == 1
        assert cpu_manager.get_cpu_by_logical_id(2).physical_id == 2
        assert cpu_manager.get_cpu_by_logical_id(2).logical_id == 2
        assert cpu_manager.get_cpu_by_logical_id(3).physical_id == 3
        assert cpu_manager.get_cpu_by_logical_id(3).logical_id == 3
        assert cpu_manager.get_cpu_by_logical_id(4).physical_id == 4
        assert cpu_manager.get_cpu_by_logical_id(4).logical_id == 4
        assert cpu_manager.get_cpu_by_logical_id(5) is None

    def test_get_cpu_hyperthreading(self, cpu_config_hyperthreading):
        cpu_manager = CpuManager(cpu_config_hyperthreading)
        cpu_manager.setup()

        assert cpu_manager.get_cpu_by_logical_id(1).physical_id == 1
        assert cpu_manager.get_cpu_by_logical_id(1).logical_id == 1
        assert cpu_manager.get_cpu_by_logical_id(2).physical_id == 1
        assert cpu_manager.get_cpu_by_logical_id(2).logical_id == 2
        assert cpu_manager.get_cpu_by_logical_id(3).physical_id == 2
        assert cpu_manager.get_cpu_by_logical_id(3).logical_id == 3
        assert cpu_manager.get_cpu_by_logical_id(4).physical_id == 2
        assert cpu_manager.get_cpu_by_logical_id(4).logical_id == 4
        assert cpu_manager.get_cpu_by_logical_id(5).physical_id == 3
        assert cpu_manager.get_cpu_by_logical_id(5).logical_id == 5
        assert cpu_manager.get_cpu_by_logical_id(6).physical_id == 3
        assert cpu_manager.get_cpu_by_logical_id(6).logical_id == 6
        assert cpu_manager.get_cpu_by_logical_id(7).physical_id == 4
        assert cpu_manager.get_cpu_by_logical_id(7).logical_id == 7
        assert cpu_manager.get_cpu_by_logical_id(8).physical_id == 4
        assert cpu_manager.get_cpu_by_logical_id(8).logical_id == 8
        assert cpu_manager.get_cpu_by_logical_id(9) is None