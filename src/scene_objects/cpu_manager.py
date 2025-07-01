from scene_objects.cpu import Cpu
from scene_objects.process import Process
from scene_objects.views.cpu_manager_view import CpuManagerView
from engine.scene_object import SceneObject

class CpuManager(SceneObject):
    def __init__(self, stage_config: 'StageConfig'):
        super().__init__(CpuManagerView(self))

        self._stage_config = stage_config
        self._cpu_list = []

    def setup(self):
        for i in range(self._stage_config.num_cpus):
            self._cpu_list.append(Cpu(i + 1))

        for i, cpu in enumerate(self._cpu_list):
            x = 50 + i * cpu.view.width + i * 5
            y = 50
            cpu.view.set_xy(x, y)
        self.children.extend(self._cpu_list)

    @property
    def cpu_list(self):
        return self._cpu_list

    def find_cpu_with_process(self, process: Process) -> Cpu | None:
        for cpu in self._cpu_list:
            if cpu.process and cpu.process == process:
                return cpu
        return None

    def remove_process_from_cpu(self, process: Process):
        cpu = self.find_cpu_with_process(process)
        if cpu:
            cpu.process = None
        