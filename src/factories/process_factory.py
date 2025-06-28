from config.process_config import ProcessConfig
from scene_objects.process import Process
from scene_objects.views.priority_process_view import PriorityProcessView
from engine.random import randint

class ProcessFactory:
    def __init__(self, stage: 'Stage', stage_config: 'StageConfig'):
        self._stage = stage
        self._stage_config = stage_config

        self._standard_process_config = ProcessConfig(
            io_probability=self._stage_config.io_probability,
            graceful_termination_probability=self._stage_config.graceful_termination_probability,
            time_between_starvation_levels_ms=10000
        )
        self._priority_process_config = ProcessConfig(
            io_probability=self._stage_config.io_probability,
            graceful_termination_probability=self._stage_config.graceful_termination_probability,
            time_between_starvation_levels_ms=6000
        )

    def create_standard_process(self, pid: int):
        return Process(
            pid,
            self._stage,
            self._standard_process_config
        )

    def create_priority_process(self, pid: int):
        return Process(
            pid,
            self._stage,
            self._priority_process_config,
            view_class=PriorityProcessView
        )

    def create_random_process(self, pid: int):
        if randint(1, 100) <= int(self._stage_config.priority_process_probability * 100):
            return self.create_priority_process(pid)
        return self.create_standard_process(pid)
