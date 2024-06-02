from game_objects.process import Process
from game_objects.views.high_priority_process_view import HighPriorityProcessView

class HighPriorityProcess(Process):
    def __init__(self, pid, stage):
        super().__init__(pid, stage,
                         time_between_starvation_levels=7000, view_class=HighPriorityProcessView)
