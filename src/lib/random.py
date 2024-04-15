"""
Wraps the `random` module to allow injection of a mock while testing.
"""

import random

class Random():
    def get_number(self, min, max):
        return random.randint(min, max)

_random = Random()

def randint(min, max):
    return _random.get_number(min, max)
