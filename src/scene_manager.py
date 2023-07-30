class SceneManager():
    def __init__(self):
        self._current_scene = None
        
    @property
    def current_scene(self):
        return self._current_scene
    
    def start_scene(self, scene):
        scene.setup()
        self._current_scene = scene
    
scene_manager = SceneManager()
