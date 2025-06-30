import asyncio
from os import path

from config.difficulty_levels import default_difficulty
from engine.game_manager import GameManager
from engine.window_config import WindowConfig
from game_info import TITLE
from scenes.how_to_play import HowToPlay
from scenes.main_menu import MainMenu
from scenes.stage import Stage
from window_size import WINDOW_SIZE

async def main():
    stage = Stage('SANDBOX', default_difficulty.config, standalone=True)

    game_manager = GameManager()
    game_manager.window_config = WindowConfig(WINDOW_SIZE, TITLE, path.join('assets', 'icon.png'))
    game_manager.startup_scene = stage

    await game_manager.play()

asyncio.run(main())
