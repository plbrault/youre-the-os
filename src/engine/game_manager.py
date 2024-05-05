from abc import ABC, abstractmethod
import pygame

from src.engine.scene import Scene
from src.engine.scene_manager import SceneManager


class GameManager(ABC):
    window_config: WindowConfig

    def __init__(self):
        self._current_scene = None
        self._scenes = None
        self._window_config = None
        self._screen = None

    @property
    def current_scene(self):
        return self._current_scene

    @property
    def scenes(self):
        return self._scenes

    def _init_pygame(self):
        pygame.init()
        pygame.font.init()

    def _init_screen(self):
        self._screen = pygame.display.set_mode(self._window_config.size)
        icon = pygame.image.load(self._window_config.icon_path)
        pygame.display.set_caption(self._window_config.title)
        pygame.display.set_icon(icon)

    @abstractmethod
    def setup(self):
        pass

    def play(self):
        self._init_pygame()
        self._setup(
            lambda window_config: self._window_config = window_config,
            lambda scenes: self._scenes = scenes,
            lambda startup_scene: self._current_scene = startup_scene
        )
