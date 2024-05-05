from pygame import Surface
from typing import Union

from engine.scene import Scene

class SceneManager():
    def __init__(self):
        self._current_scene = None
        self._scenes = {}
        self._screen = None

    @property
    def current_scene(self):
        return self._current_scene

    @property
    def screen(self):
        return self._screen

    @screen.setter
    def screen(self, value: Surface):
        self._screen = value
        for scene in self._scenes.values():
            scene.screen = value

    def add_scene(self, scene: Scene):
        self._scenes[scene.name] = scene
        self._scenes[scene.name].scene_manager = self

    def get_scene(self, scene_name: str):
        if scene_name not in self._scenes:
            return None
        return self._scenes[scene_name]

    def start_scene(self, scene: Union[Scene, str]):
        scene_name = None
        if isinstance(scene, Scene):
            scene_name = scene.name
        else:
            scene_name = scene
        self._scenes[scene_name].setup()
        self._current_scene = self._scenes[scene_name]
