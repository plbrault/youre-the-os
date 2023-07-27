from os import path
import pygame

pygame.font.init()

FONT_PRIMARY_SMALL = pygame.font.Font(path.join('assets', 'VT323-Regular.ttf'), 16) 
FONT_PRIMARY_MEDIUM = pygame.font.Font(path.join('assets', 'VT323-Regular.ttf'), 20)
FONT_PRIMARY_LARGE = pygame.font.Font(path.join('assets', 'VT323-Regular.ttf'), 24)
FONT_PRIMARY_XLARGE = pygame.font.Font(path.join('assets', 'VT323-Regular.ttf'), 30)
FONT_PRIMARY_XXLARGE = pygame.font.Font(path.join('assets', 'VT323-Regular.ttf'), 40)

FONT_SECONDARY_XXSMALL = pygame.font.Font(path.join('assets', 'VictorMono-Regular.ttf'), 8)
FONT_SECONDARY_XSMALL = pygame.font.Font(path.join('assets', 'VictorMono-Regular.ttf'), 9)
