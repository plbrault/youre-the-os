class GameEvent():
    def __init__(self, type, properties = {}):
        self._type = type
        self._properties = properties

    @property
    def type(self):
        return self._type

    def getProperty(self, name):
        return self._properties[name]
