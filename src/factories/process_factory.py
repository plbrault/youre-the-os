from config.process_config import ProcessConfig
from scene_objects.process import Process, ProcessType
from scene_objects.views.high_priority_process_view import HighPriorityProcessView
from scene_objects.views.low_priority_process_view import LowPriorityProcessView
from engine.random import randint

class ProcessFactory:
    def __init__(self, stage: 'Stage', stage_config: 'StageConfig'):
        self._stage = stage
        self._stage_config = stage_config

        self._standard_process_config = ProcessConfig(
            io_probability=self._stage_config.io_probability,
            graceful_termination_probability=self._stage_config.graceful_termination_probability,
            time_between_starvation_levels_ms=10000,
            max_pages=self._stage_config.max_pages_per_process
        )
        self._high_priority_process_config = ProcessConfig(
            io_probability=self._stage_config.high_priority_process_io_probability,
            graceful_termination_probability=
                self._stage_config.high_priority_process_graceful_termination_probability,
            time_between_starvation_levels_ms=6000,
            max_pages=self._stage_config.max_pages_per_process
        )
        self._low_priority_process_config = ProcessConfig(
            io_probability=self._stage_config.low_priority_process_io_probability,
            graceful_termination_probability=
                self._stage_config.low_priority_process_graceful_termination_probability,
            time_between_starvation_levels_ms=20000,
            max_pages=self._stage_config.max_pages_per_process
        )

    def create_standard_process(self, pid: int, current_time: int = 0):
        return Process(
            pid,
            self._stage,
            self._standard_process_config,
            process_type=ProcessType.STANDARD,
            current_time=current_time
        )

    def create_high_priority_process(self, pid: int, current_time: int = 0):
        return Process(
            pid,
            self._stage,
            self._high_priority_process_config,
            process_type=ProcessType.HIGH_PRIORITY,
            view_class=HighPriorityProcessView,
            current_time=current_time
        )

    def create_low_priority_process(self, pid: int, current_time: int = 0):
        return Process(
            pid,
            self._stage,
            self._low_priority_process_config,
            process_type=ProcessType.LOW_PRIORITY,
            view_class=LowPriorityProcessView,
            current_time=current_time
        )

    def create_random_process(self, pid: int, current_time: int = 0):
        if randint(1, 100) <= int(self._stage_config.high_priority_process_probability * 100):
            return self.create_high_priority_process(pid, current_time=current_time)
        if randint(1, 100) <= int(self._stage_config.low_priority_process_probability * 100):
            return self.create_low_priority_process(pid, current_time=current_time)
        return self.create_standard_process(pid, current_time=current_time)
