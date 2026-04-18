from engine.modal import Modal
from scene_objects.button import Button
from scene_objects.views.about_dialog_view import AboutDialogView


class AboutDialog(Modal):

    def __init__(self):
        super().__init__(AboutDialogView(self))

        self.close_button = Button('Close', self.close)
        self.children.append(self.close_button)
