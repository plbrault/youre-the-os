from abc import ABC, abstractmethod


class GameManager(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def setup(self, set_window_config, set_scenes)