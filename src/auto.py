"""
Entry point to run the game with an automated script.

This just runs the Stage scene, with the difficulty and script
provided from the command line.
"""

import asyncio
from os import path
import argparse

from engine.game_manager import GameManager
from engine.window_config import WindowConfig
from scenes.game import Stage
from game_info import TITLE
from window_size import WINDOW_SIZE
import difficulty_levels

def _int_range(vmin, vmax):
    def ranged_int(arg):
        iarg = int(arg)
        if iarg < vmin or arg > vmax:
            raise ValueError("Argument not in range")
        return iarg
    return ranged_int

class RangedInt:
    """Type validator for argparse"""
    def __init__(self, name, vmin, vmax):
        self._name = name
        self._min = vmin
        self._max = vmax

    def __call__(self, arg):
        ival = int(arg)
        if ival < self._min or ival > self._max:
            raise ValueError("not in range")
        return ival

    def __repr__(self):
        """for argparse"""
        return f"{self._name} ({self._min}-{self._max})"

def parse_arguments():
    """Parse command line arguments

    returns the script filename and the difficulty configuration"""

    parser = argparse.ArgumentParser(
                prog="auto",
                description="Run the game with an automated script")

    # file for script
    parser.add_argument('filename',
        help="filename of the automated script")

    # base difficulty (only one can be provided
    difficulty_group = parser.add_mutually_exclusive_group()
    difficulty_group.add_argument('--easy', action='store_const',
        const='easy', dest='difficulty', help="set base difficulty to easy")
    difficulty_group.add_argument('--normal', action='store_const',
        const='normal', dest='difficulty', help="set base difficulty to normal (default)")
    difficulty_group.add_argument('--hard', action='store_const',
        const='hard', dest='difficulty', help="set base difficulty to hard")
    difficulty_group.add_argument('--harder', action='store_const',
        const='harder', dest='difficulty', help="set base difficulty to harder")
    difficulty_group.add_argument('--insane', action='store_const',
        const='insane', dest='difficulty', help="set base difficulty to insane")

    # further customize difficulty
    parser.add_argument('--num-cpus',
        type=RangedInt('num_cpus', 1, 16),
        help="number of CPUs (1-16)")
    parser.add_argument('--num-processes-at-startup',
        type=RangedInt('num_processes_at_startup', 1, 42),
        help="number of processes at startup (1-42)")
    parser.add_argument('--num-ram-rows',
        type=RangedInt('num_ram_rows', 1, 11),
        help="number of RAM rows (1-11)")
    parser.add_argument('--new-process-probability',
        type=RangedInt('new_process_probability', 1, 100),
        help="probability of spawning a new process (1-100) %%")
    parser.add_argument('--io-probability',
        type=RangedInt('io_probability', 1, 50),
        help="probability of process blocking for IO (1-50) %%")

    args = parser.parse_args()

    # get base difficulty level
    config = difficulty_levels.default_difficulty['config']
    if args.difficulty is not None:
        config = difficulty_levels.difficulty_levels_map[args.difficulty]['config']

    # set custom fields
    for key in config.keys():
        try:
            val = getattr(args, key)
        except AttributeError:
            # key is in config but is not configurable
            continue
        if val is not None:
            config[key] = val
            # on change, difficulty is now Custom
            config['name'] = "Custom"

    return args.filename, config


def compile_auto_script(source_file):
    if not path.isabs(source_file):
        source_file = '../' + source_file
    with open(source_file, encoding="utf_8") as in_file:
        source = in_file.read()
    return compile(source, source_file, 'exec')

source_filename, difficulty_config = parse_arguments()
compiled_script = compile_auto_script(source_filename)

async def main():
    game_manager = GameManager()
    game_manager.window_config = WindowConfig(WINDOW_SIZE, TITLE, path.join('assets', 'icon.png'))

    game_scene = Stage(difficulty_config, compiled_script, True)

    game_manager.add_scene(game_scene)
    game_manager.startup_scene = game_scene

    await game_manager.play(ignore_events=True)

asyncio.run(main())
