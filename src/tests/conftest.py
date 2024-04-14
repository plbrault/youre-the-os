import os
os.chdir('src')

import pytest

import scenes.game

@pytest.fixture
def game():
    return scenes.game.Game(None, None)
