class PlayerInput():
    def __init__(self, player_input_type, properties=None):
        self._type = player_input_type
        self._properties = properties
        if self._properties is None:
            self._properties = {}

    @property
    def type(self):
        return self._type

    def get_property(self, name):
        return self._properties[name]
