class SceneManager():
    def __init__(self):
        self._current_scene = None
        self._scenes = {}

    @property
    def current_scene(self):
        return self._current_scene

    def add_scene(self, scene):
        self._scenes[scene.name] = scene
        self._scenes[scene.name].scene_manager = self

    def get_scene(self, scene_name):
        return self._scenes[scene_name]

    def start_scene(self, scene_name):
        self._scenes[scene_name].setup()
        self._current_scene = self._scenes[scene_name]
