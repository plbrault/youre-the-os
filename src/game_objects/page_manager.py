from lib.ui.fonts import FONT_ARIAL_20
from lib.game_object import GameObject
from game_objects.label import Label
from game_objects.views.page_manager_view import PageManagerView
from game_objects.page import Page
from game_objects.page_slot import PageSlot

class PageManager(GameObject):
    _MAX_PAGES= 156
    
    def __init__(self, game):
        self._game = game
        
        self._ram_slots = []
        self._swap_slots = []
        
        super().__init__(PageManagerView(self))
        
        self._setup()
        
    def _setup(self):
        ram_pages_label = Label('Memory Pages in RAM :')
        ram_pages_label.view.set_xy(self._game.process_manager.view.width, 120)
        ram_pages_label.font = FONT_ARIAL_20
        self.children.append(ram_pages_label)
              
        for row in range(4):
            for column in range(12):
                ram_slot = PageSlot()          
                x = self._game.process_manager.view.width + column * ram_slot.view.width + column * 5
                y = 150 + row * ram_slot.view.height + row * 5
                ram_slot.view.set_xy(x, y)
                self._ram_slots.append(ram_slot)
        self.children.extend(self._ram_slots)
        
        swap_pages_label = Label('Memory Pages in Swap Space :')
        swap_pages_label.view.set_xy(self._game.process_manager.view.width, 300)
        swap_pages_label.font = FONT_ARIAL_20
        self.children.append(swap_pages_label)
        
        for row in range(9):
            for column in range(12):
                swap_slot = PageSlot()          
                x = self._game.process_manager.view.width + column * ram_slot.view.width + column * 5
                y = 305 + swap_pages_label.view.height + row * ram_slot.view.height + row * 5
                swap_slot.view.set_xy(x, y)
                self._swap_slots.append(swap_slot)
        self.children.extend(self._swap_slots)        
        
    def create_page(self, pid):
        page = Page(pid, self)
        page_created = False
        for ram_slot in self._ram_slots:
            if not ram_slot.has_page:
                ram_slot.page = page
                page.view.set_xy(ram_slot.view.x, ram_slot.view.y)
                page_created = True
                break
        if not page_created:
            for swap_slot in self._swap_slots:
                if not swap_slot.has_page:
                    swap_slot.page = page
                    page._in_swap = True
                    page.view.set_xy(swap_slot.view.x, swap_slot.view.y)
                    page_created = True
                    break
        self.children.append(page)
        return page
    
    def swap_page(self, page):
        can_swap = False
        if page.in_swap:
            for ram_slot in self._ram_slots:
                if not ram_slot.has_page:
                    can_swap = True
                    break
            if can_swap:
                for swap_slot in self._swap_slots:
                    if swap_slot.page == page:
                        swap_slot.page = None
                        break
                for ram_slot in self._ram_slots:
                    if not ram_slot.has_page:
                        ram_slot.page = page
                        page.view.set_xy(ram_slot.view.x, ram_slot.view.y)
                        break
        else:
            for swap_slot in self._swap_slots:
                if not swap_slot.has_page:
                    can_swap = True
                    break
            if can_swap:
                for ram_slot in self._ram_slots:
                    if ram_slot.page == page:
                        ram_slot.page = None
                        break
                for swap_slot in self._swap_slots:
                    if not swap_slot.has_page:
                        swap_slot.page = page
                        page.view.set_xy(swap_slot.view.x, swap_slot.view.y)
                        break
        page._in_swap = not page._in_swap
    
    def delete_page(self, page):
        for ram_slot in self._ram_slots:
            if ram_slot.page == page:
                ram_slot.page = None
                break
        self.children.remove(page)
