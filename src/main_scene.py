from random import randint
import os
import pygame
import sys

from game_objects.process_manager import ProcessManager

from game_objects.cpu import Cpu
from game_objects.game_over_dialog import GameOverDialog
from game_objects.io_queue import IoQueue
from game_objects.label import Label
from game_objects.process import Process
from game_objects.process_slot import ProcessSlot
from lib.ui.color import Color
from lib.ui.fonts import FONT_ARIAL_20
from lib.game_event import GameEvent
from lib.game_event_type import GameEventType

class MainScene:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        
        self._game_objects = []

        self._game_over = False
        self._game_over_time = None
        self._game_over_dialog = None

        self._window_width = 1024
        self._window_height = 768
        screen_size = self._window_width, self._window_height
        self._screen = pygame.display.set_mode(screen_size)

        icon = pygame.image.load(os.path.join('assets', 'icon.png'))
        pygame.display.set_caption("You're the OS!")
        pygame.display.set_icon(icon)

        self._setup()
        self._main_loop()

    @property
    def game_over(self):
        return self._game_over
    
    @game_over.setter
    def game_over(self, value):
        self._game_over = value

    def _setup(self):
        self._game_objects = []
        
        self._game_over = False
        self._game_over_time = None
        self._game_over_dialog = None
        
        process_manager = ProcessManager(self)
        self._game_objects.append(process_manager)

    def _main_loop(self):
        while True:
            self._update(pygame.time.get_ticks())
            self._render()

    def _update(self, current_time):
        events = []

        display_game_over_dialog = self._game_over and self._game_over_time is not None and current_time - self._game_over_time > 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if self._game_over and display_game_over_dialog:
                if event.type == pygame.MOUSEBUTTONUP or event.type == pygame.KEYUP:
                    self._setup()
            elif not self._game_over:
                if event.type == pygame.MOUSEBUTTONUP:
                    if (event.button == 1):
                        events.append(GameEvent(GameEventType.MOUSE_LEFT_CLICK, { 'position': event.pos }))

        if self._game_over:
            if self._game_over_time is None:
                self._game_over_time = current_time
            elif display_game_over_dialog and self._game_over_dialog is None:
                self._game_over_dialog = GameOverDialog()
                self._game_over_dialog.view.set_xy(
                    (self._window_width - self._game_over_dialog.view.width) / 2, (self._window_height - self._game_over_dialog.view.height) / 2
                )
                self._game_objects.append(self._game_over_dialog)
        else:  
            for game_object in self._game_objects:
                game_object.update(current_time, events)

    def _render(self):
        self._screen.fill(Color.BLACK)

        for game_object in self._game_objects:
            game_object.render(self._screen)

        pygame.display.flip()
