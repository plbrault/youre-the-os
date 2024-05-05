import asyncio
from os import path
import sys

import pygame

from engine.game_event import GameEvent
from engine.game_event_type import GameEventType
from engine.game_manager import GameManager
from engine.window_config import WindowConfig
from engine.scene_manager import SceneManager
from scenes.game import Game
from scenes.how_to_play import HowToPlay
from scenes.main_menu import MainMenu
from game_info import TITLE
from window_size import WINDOW_SIZE

async def main():
    game_manager = GameManager()
    game_manager.window_config = WindowConfig(WINDOW_SIZE, TITLE, path.join('assets', 'icon.png'))

    game_scene = Game()
    main_menu_scene = MainMenu()
    how_to_play_scene = HowToPlay()

    game_manager.add_scene(game_scene)
    game_manager.add_scene(main_menu_scene)
    game_manager.add_scene(how_to_play_scene)

    game_manager.startup_scene = main_menu_scene
    await game_manager.play()

asyncio.run(main())
