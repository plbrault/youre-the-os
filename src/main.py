import asyncio
from os import path
import sys

import pygame

from engine.game_event import GameEvent
from engine.game_event_type import GameEventType
from engine.window_config import WindowConfig
from scenes.game import Game
from scenes.how_to_play import HowToPlay
from scenes.main_menu import MainMenu
from scene_manager import scene_manager
from game_info import TITLE
from window_size import WINDOW_SIZE

pygame.init()
pygame.font.init()

window_config = WindowConfig(WINDOW_SIZE, TITLE, path.join('assets', 'icon.png'))

screen = pygame.display.set_mode(window_config.size)

icon = pygame.image.load(window_config.icon_path)
pygame.display.set_caption(window_config.title)
pygame.display.set_icon(icon)

scenes = {}

game_scene = Game(screen, scenes)
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
