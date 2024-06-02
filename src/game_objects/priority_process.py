from game_objects.process import Process
from game_objects.views.priority_process_view import PriorityProcessView

class PriorityProcess(Process):
    def __init__(self, pid, stage):
        super().__init__(pid, stage,
                         time_between_starvation_levels=6000, view_class=PriorityProcessView)
