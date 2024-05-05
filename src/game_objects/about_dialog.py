from engine.game_object import GameObject
from game_objects.button import Button
from game_objects.views.about_dialog_view import AboutDialogView


class AboutDialog(GameObject):

    def __init__(self, close_fn):
        super().__init__(AboutDialogView(self))

        self._close_button = Button('Close', close_fn)
        self.children.append(self._close_button)

    def update(self, current_time, events):
        self._close_button.view.set_xy(
            self.view.x + (self.view.width -
                           self._close_button.view.width) / 2,
            self.view.y + self.view.height - self._close_button.view.height - 40
        )

        for child in self.children:
            child.update(current_time, events)
