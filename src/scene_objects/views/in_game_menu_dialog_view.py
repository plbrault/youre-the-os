from engine.modal_view import ModalView

class InGameMenuDialogView(ModalView):
    def __init__(self, in_game_menu_dialog):
        self._in_game_menu_dialog = in_game_menu_dialog
        super().__init__()

    @ModalView.x.setter
    def x(self, value):
        self._x = value
        self._in_game_menu_dialog.restart_button.view.x = self.x + (
            self.width - self._in_game_menu_dialog.restart_button.view.width
        ) / 2
        self._in_game_menu_dialog.main_menu_button.view.x = self.x + (
            self.width - self._in_game_menu_dialog.main_menu_button.view.width
        ) / 2
        self._in_game_menu_dialog.close_menu_button.view.x = self.x + (
            self.width - self._in_game_menu_dialog.close_menu_button.view.width
        ) / 2

    @ModalView.y.setter
    def y(self, value):
        self._y = value
        y = self.y + 4
        self._in_game_menu_dialog.restart_button.view.y = y
        y += self._in_game_menu_dialog.restart_button.view.height + 2
        self._in_game_menu_dialog.main_menu_button.view.y = y
        y += self._in_game_menu_dialog.main_menu_button.view.height + 2
        self._in_game_menu_dialog.close_menu_button.view.y = y

    @property
    def width(self):
        return self._in_game_menu_dialog.button_width + 8

    @property
    def height(self):
        return 3 * self._in_game_menu_dialog.button_height + 12

    def draw_content(self, surface):
        pass
