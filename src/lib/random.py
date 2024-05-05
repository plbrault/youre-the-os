"""
Wraps the `random` module to allow injection of a mock while testing.
"""

import random

# pylint: disable=too-few-public-methods
class Random():
    def get_number(self, min_value, max_value):
        return random.randint(min_value, max_value)

_random = Random()

def randint(min_value, max_value):
    return _random.get_number(min_value, max_value)
