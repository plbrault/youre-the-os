"""Entrypoint to run game with automated script

This just runs the Game scene, with the difficulty and script
provided from the command line.
"""

import asyncio
from os import path
import sys
import argparse

import pygame

from scenes.game import Game
from scene_manager import scene_manager
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
        config = difficulty_levels.difficulty_levels_map[args.difficulty]

    # set custom fields
    for key in config.keys():
        val = getattr(args, key)
        if val is not None:
            difficulty_config[key] = val

    return args.filename, config


def compile_auto_script(source_file):
    if not path.isabs(source_file):
        source_file = '../' + source_file
    with open(source_file, encoding="utf_8") as in_file:
        source = in_file.read()
    return compile(source, source_file, 'exec')

source_filename, difficulty_config = parse_arguments()
compiled_script = compile_auto_script(source_filename)

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode(WINDOW_SIZE)

icon = pygame.image.load(path.join('assets', 'icon.png'))
pygame.display.set_caption(TITLE)
pygame.display.set_icon(icon)

scenes = {}

game_scene = Game(screen, scenes, difficulty_config, compiled_script, True)
scenes['game'] = game_scene

game_scene.start()

clock = pygame.time.Clock()

FPS = 60

async def main():

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        scene_manager.current_scene.update(pygame.time.get_ticks(), [])
        scene_manager.current_scene.render()

        clock.tick(FPS)

        await asyncio.sleep(0)

asyncio.run(main())
