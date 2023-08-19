from lib.game_object import GameObject
from game_objects.button import Button
from game_objects.views.in_game_menu_dialog_view import InGameMenuDialogView


class InGameMenuDialog(GameObject):

    def __init__(self, restart_game_fn, main_menu_fn, close_menu_fn):
        super().__init__(InGameMenuDialogView(self))

        self._restartButton = Button('Restart Game', restart_game_fn)
        self._mainMenuButton = Button('Return to Main Menu', main_menu_fn)
        self._closeMenuButton = Button('Close', close_menu_fn)

        self.children.append(self._restartButton)
        self.children.append(self._mainMenuButton)
        self.children.append(self._closeMenuButton)

        self.button_width = self._mainMenuButton.view.width
        self.button_height = self._mainMenuButton.view.height

        self._restartButton.view.min_width = self.button_width
        self._closeMenuButton.view.min_width = self.button_width

    def update(self, current_time, events):
        self._restartButton.view.set_xy(
            self.view.x + (self.view.width -
                           self._restartButton.view.width) / 2,
            self.view.y + 4
        )
        self._mainMenuButton.view.set_xy(
            self.view.x + (self.view.width -
                           self._mainMenuButton.view.width) / 2,
            self._restartButton.view.y + self._restartButton.view.height + 2
        )
        self._closeMenuButton.view.set_xy(
            self.view.x + (self.view.width -
                           self._closeMenuButton.view.width) / 2,
            self._mainMenuButton.view.y + self._mainMenuButton.view.height + 2
        )

        for child in self.children:
            child.update(current_time, events)
