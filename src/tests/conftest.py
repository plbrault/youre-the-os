import os
os.chdir('src')

import pygame
import pytest

import scenes.game
from window_size import WINDOW_SIZE

@pytest.fixture
def screen(monkeypatch):
    screen = pygame.Surface(WINDOW_SIZE)
    return screen

@pytest.fixture
def Game(monkeypatch):
    @property
    def current_time(self):
        return 0
    monkeypatch.setattr(scenes.game.Game, 'current_time', current_time)
    return scenes.game.Game

@pytest.fixture
def game(Game, screen):
    game_config = {
        'name': 'Test Config',
        'num_cpus': 4,
        'num_processes_at_startup': 14,
        'num_ram_rows': 8,
        'new_process_probability': 0,
        'io_probability': 0,
        'graceful_termination_probability': 0
    }
    game = Game(screen, None, game_config)
    game.setup()
    return game

@pytest.fixture
def game_custom_config(screen, Game):
    def create_game(game_config):
        game = Game(screen, None, game_config)
        game.setup()
        return game
    return create_game
