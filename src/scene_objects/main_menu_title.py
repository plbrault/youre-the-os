from engine.scene_object import SceneObject
from scene_objects.views.main_menu_title_view import MainMenuTitleView


class MainMenuTitle(SceneObject):

    def __init__(self):
        super().__init__(MainMenuTitleView(self))
