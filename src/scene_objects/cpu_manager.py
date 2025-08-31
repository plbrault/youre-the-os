from scene_objects.cpu import Cpu
from scene_objects.process import Process
from scene_objects.views.cpu_manager_view import CpuManagerView
from engine.scene_object import SceneObject

class CpuManager(SceneObject):
    def __init__(self, cpu_config: 'CpuConfig'):
        super().__init__(CpuManagerView(self))

        self._cpu_config = cpu_config
        self._physical_cores: [[Cpu]] = []

    @property
    def _cpu_list(self):
        return [cpu for core in self._physical_cores for cpu in core]

    def setup(self):
        logical_id = 0
        for i in range(self._cpu_config.num_cores):
            physical_id = i + 1
            physical_core = []
            for j in range(self._cpu_config.num_threads_for_core[i]):
                logical_id += 1
                logical_core = Cpu(
                    physical_id,
                    logical_id,
                    self,
                    core_type=self._cpu_config.type_for_core[i],
                    process_happiness_ms=self._cpu_config.process_happiness_ms_for_core[i],
                    penalty_ms=self._cpu_config.penalty_ms_for_core[i],
                )
                physical_core.append(logical_core)
            self._physical_cores.append(physical_core)

        x = 50
        y = 50
        for i, physical_core in enumerate(self._physical_cores):
            for j, logical_core in enumerate(physical_core):
                logical_core.view.set_xy(x, y)
                x += logical_core.view.width + 5
                if j == len(physical_core) - 1 and len(physical_core) > 1:
                    x += 15

        self.children.extend(self._cpu_list)

    def get_cpu_by_logical_id(self, logical_id) -> Cpu | None:
        if logical_id < 1 or logical_id > len(self._cpu_list):
            return None
        return self._cpu_list[logical_id - 1]

    def select_free_cpu(self) -> Cpu | None:
        max_num_threads = max(
            self._cpu_config.num_threads_for_core
        )
        for thread_index in range(max_num_threads):
            for physical_core in self._physical_cores:
                if thread_index < len(physical_core):
                    cpu = physical_core[thread_index]
                    if not cpu.has_process:
                        return cpu
        return None

    def check_cpu_for_penalty(self, cpu: Cpu) -> bool:
        return len([
            core for core in
            self._physical_cores[cpu.physical_id - 1]
            if core.has_process
        ]) > 1

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

    @property
    def view_vars(self):
        physical_core_rectangles = []
        for physical_core in self._physical_cores:
            if len(physical_core) > 1:
                rectangle_x = physical_core[0].view.x - 4
                rectangle_y = physical_core[0].view.y - 4
                rectangle_width = sum(cpu.view.width for cpu in physical_core) + 13
                rectangle_height = physical_core[0].view.height + 8
                rectangle = {
                    'x': rectangle_x,
                    'y': rectangle_y,
                    'width': rectangle_width,
                    'height': rectangle_height,
                }
                physical_core_rectangles.append(rectangle)
        return {
            'physical_core_rectangles': physical_core_rectangles,
        }
