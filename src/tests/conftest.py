import os
os.chdir('src')

import pygame
import pytest

import scenes.stage
from stage_config import StageConfig
from window_size import WINDOW_SIZE

@pytest.fixture
def screen(monkeypatch):
    screen = pygame.Surface(WINDOW_SIZE)
    return screen

@pytest.fixture
def Stage(monkeypatch):
    @property
    def current_time(self):
        return 0
    monkeypatch.setattr(scenes.stage.Stage, 'current_time', current_time)
    return scenes.stage.Stage

@pytest.fixture
def stage(Stage, screen):
    config = StageConfig(
        num_cpus = 4,
        num_processes_at_startup = 14,
        num_ram_rows = 8,
        new_process_probability = 0,
        io_probability = 0,
        graceful_termination_probability = 0
    )
    stage = Stage('Test Stage', config)
    stage.screen = screen
    stage.setup()
    return stage

@pytest.fixture
def stage_custom_config(screen, Stage):
    def create_stage(stage_config):
        stage = Stage('Test Stage', stage_config)
        stage.screen = screen
        stage.setup()
        return stage
    return create_stage
