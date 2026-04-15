from engine.modal import Modal
from scene_objects.button import Button
from scene_objects.views.hotkey_dialog_view import HokeyDialogView


class HokeyDialog(Modal):

    def __init__(self):
        super().__init__(HokeyDialogView(self))

        self._close_button = Button('Close', self.close)
        self.children.append(self._close_button)

    def update(self, current_time, events):
        self._close_button.view.set_xy(
            self.view.x + (self.view.width -
                           self._close_button.view.width) / 2,
            self.view.y + self.view.height - self._close_button.view.height - 40
        )

        for child in self.children:
            child.update(current_time, events)
