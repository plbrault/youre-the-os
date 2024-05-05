from engine.game_object import GameObject
from game_objects.views.main_menu_title_view import MainMenuTitleView


class MainMenuTitle(GameObject):

    def __init__(self):
        super().__init__(MainMenuTitleView(self))
