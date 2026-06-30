from config.page_config import PageConfig
from scene_objects.page import Page
from scene_objects.views.page_view import PageView
from scene_objects.views.priority_page_view import PriorityPageView

class PageFactory: # pylint: disable=too-few-public-methods
    def __init__(self, stage: 'Stage', stage_config: 'StageConfig'):
        self._stage = stage
        self._stage_config = stage_config
        self._page_config = PageConfig(
            swap_delay_ms=stage_config.swap_delay_ms,
            parallel_swaps=stage_config.parallel_swaps
        )

    def create_page(self, pid: int, idx: int, is_priority: bool = False):
        return Page(
            pid=pid,
            idx=idx,
            page_manager=self._stage.page_manager,
            config=self._page_config,
            view_class=PriorityPageView if is_priority else PageView
        )
