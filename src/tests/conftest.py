import os
os.chdir('src')

import pygame
import pytest

from engine.scene_manager import SceneManager
import scenes.stage
from config.cpu_config import CpuConfig
from config.stage_config import StageConfig
from window_size import WINDOW_SIZE

@pytest.fixture
def scene_manager():
    scene_manager = SceneManager()
    scene_manager.screen = pygame.Surface(WINDOW_SIZE)
    return scene_manager

@pytest.fixture
def Stage(monkeypatch):
    @property
    def current_time(self):
        return 0
    monkeypatch.setattr(scenes.stage.Stage, 'current_time', current_time)
    return scenes.stage.Stage

@pytest.fixture
def stage_config():
    return StageConfig(
        cpu_config = CpuConfig(num_cores=4),
        num_processes_at_startup = 14,
        num_ram_rows = 8,
        new_process_probability = 0,
        io_probability = 0,
        graceful_termination_probability = 0
    )

@pytest.fixture
def stage(Stage, stage_config, scene_manager):
    stage = Stage('Test Stage', stage_config)
    stage.scene_manager = scene_manager
    stage.setup()
    return stage

@pytest.fixture
def stage_custom_config(scene_manager, Stage):
    def create_stage(custom_config):
        stage = Stage('Test Stage', custom_config)
        stage.scene_manager = scene_manager
        stage.setup()
        return stage
    return create_stage
