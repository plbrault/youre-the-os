from engine.modal_view import ModalView
from engine.scene_object import SceneObject


class Modal(SceneObject):
    def __init__(self, view: ModalView):
        super().__init__(view)
        self.scene = None

    def close(self):
        if self.scene is not None:
            self.scene.close_modal()
