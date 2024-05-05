import asyncio
from os import path
import sys

import pygame

from engine.game_event import GameEvent
from engine.game_event_type import GameEventType
from scenes.game import Game
from scenes.how_to_play import HowToPlay
from scenes.main_menu import MainMenu
from scene_manager import scene_manager
from game_info import TITLE
from window_size import WINDOW_SIZE

def compile_auto_script():
    if len(sys.argv) == 1:
        return None
    try:
        source_file = sys.argv[1]
        if not path.isabs(source_file):
            source_file = '../' + source_file
        print('reading source file' , source_file, file=sys.stderr)
        with open(source_file, encoding="utf_8") as in_file:
            source = in_file.read()
        return compile(source, source_file, 'exec')
    except (SyntaxError, ValueError):
        print('Compilation failed, ignoring argument', file=sys.stderr)
        return None

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode(WINDOW_SIZE)

icon = pygame.image.load(path.join('assets', 'icon.png'))
pygame.display.set_caption(TITLE)
pygame.display.set_icon(icon)

scenes = {}

game_scene = Game(screen, scenes, script=compile_auto_script())
scenes['game'] = game_scene

main_menu_scene = MainMenu(screen, scenes)
scenes['main_menu'] = main_menu_scene

how_to_play_scene = HowToPlay(screen, scenes)
scenes['how_to_play'] = how_to_play_scene

main_menu_scene.start()

clock = pygame.time.Clock()

FPS = 60

LEFT_MOUSE_BUTTON = 1

async def main():
    mouse_down = False
    shift_down = False

    while True:
        events = []
        mouse_event_added = False
        mouse_drag_event = None

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT_MOUSE_BUTTON:
                mouse_down = True
            elif event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP and event.button == LEFT_MOUSE_BUTTON:
                mouse_down = False
                if mouse_event_added and mouse_drag_event:
                    events.remove(mouse_drag_event)
                    mouse_event_added = False
                    mouse_drag_event = None
                if not mouse_event_added:
                    events.append(
                        GameEvent(
                            GameEventType.MOUSE_LEFT_CLICK, {
                                'position': event.pos}))
                    mouse_event_added = True
            elif event.type == pygame.KEYDOWN:
                if pygame.key.name(event.key).endswith('shift'):
                    shift_down = True
            elif event.type == pygame.KEYUP:
                if pygame.key.name(event.key).endswith('shift'):
                    shift_down = False
                events.append(
                    GameEvent(
                        GameEventType.KEY_UP, {
                            'key': pygame.key.name(
                                event.key), 'shift': shift_down}))
            elif event.type == pygame.MOUSEMOTION and mouse_down and not mouse_event_added:
                event = GameEvent(GameEventType.MOUSE_LEFT_DRAG, {'position': event.pos})
                events.append(event)
                mouse_event_added = True
                mouse_drag_event = event

        scene = scene_manager.current_scene

        scene.update(scene_manager.current_scene.current_time, events)
        if scene != scene_manager.current_scene:
            scene = scene_manager.current_scene
            scene_manager.current_scene.update(scene_manager.current_scene.current_time, [])

        scene.render()

        clock.tick(FPS)

        await asyncio.sleep(0)

asyncio.run(main())
