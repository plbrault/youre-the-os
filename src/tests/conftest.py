import os
os.chdir('src')

import pygame
import pytest

from engine.scene_manager import SceneManager
from scenes.stage import Stage
from config.cpu_config import CpuConfig
from config.stage_config import StageConfig
from window_size import WINDOW_SIZE

@pytest.fixture
def scene_manager():
    scene_manager = SceneManager()
    scene_manager.screen = pygame.Surface(WINDOW_SIZE)
    return scene_manager

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
def stage(stage_config, scene_manager):
    stage = Stage('Test Stage', stage_config)
    stage.scene_manager = scene_manager
    stage.setup()
    return stage

@pytest.fixture
def stage_custom_config(scene_manager):
    def create_stage(custom_config):
        stage = Stage('Test Stage', custom_config)
        stage.scene_manager = scene_manager
        stage.setup()
        return stage
    return create_stage
