from os import path
import pygame
import sys
from random import randint
from types import SimpleNamespace

from lib.scene import Scene
from difficulty_levels import default_difficulty
from lib.game_event import GameEvent
from lib.game_event_type import GameEventType
from game_objects.button import Button
from game_objects.game_over_dialog import GameOverDialog
from game_objects.in_game_menu_dialog import InGameMenuDialog
from game_objects.page_manager import PageManager
from game_objects.process_manager import ProcessManager
from game_objects.score_manager import ScoreManager
from game_objects.uptime_manager import UptimeManager
from game_objects.io_queue import IoQueue
from game_objects.process import Process
from game_objects.page import Page

from lib import event_manager

class Game(Scene):
    def __init__(self, screen, scenes, config=default_difficulty['config'], script=None):
        self._config = config
        self._script = script
        self._script_callback = None

        self._current_time = 0

        self._process_manager = None
        self._page_manager = None

        self._in_game_menu_is_open = False
        self._in_game_menu_dialog = None

        self._game_over = False
        self._game_over_time = None
        self._game_over_dialog = None

        super().__init__(screen, scenes)

    def setup(self):
        self._scene_objects = []

        self._in_game_menu_is_open = False
        self._in_game_menu_dialog = None

        self._game_over = False
        self._game_over_time = None
        self._game_over_dialog = None

        self._process_manager = ProcessManager(self)
        self._page_manager = PageManager(self)

        self._process_manager.setup()
        self._scene_objects.append(self._process_manager)

        self._page_manager.setup()
        self._scene_objects.append(self._page_manager)

        self._score_manager = ScoreManager(self)
        self._scene_objects.append(self._score_manager)

        self._uptime_manager = UptimeManager(self, pygame.time.get_ticks())
        self._scene_objects.append(self._uptime_manager)

        open_in_game_menu_button = Button('Menu', self._open_in_game_menu)
        open_in_game_menu_button.view.set_xy(
            self._screen.get_width() - open_in_game_menu_button.view.width - 10,
            10
        )
        self._scene_objects.append(open_in_game_menu_button)

        # for automation
        self._script_callback = None
        if self._script:
            g = {
                'num_cpus': self._config['num_cpus'],
                'num_ram_pages': 16 * self._config['num_ram_rows'],
                'num_swap_pages': 16 * (PageManager._TOTAL_ROWS - self._config['num_ram_rows']),
                **{
                    v.name: v.value
                    for v in event_manager.etypes
                }
            }

            l = None#{}
            exec(self._script, g, l)
            try:
                self._script_callback = g['run_os']
            except KeyError:
                pass

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        self._config = value

    @property
    def game_over(self):
        return self._game_over

    @game_over.setter
    def game_over(self, value):
        self._game_over = value

    @property
    def process_manager(self):
        return self._process_manager

    @property
    def page_manager(self):
        return self._page_manager

    def _open_in_game_menu(self):
        self._in_game_menu_is_open = True
        if self._in_game_menu_dialog is None:
            self._in_game_menu_dialog = InGameMenuDialog(self.setup, self._return_to_main_menu, self._close_in_game_menu)
            self._in_game_menu_dialog.view.set_xy(
                (self._screen.get_width() - self._in_game_menu_dialog.view.width) / 2,
                (self._screen.get_height() - self._in_game_menu_dialog.view.height) / 2
            )
            self._scene_objects.append(self._in_game_menu_dialog)
        self._uptime_manager.pause()

    def _close_in_game_menu(self):
        self._in_game_menu_is_open = False
        self._scene_objects.remove(self._in_game_menu_dialog)
        self._in_game_menu_dialog = None
        self._uptime_manager.resume()

    def _return_to_main_menu(self):
        self._scenes['main_menu'].start()

    def _get_script_events(self):
        if self._script_callback is None:
            return []
        events = self._script_callback(event_manager.get_events())
        event_manager.clear_events()
        return events

    def update(self, current_time, events):
        dialog = None

        if self._in_game_menu_is_open:
            dialog = self._in_game_menu_dialog
        elif self._game_over:
            display_game_over_dialog = self._game_over_time is not None and current_time - self._game_over_time > 1000
            if self._game_over_time is None:
                self._game_over_time = current_time
            elif display_game_over_dialog:
                if self._game_over_dialog is None:
                    self._game_over_dialog = GameOverDialog(
                        self._uptime_manager.uptime_text, self._score_manager.score, self.setup, self._return_to_main_menu
                    )
                    self._game_over_dialog.view.set_xy(
                        (self._screen.get_width() - self._game_over_dialog.view.width) / 2,
                        (self._screen.get_height() - self._game_over_dialog.view.height) / 2
                    )
                    self._scene_objects.append(self._game_over_dialog)
                dialog = self._game_over_dialog

        if dialog is not None:
            dialog.update(current_time, events)
        else:
            # first, the script generated events
            for event in self._get_script_events():
                try:
                    if event['type'] == 'io_queue':
                        IoQueue.Instance.onClick()
                    elif event['type'] == 'process':
                        Process.Processes[event['pid']].onClick()
                    elif event['type'] == 'page':
                        Page.Pages[(event['pid'],event['idx'])].onClick()
                except Exception as e:
                    print(e.__class__.__name__, *e.args, event, file=sys.stderr)
            # now, update
            for game_object in self._scene_objects:
                game_object.update(current_time, events)
