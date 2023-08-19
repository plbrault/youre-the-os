class GameEvent():
    def __init__(self, event_type, properties=None):
        self._type = event_type
        self._properties = properties
        if self._properties is None:
            self._properties = {}

    @property
    def type(self):
        return self._type

    def get_property(self, name):
        return self._properties[name]
