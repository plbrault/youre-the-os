import pygame

from engine.drawable import Drawable
from ui.color import Color
from ui.fonts import FONT_PRIMARY_XXLARGE, FONT_SECONDARY_SMALL


class HokeyDialogView(Drawable):
    def __init__(self, about_dialog):
        self.about_dialog = about_dialog
        super().__init__()

        self._title_text = FONT_PRIMARY_XXLARGE.render(
            'Hotkeys', True, Color.WHITE)

        self._explanation_text = FONT_SECONDARY_SMALL.render(
            'Step up your game by using these hotkeys:', True, Color.WHITE)

        self._binding_keys = [
            FONT_SECONDARY_SMALL.render('SPACEBAR', True, Color.WHITE),
            FONT_SECONDARY_SMALL.render('1-9', True, Color.WHITE),
            FONT_SECONDARY_SMALL.render('0', True, Color.WHITE),
            FONT_SECONDARY_SMALL.render('SHIFT + 1-6', True, Color.WHITE),
            FONT_SECONDARY_SMALL.render('SHIFT + Click', True, Color.WHITE),
            FONT_SECONDARY_SMALL.render('S', True, Color.WHITE),
        ]

        self._binding_explanations = [
            FONT_SECONDARY_SMALL.render(
                'Process I/O events',
                True,
                Color.WHITE),
            FONT_SECONDARY_SMALL.render(
                'Remove process from a CPU between #1 and #9',
                True,
                Color.WHITE),
            FONT_SECONDARY_SMALL.render(
                'Remove process from CPU #10',
                True,
                Color.WHITE),
            FONT_SECONDARY_SMALL.render(
                'Remove process from a CPU between #11 and #16',
                True,
                Color.WHITE),
            FONT_SECONDARY_SMALL.render(
                'Swap a whole row of memory pages at once',
                True,
                Color.WHITE),
            FONT_SECONDARY_SMALL.render(
                'Sort Processes (once Sort button is available)',
                True,
                Color.WHITE),
        ]

    @property
    def width(self):
        return 533

    @property
    def height(self):
        return 440

    def draw(self, surface):
        y = self.y + 40

        pygame.draw.rect(surface, Color.WHITE, pygame.Rect(
            self.x, self.y, self.width, self.height), border_radius=3)
        pygame.draw.rect(
            surface,
            (70,
             70,
             70),
            pygame.Rect(
                self.x + 2,
                self.y + 2,
                self.width - 4,
                self.height - 4),
            border_radius=3)

        surface.blit(self._title_text, (self.x + (self.width -
                     self._title_text.get_width()) / 2, self.y + 30))

        y += self._title_text.get_height() + 20
        surface.blit(self._explanation_text, (self.x +
                     (self.width - self._explanation_text.get_width()) / 2, y))

        y += self._explanation_text.get_height() + 40
        first_key_y = y

        for binding_key in self._binding_keys:
            surface.blit(binding_key, (self.x + 20, y))
            y += binding_key.get_height() + 10

        y = first_key_y

        for binding_explanation in self._binding_explanations:
            surface.blit(binding_explanation, (self.x + 150, y))
            y += binding_explanation.get_height() + 10
