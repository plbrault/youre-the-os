import asyncio
from os import path
import pygame
import sys

from scenes.game import Game
from lib.game_event import GameEvent
from lib.game_event_type import GameEventType
from scenes.how_to_play import HowToPlay
from scenes.main_menu import MainMenu
from scene_manager import scene_manager
from game_info import TITLE

pygame.init()
pygame.font.init()

window_width = 1024
window_height = 768
screen_size = (window_width, window_height)
screen = pygame.display.set_mode(screen_size)

icon = pygame.image.load(path.join('assets', 'icon.png'))
pygame.display.set_caption(TITLE)
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

async def main():
    mouse_down = False
    
    while True:      
        events = []
        
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_down = True
            elif event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_down = False
                events.append(GameEvent(GameEventType.MOUSE_LEFT_CLICK, { 'position': event.pos }))
                
            if event.type == pygame.MOUSEMOTION and mouse_down:
                events.append(GameEvent(GameEventType.MOUSE_LEFT_DRAG, { 'position': event.pos }))
                    
        scene_manager.current_scene.update(pygame.time.get_ticks(), events)
        scene_manager.current_scene.render()
        
        clock.tick(FPS)
        
        await asyncio.sleep(0)

asyncio.run(main())
