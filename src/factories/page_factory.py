from config.page_config import PageConfig
from scene_objects.page import Page
from scene_objects.process import ProcessType
from scene_objects.views.page_view import PageView
from scene_objects.views.high_priority_page_view import HighPriorityPageView
from scene_objects.views.low_priority_page_view import LowPriorityPageView

class PageFactory: # pylint: disable=too-few-public-methods
    _view_class_by_process_type = {
        ProcessType.STANDARD: PageView,
        ProcessType.HIGH_PRIORITY: HighPriorityPageView,
        ProcessType.LOW_PRIORITY: LowPriorityPageView,
    }

    def __init__(self, stage: 'Stage', stage_config: 'StageConfig'):
        self._stage = stage
        self._stage_config = stage_config
        self._page_config = PageConfig(
            swap_delay_ms=stage_config.swap_delay_ms,
            parallel_swaps=stage_config.parallel_swaps
        )

    def create_page(self, pid: int, idx: int,
                    process_type: ProcessType = ProcessType.STANDARD):
        return Page(
            pid=pid,
            idx=idx,
            page_manager=self._stage.page_manager,
            config=self._page_config,
            view_class=self._view_class_by_process_type[process_type]
        )
