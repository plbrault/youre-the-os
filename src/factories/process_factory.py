from config.process_config import ProcessConfig
from config.stage_config import StageConfig
from game_objects.process import Process
from game_objects.views.priority_process_view import PriorityProcessView

class ProcessFactory:
    def __init__(self, stage: 'Stage', stage_config: StageConfig):
        self._stage = stage
        self._stage_config = stage_config

    def create_standard_process(self, pid: int):
        return Process(
            pid,
            self._stage,
            ProcessConfig(
                io_probability=self._stage_config.io_probability,
                graceful_termination_probability=self._stage_config.graceful_termination_probability,
                time_between_starvation_levels_ms=10000
            )
        )

    def create_priority_process(self, pid: int):
        return Process(
            pid,
            self._stage,
            ProcessConfig(
                io_probability=self._stage_config.io_probability,
                graceful_termination_probability=self._stage_config.graceful_termination_probability,
                time_between_starvation_levels_ms=6000
            ),
            view_class=PriorityProcessView
        )
