"""
Entry point to run the game with an automated script.

Runs a Stage scene with an automation script. Configuration can be
provided via difficulty presets or a sandbox-style config module.
"""

import asyncio
from importlib import import_module
from os import path
import argparse
import sys

from config.difficulty_levels import default_difficulty, difficulty_levels_map
from engine.game_manager import GameManager
from engine.window_config import WindowConfig
from scenes.stage import Stage
from game_info import TITLE
from window_size import WINDOW_SIZE


def parse_arguments():
    """Parse command line arguments.

    Returns the script filename, stage name, and stage configuration.
    """
    parser = argparse.ArgumentParser(
        prog="pipenv run auto",
        description="Run the game with an automated script"
    )

    # Required: automation script file
    parser.add_argument('filename',
        help="filename of the automated script")

    # Configuration source (mutually exclusive)
    config_group = parser.add_mutually_exclusive_group()

    # Difficulty presets
    config_group.add_argument('--easy', action='store_const',
        const='easy', dest='difficulty', help="use easy difficulty preset")
    config_group.add_argument('--normal', action='store_const',
        const='normal', dest='difficulty', help="use normal difficulty preset (default)")
    config_group.add_argument('--hard', action='store_const',
        const='hard', dest='difficulty', help="use hard difficulty preset")
    config_group.add_argument('--harder', action='store_const',
        const='harder', dest='difficulty', help="use harder difficulty preset")
    config_group.add_argument('--insane', action='store_const',
        const='insane', dest='difficulty', help="use insane difficulty preset")

    # Custom stage config
    config_group.add_argument('--sandbox', metavar='MODULE',
        help="use a sandbox config module (e.g., sandbox.sample)")

    args = parser.parse_args()

    # Determine configuration
    if args.sandbox is not None:
        config, name = _load_config_module(args.sandbox)
    else:
        config, name = _get_difficulty_config(args.difficulty)

    return args.filename, name, config


def _load_config_module(module_path):
    """Load configuration from a sandbox-style module."""
    try:
        config_module = import_module(module_path)
    except ModuleNotFoundError:
        print(f"Error: Config module '{module_path}' not found.", file=sys.stderr)
        sys.exit(1)

    if hasattr(config_module, 'config'):
        return config_module.config, 'Custom Config'

    if hasattr(config_module, 'stage'):
        stage = config_module.stage
        # Extract config from stage object
        return stage._config, stage.name or 'Custom Config'  # pylint: disable=protected-access

    print("Error: Config module must define 'config' or 'stage'.", file=sys.stderr)
    sys.exit(1)


def _get_difficulty_config(difficulty_name):
    """Get configuration for a difficulty preset."""
    difficulty = default_difficulty
    if difficulty_name is not None:
        difficulty = difficulty_levels_map[difficulty_name]
    return difficulty.config, f"Difficulty: {difficulty.name.upper()}"


def compile_auto_script(source_file):
    """Compile an automation script file."""
    if not path.isabs(source_file):
        source_file = '../' + source_file
    with open(source_file, encoding="utf_8") as in_file:
        source = in_file.read()
    return compile(source, source_file, 'exec')


script_filename, stage_name, stage_config = parse_arguments()
compiled_script = compile_auto_script(script_filename)

stage_scene = Stage(stage_name, stage_config, script=compiled_script, standalone=True)


async def main():
    """Main entry point."""
    game_manager = GameManager()
    game_manager.window_config = WindowConfig(WINDOW_SIZE, TITLE, path.join('assets', 'icon.png'))

    game_manager.register_scene(stage_scene)
    game_manager.startup_scene = stage_scene

    await game_manager.play(ignore_events=True)

asyncio.run(main())
