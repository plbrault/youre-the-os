from typing import Union

from pygame import Surface

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
        self._scenes[scene.scene_id] = scene
        self._scenes[scene.scene_id].scene_manager = self

    def get_scene(self, scene_id: str):
        if scene_id not in self._scenes:
            return None
        return self._scenes[scene_id]

    def start_scene(self, scene: Union[Scene, str]):
        scene_id = None
        if isinstance(scene, Scene):
            scene_id = scene.scene_id
        else:
            scene_id = scene
        if scene_id not in self._scenes:
            raise ValueError('Scene needs to be added with `add_scene` prior to starting it.')

        self._scenes[scene_id].setup()
        self._current_scene = self._scenes[scene_id]
