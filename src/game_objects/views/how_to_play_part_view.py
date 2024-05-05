import pygame

from ui.color import Color
from lib.drawable import Drawable
from ui.fonts import FONT_SECONDARY_SMALL
from window_size import WINDOW_WIDTH, WINDOW_HEIGHT


class HowToPlayPartView(Drawable):
    def __init__(self, how_to_play_part):
        self._how_to_play_part = how_to_play_part
        super().__init__()

        self._text_surfaces = list(
            map(
                lambda text: FONT_SECONDARY_SMALL.render(
                    text, True, Color.BLACK),
                how_to_play_part.text
            )
        )

        self._images = how_to_play_part.images

    @property
    def width(self):
        return WINDOW_WIDTH

    @property
    def height(self):
        return WINDOW_HEIGHT

    def draw(self, surface):
        surface.blit(self._images[self._how_to_play_part.current_image_id], (
            self.x +
            (self.width -
             self._images[self._how_to_play_part.current_image_id].get_width()) / 2,
            (self.height - 65 -
             self._images[self._how_to_play_part.current_image_id].get_height()) / 2
        ))

        pygame.draw.rect(
            surface,
            Color.YELLOW,
            pygame.Rect(
                self.x + 50,
                self.y + self.height - 82,
                self.width - 100,
                58
            )
        )

        y = self.height - 80
        for text_surface in self._text_surfaces:
            surface.blit(text_surface, (
                self.x + (self.width - text_surface.get_width()) / 2,
                y
            ))
            y += text_surface.get_height() + 10

        if len(self._text_surfaces) == 1:
            y += self._text_surfaces[0].get_height() + 10
