import argparse
import asyncio
from importlib import import_module
from os import path
import sys

from engine.game_manager import GameManager
from engine.window_config import WindowConfig
from game_info import TITLE
from window_size import WINDOW_SIZE

arg_parser = argparse.ArgumentParser(
    prog='pipenv run sandbox', description='Run the game in sandbox mode.'
)
arg_parser.add_argument(
    'config_module',
    help='The Python module path from `src` to the sandbox configuration file to use, ' \
        'e.g. `sandbox.sample`.'
)

async def main():
    args = arg_parser.parse_args()
    try:
        config_module = import_module(args.config_module)
    except ModuleNotFoundError:
        print(f"Error: The specified module '{args.config_module}' could not be found.")
        sys.exit(1)

    print("Config module:", args.config_module)

    stage = config_module.stage
    stage.name = 'SANDBOX'
    stage.standalone = True

    game_manager = GameManager()
    game_manager.window_config = WindowConfig(WINDOW_SIZE, TITLE, path.join('assets', 'icon.png'))
    game_manager.startup_scene = stage

    await game_manager.play()

asyncio.run(main())
