from typing import Optional, Type

from engine.game_object import GameObject
from game_objects.views.page_slot_view import PageSlotView


class PageSlot(GameObject):
    def __init__(self):
        self._page = None
        self._incoming_page = None

        super().__init__(PageSlotView())

    @property
    def page(self) -> Optional[Type['Page']]:
        return self._page

    @page.setter
    def page(self, page: Optional[Type['Page']]):
        self._page = page

    @property
    def incoming_page(self) -> Optional[Type['Page']]:
        return self._incoming_page

    @incoming_page.setter
    def incoming_page(self, page: Optional[Type['Page']]):
        self._incoming_page = page

    @property
    def is_available(self) -> bool:
        return not (self.page or self.incoming_page)

    def update(self, current_time, events):
        pass
