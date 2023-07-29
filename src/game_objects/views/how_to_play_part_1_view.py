from os import path
import pygame

from lib.ui.color import Color
from lib.drawable import Drawable
from lib.ui.fonts import FONT_SECONDARY_SMALL

_text = [
    'In this game, you are the operating system of a computer.',
    'You have to manage processes, memory, and input/output (I/O) events.'
]

_IMAGE_SCALE = 0.9

class HowToPlayPart1View(Drawable):
    def __init__(self, how_to_play_part1):
        self._how_to_play_part1 = how_to_play_part1
        super().__init__()
        
        self._text_surfaces = list(
            map(
                lambda text: FONT_SECONDARY_SMALL.render(text, True, Color.BLACK),
                _text
            )
        )
        
        original_size_image = pygame.image.load(path.join('assets', 'how_to_play_0_0.png'))
        self._image = pygame.transform.scale(original_size_image, (
            int(original_size_image.get_width() * _IMAGE_SCALE),
            int(original_size_image.get_height() * _IMAGE_SCALE)
        ))

    @property
    def width(self):
        return 1024

    @property
    def height(self):
        return 768

    def draw(self, surface):
        y = self.y + 10
        for text_surface in self._text_surfaces:
            surface.blit(text_surface, (
                self.x + (self.width - text_surface.get_width()) / 2,
                y
            ))
            y += text_surface.get_height() + 10
            
        surface.blit(self._image, (
            self.x + (self.width - self._image.get_width()) / 2,
            y
        ))
