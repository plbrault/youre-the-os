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

    def register_scene(self, scene: Scene):
        self._scenes[scene.scene_id] = scene

    def get_scene(self, scene_id: str):
        if scene_id not in self._scenes:
            return None
        return self._scenes[scene_id]

    def start_scene(self, scene: Union[Scene, str]):
        if isinstance(scene, str):
            scene_id = scene
            if scene_id not in self._scenes:
                raise ValueError('Scene not found: {}'.format(scene_id))
            scene = self._scenes[scene_id]

        scene.scene_manager = self
        scene.setup()
        self._current_scene = scene
