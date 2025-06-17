from config.page_config import PageConfig
from game_objects.page import Page

class PageFactory: # pylint: disable=too-few-public-methods
    def __init__(self, stage: 'Stage', stage_config: 'StageConfig'):
        self._stage = stage
        self._stage_config = stage_config
        self._page_config = PageConfig(
            swap_delay_ms=stage_config.swap_delay_ms,
            parallel_swaps=stage_config.parallel_swaps
        )

    def create_page(self, pid: int, idx: int):
        return Page(
            pid=pid,
            idx=idx,
            page_manager=self._stage.page_manager,
            config=self._page_config
        )
