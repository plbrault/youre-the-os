from scene_objects.cpu import Cpu
from scene_objects.process import Process
from scene_objects.views.cpu_manager_view import CpuManagerView
from engine.scene_object import SceneObject

class CpuManager(SceneObject):
    def __init__(self, stage_config: 'StageConfig'):
        super().__init__(CpuManagerView(self))

        self._stage_config = stage_config
        self._physical_cores: [[Cpu]] = []

    @property
    def _cpu_list(self):
        return [cpu for core in self._physical_cores for cpu in core]

    def setup(self):
        logical_id = 0
        for i in range(self._stage_config.cpu_config.num_cores):
            physical_id = i + 1
            physical_core = []
            for j in range(self._stage_config.cpu_config.num_threads_for_core[i]):
                logical_id += 1
                logical_core = Cpu(
                    physical_id,
                    logical_id,
                    process_happiness_ms=self._stage_config.cpu_config.process_happiness_ms_for_core[i],
                    penalty_ms=self._stage_config.cpu_config.penalty_ms_for_core[i],
                )
                physical_core.append(logical_core)
            self._physical_cores.append(physical_core)

        for i, cpu in enumerate(self._cpu_list):
            x = 50 + i * cpu.view.width + i * 5
            y = 50
            cpu.view.set_xy(x, y)
        self.children.extend(self._cpu_list)

    def get_cpu_by_logical_id(self, logical_id) -> Cpu | None:
        if logical_id < 1 or logical_id > len(self._cpu_list):
            return None
        return self._cpu_list[logical_id - 1]

    def select_free_cpu(self) -> Cpu | None:
        for cpu in self._cpu_list:
            if not cpu.has_process:
                return cpu
        return None

    def find_cpu_with_process(self, process: Process) -> Cpu | None:
        for cpu in self._cpu_list:
            if cpu.process and cpu.process == process:
                return cpu
        return None

    def remove_process_from_cpu(self, process: Process):
        cpu = self.find_cpu_with_process(process)
        if cpu:
            cpu.process = None

    def get_current_stats(self):
        active_process_count_by_starvation_level = [0, 0, 0, 0, 0, 0]
        for cpu in self._cpu_list:
            if cpu.process is not None and not cpu.process.has_ended:
                active_process_count_by_starvation_level[cpu.process.starvation_level] += 1
        return {
            'active_process_count': len([
                cpu for cpu in self._cpu_list
                    if cpu.process is not None and not cpu.process.has_ended
            ]),
            'active_process_count_by_starvation_level': active_process_count_by_starvation_level,
            'blocked_active_process_count': len([
                cpu for cpu in self._cpu_list
                    if cpu.process is not None and cpu.process.is_blocked
            ]),
        }
