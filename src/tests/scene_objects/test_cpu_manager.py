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

    def test_select_free_cpu_with_hyperthreading(self, cpu_config_hyperthreading, create_process):
        cpu_manager = CpuManager(cpu_config_hyperthreading)
        cpu_manager.setup()

        process1 = create_process(cpu_manager, 1)
        process2 = create_process(cpu_manager, 2)
        process3 = create_process(cpu_manager, 3)
        process4 = create_process(cpu_manager, 4)
        process5 = create_process(cpu_manager, 5)
        process6 = create_process(cpu_manager, 6)
        process7 = create_process(cpu_manager, 7)
        process8 = create_process(cpu_manager, 8)

        cpu1_1 = cpu_manager.get_cpu_by_logical_id(1)
        cpu1_2 = cpu_manager.get_cpu_by_logical_id(2)
        cpu2_1 = cpu_manager.get_cpu_by_logical_id(3)
        cpu2_2 = cpu_manager.get_cpu_by_logical_id(4)
        cpu3_1 = cpu_manager.get_cpu_by_logical_id(5)
        cpu3_2 = cpu_manager.get_cpu_by_logical_id(6)
        cpu4_1 = cpu_manager.get_cpu_by_logical_id(7)
        cpu4_2 = cpu_manager.get_cpu_by_logical_id(8)

        cpu = cpu_manager.select_free_cpu()
        assert cpu is cpu1_1

        cpu1_1.process = process1
        cpu = cpu_manager.select_free_cpu()
        assert cpu is cpu2_1

        cpu2_1.process = process2
        cpu4_1.process = process3
        cpu = cpu_manager.select_free_cpu()
        assert cpu is cpu3_1

        cpu3_1.process = process4
        cpu = cpu_manager.select_free_cpu()
        assert cpu is cpu1_2

        cpu1_2.process = process5
        cpu4_2.process = process6
        cpu = cpu_manager.select_free_cpu()
        assert cpu is cpu2_2

        cpu2_2.process = process7
        cpu = cpu_manager.select_free_cpu()
        assert cpu is cpu3_2

        cpu3_2.process = process8
        cpu = cpu_manager.select_free_cpu()
        assert cpu is None

        cpu4_1.process = None
        cpu = cpu_manager.select_free_cpu()
        assert cpu is cpu4_1

    def test_check_cpu_for_penalty_with_no_hyperthreading(self, cpu_config_no_hyperthreading, create_process):
        cpu_manager = CpuManager(cpu_config_no_hyperthreading)
        cpu_manager.setup()

        process = create_process(cpu_manager, 1)

        cpu = cpu_manager.get_cpu_by_logical_id(1)
        assert cpu_manager.check_cpu_for_penalty(cpu) is False

        cpu.process = process
        assert cpu_manager.check_cpu_for_penalty(cpu) is False

    def test_check_cpu_for_penalty_with_hyperthreading(self, cpu_config_hyperthreading, create_process):
        cpu_manager = CpuManager(cpu_config_hyperthreading)
        cpu_manager.setup()

        process1 = create_process(cpu_manager, 1)
        process2 = create_process(cpu_manager, 2)

        cpu1_1 = cpu_manager.get_cpu_by_logical_id(1)
        cpu1_2 = cpu_manager.get_cpu_by_logical_id(2)
        cpu2_1 = cpu_manager.get_cpu_by_logical_id(3)
        cpu2_2 = cpu_manager.get_cpu_by_logical_id(4)

        assert cpu_manager.check_cpu_for_penalty(cpu1_1) is False
        assert cpu_manager.check_cpu_for_penalty(cpu1_2) is False
        assert cpu_manager.check_cpu_for_penalty(cpu2_1) is False
        assert cpu_manager.check_cpu_for_penalty(cpu2_2) is False

        cpu1_1.process = process1
        assert cpu_manager.check_cpu_for_penalty(cpu1_1) is False
        assert cpu_manager.check_cpu_for_penalty(cpu1_2) is False

        cpu1_2.process = process2
        assert cpu_manager.check_cpu_for_penalty(cpu1_1) is True
        assert cpu_manager.check_cpu_for_penalty(cpu1_2) is True
        assert cpu_manager.check_cpu_for_penalty(cpu2_1) is False
        assert cpu_manager.check_cpu_for_penalty(cpu2_2) is False

        cpu1_1.process = None
        assert cpu_manager.check_cpu_for_penalty(cpu1_1) is False
        assert cpu_manager.check_cpu_for_penalty(cpu1_2) is False
        assert cpu_manager.check_cpu_for_penalty(cpu2_1) is False
        assert cpu_manager.check_cpu_for_penalty(cpu2_2) is False

        cpu1_1.process = process1
        assert cpu_manager.check_cpu_for_penalty(cpu1_1) is True
        assert cpu_manager.check_cpu_for_penalty(cpu1_2) is True
        assert cpu_manager.check_cpu_for_penalty(cpu2_1) is False
        assert cpu_manager.check_cpu_for_penalty(cpu2_2) is False

        cpu1_2.process = None
        assert cpu_manager.check_cpu_for_penalty(cpu1_1) is False
        assert cpu_manager.check_cpu_for_penalty(cpu1_2) is False
        assert cpu_manager.check_cpu_for_penalty(cpu2_1) is False
        assert cpu_manager.check_cpu_for_penalty(cpu2_2) is False

    def test_find_cpu_with_process_with_no_hyperthreading(self, cpu_config_no_hyperthreading, create_process):
        cpu_manager = CpuManager(cpu_config_no_hyperthreading)
        cpu_manager.setup()

        process1 = create_process(cpu_manager, 1)
        process2 = create_process(cpu_manager, 2)

        cpu1 = cpu_manager.get_cpu_by_logical_id(1)
        cpu4 = cpu_manager.get_cpu_by_logical_id(4)

        assert cpu_manager.find_cpu_with_process(process1) is None
        assert cpu_manager.find_cpu_with_process(process2) is None

        cpu1.process = process1
        assert cpu_manager.find_cpu_with_process(process1) is cpu1
        assert cpu_manager.find_cpu_with_process(process2) is None

        cpu4.process = process2
        assert cpu_manager.find_cpu_with_process(process1) is cpu1
        assert cpu_manager.find_cpu_with_process(process2) is cpu4

    def test_find_cpu_with_process_with_hyperthreading(self, cpu_config_hyperthreading, create_process):
        cpu_manager = CpuManager(cpu_config_hyperthreading)
        cpu_manager.setup()

        process1 = create_process(cpu_manager, 1)
        process2 = create_process(cpu_manager, 2)

        cpu1_1 = cpu_manager.get_cpu_by_logical_id(1)
        cpu2_2 = cpu_manager.get_cpu_by_logical_id(4)

        assert cpu_manager.find_cpu_with_process(process1) is None
        assert cpu_manager.find_cpu_with_process(process2) is None

        cpu1_1.process = process1
        assert cpu_manager.find_cpu_with_process(process1) is cpu1_1
        assert cpu_manager.find_cpu_with_process(process2) is None

        cpu2_2.process = process2
        assert cpu_manager.find_cpu_with_process(process1) is cpu1_1
        assert cpu_manager.find_cpu_with_process(process2) is cpu2_2

    def test_remove_process_from_cpu_with_no_hyperthreading(self, cpu_config_no_hyperthreading, create_process):
        cpu_manager = CpuManager(cpu_config_no_hyperthreading)
        cpu_manager.setup()

        process = create_process(cpu_manager, 1)

        cpu = cpu_manager.get_cpu_by_logical_id(1)
        cpu.process = process
        cpu_manager.remove_process_from_cpu(process)
        assert cpu.process is None
        cpu_manager.remove_process_from_cpu(process)
        assert cpu.process is None

    def test_remove_process_from_cpu_with_hyperthreading(self, cpu_config_hyperthreading, create_process):
        cpu_manager = CpuManager(cpu_config_hyperthreading)
        cpu_manager.setup()

        process1 = create_process(cpu_manager, 1)
        process2 = create_process(cpu_manager, 2)

        cpu1_1 = cpu_manager.get_cpu_by_logical_id(1)
        cpu1_2 = cpu_manager.get_cpu_by_logical_id(2)

        cpu1_1.process = process1
        cpu1_2.process = process2

        cpu_manager.remove_process_from_cpu(process1)
        assert cpu1_1.process is None
        assert cpu1_2.process is process2

        cpu_manager.remove_process_from_cpu(process1)
        assert cpu1_1.process is None
        assert cpu1_2.process is process2

        cpu_manager.remove_process_from_cpu(process2)
        assert cpu1_1.process is None
        assert cpu1_2.process is None

        cpu_manager.remove_process_from_cpu(process2)
        assert cpu1_1.process is None
        assert cpu1_2.process is None
        