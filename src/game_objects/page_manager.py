from lib.game_object import GameObject
from game_objects.views.page_manager_view import PageManagerView
from game_objects.page import Page
from game_objects.page_slot import PageSlot

class PageManager(GameObject):
    _TOTAL_ROWS = 11
    
    def __init__(self, game):
        self._game = game
        
        self._ram_slots = []
        self._swap_slots = []
        
        self._pages_in_ram_label_xy = (0,0)
        self._swap_is_enabled = True
        self._pages_in_swap_label_xy = None
        
        super().__init__(PageManagerView(self))

    @property
    def pages_in_ram_label_xy(self):
        return self._pages_in_ram_label_xy
    
    @property
    def pages_in_swap_label_xy(self):
        return self._pages_in_swap_label_xy
               
    def setup(self):        
        self._pages_in_ram_label_xy = (self._game.process_manager.view.width, 120)
        
        num_ram_rows = self._game.config['num_ram_rows']
        num_swap_rows = self._TOTAL_ROWS - num_ram_rows
        
        num_cols = 16
             
        for row in range(num_ram_rows):
            for column in range(num_cols):
                ram_slot = PageSlot()          
                x = self._game.process_manager.view.width + column * ram_slot.view.width + column * 5
                y = 155 + row * ram_slot.view.height + row * 5
                ram_slot.view.set_xy(x, y)
                self._ram_slots.append(ram_slot)
        self.children.extend(self._ram_slots)
        
        if num_swap_rows > 0:
            self._pages_in_swap_label_xy = (self._game.process_manager.view.width, 164 + num_ram_rows * PageSlot().view.height + num_ram_rows * 5)
            
            for row in range(num_swap_rows):
                for column in range(num_cols):
                    swap_slot = PageSlot()          
                    x = self._game.process_manager.view.width + column * ram_slot.view.width + column * 5
                    y = self._pages_in_swap_label_xy[1] + 35 + row * ram_slot.view.height + row * 5
                    swap_slot.view.set_xy(x, y)
                    self._swap_slots.append(swap_slot)
            self.children.extend(self._swap_slots)
        else:
            self._swap_is_enabled = False
        
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
                page._in_swap = False
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
                page._in_swap = True
    
    def delete_page(self, page):
        for ram_slot in self._ram_slots:
            if ram_slot.page == page:
                ram_slot.page = None
                break
        self.children.remove(page)
