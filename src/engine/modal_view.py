from abc import abstractmethod

import pygame

from engine.drawable import Drawable
from ui.color import Color


class ModalView(Drawable):
    @property
    @abstractmethod
    def width(self):
        pass

    @property
    @abstractmethod
    def height(self):
        pass

    def draw(self, surface):
        pygame.draw.rect(
            surface,
            Color.WHITE,
            pygame.Rect(self.x, self.y, self.width, self.height),
            border_radius=3
        )
        pygame.draw.rect(
            surface,
            (70, 70, 70),
            pygame.Rect(self.x + 2, self.y + 2, self.width - 4, self.height - 4),
            border_radius=3
        )
        self.draw_content(surface)

    @abstractmethod
    def draw_content(self, surface):
        pass
