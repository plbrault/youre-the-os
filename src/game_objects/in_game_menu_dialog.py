from engine.game_object import GameObject
from game_objects.button import Button
from game_objects.views.in_game_menu_dialog_view import InGameMenuDialogView


class InGameMenuDialog(GameObject):

    def __init__(self, restart_game_fn, main_menu_fn, close_menu_fn):
        super().__init__(InGameMenuDialogView(self))

        self._restart_button = Button('Restart Game', restart_game_fn)
        self._main_menu_button = Button('Return to Main Menu', main_menu_fn)
        self._close_menu_button = Button('Close', close_menu_fn, key_bind='escape')

        self.children.append(self._restart_button)
        self.children.append(self._main_menu_button)
        self.children.append(self._close_menu_button)

        self.button_width = self._main_menu_button.view.width
        self.button_height = self._main_menu_button.view.height

        self._restart_button.view.min_width = self.button_width
        self._close_menu_button.view.min_width = self.button_width

    @property
    def restart_button(self):
        return self._restart_button

    @property
    def main_menu_button(self):
        return self._main_menu_button

    @property
    def close_menu_button(self):
        return self._close_menu_button

    def update(self, current_time, events):
        for child in self.children:
            child.update(current_time, events)
