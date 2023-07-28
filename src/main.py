from os import path
import pygame

from scenes.main_menu import MainMenu
from scenes.game import Game

pygame.init()
pygame.font.init()

window_width = 1024
window_height = 768
screen_size = (1024, 768)
screen = pygame.display.set_mode(screen_size)

icon = pygame.image.load(path.join('assets', 'icon.png'))
pygame.display.set_caption("You're the OS!")
pygame.display.set_icon(icon)

scenes = {}

game_scene = Game(screen, scenes)
scenes['game'] = game_scene

main_menu_scene = MainMenu(screen, scenes)
scenes['main_menu'] = main_menu_scene

main_menu_scene.start()
