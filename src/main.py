import asyncio
from os import path

from engine.game_manager import GameManager
from engine.window_config import WindowConfig
from game_info import TITLE
from scenes.stage import Stage
from scenes.how_to_play import HowToPlay
from scenes.main_menu import MainMenu
from window_size import WINDOW_SIZE

async def main():
    game_manager = GameManager()
    game_manager.window_config = WindowConfig(WINDOW_SIZE, TITLE, path.join('assets', 'icon.png'))

    stage_scene = Stage()
    main_menu_scene = MainMenu()
    how_to_play_scene = HowToPlay()

    game_manager.register_scene(stage_scene)
    game_manager.register_scene(main_menu_scene)
    game_manager.register_scene(how_to_play_scene)

    game_manager.startup_scene = main_menu_scene
    await game_manager.play()

asyncio.run(main())
