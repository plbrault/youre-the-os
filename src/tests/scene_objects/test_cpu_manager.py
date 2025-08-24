import pytest

from config.cpu_config import CpuConfig
from config.stage_config import StageConfig
from factories.process_factory import ProcessFactory
from scene_objects.cpu_manager import CpuManager
from scene_objects.process_manager import ProcessManager
from scenes.stage import Stage

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

    @pytest.fixture
    def create_process(self, monkeypatch):
        stage_config = StageConfig()
        stage = Stage('test_stage', stage_config)

        the_cpu_manager = None
        def get_cpu_manager(self):
            return the_cpu_manager
        monkeypatch.setattr(ProcessManager, 'cpu_manager', property(get_cpu_manager))

        process_factory = ProcessFactory(stage, stage_config)
        process_manager = ProcessManager(stage, stage_config)
        monkeypatch.setattr(Stage, 'process_manager', process_manager)

        def create_process_fn(cpu_manager, pid: int):
            the_cpu_manager = cpu_manager
            return process_factory.create_standard_process(pid)
        return create_process_fn

    def test_get_cpu_with_no_hyperthreading(self, cpu_config_no_hyperthreading):
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

    def test_get_cpu_with_hyperthreading(self, cpu_config_hyperthreading):
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

    def test_select_free_cpu_with_no_hyperthreading(self, cpu_config_no_hyperthreading, create_process):
        cpu_manager = CpuManager(cpu_config_no_hyperthreading)
        cpu_manager.setup()

        process1 = create_process(cpu_manager, 1)
        process2 = create_process(cpu_manager, 2)
        process3 = create_process(cpu_manager, 3)
        process4 = create_process(cpu_manager, 4)

        cpu1 = cpu_manager.get_cpu_by_logical_id(1)
        cpu2 = cpu_manager.get_cpu_by_logical_id(2)
        cpu3 = cpu_manager.get_cpu_by_logical_id(3)
        cpu4 = cpu_manager.get_cpu_by_logical_id(4)

        cpu = cpu_manager.select_free_cpu()
        assert cpu is cpu1

        cpu1.process = process1
        cpu = cpu_manager.select_free_cpu()
        assert cpu is cpu2

        cpu2.process = process2
        cpu4.process = process3
        cpu = cpu_manager.select_free_cpu()
        assert cpu is cpu3

        cpu3.process = process4
        cpu = cpu_manager.select_free_cpu()
        assert cpu is None

        cpu4.process = None
        cpu = cpu_manager.select_free_cpu()
        assert cpu is cpu4
