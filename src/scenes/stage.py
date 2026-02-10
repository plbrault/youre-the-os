import sys
from os.path import dirname, abspath

from constants import ONE_SECOND
import game_monitor
from engine.scene import Scene
from scene_objects.button import Button
from scene_objects.game_over_dialog import GameOverDialog
from scene_objects.in_game_menu_dialog import InGameMenuDialog
from scene_objects.label import Label
from scene_objects.page_manager import PageManager
from scene_objects.process_manager import ProcessManager
from scene_objects.score_manager import ScoreManager
from scene_objects.uptime_manager import UptimeManager
from config.stage_config import StageConfig

class Stage(Scene):
    def __init__(self, name: str, config : StageConfig,
                 *, script=None, standalone=False):
        self._name = name

        self._config = config
        self._script = script
        self._script_callback = None
        self._standalone = standalone

        self._paused_since = None
        self._total_paused_time = 0

        self._process_manager = None
        self._page_manager = None

        self._in_game_menu_dialog = None

        self._game_over = False
        self._game_over_time = None
        self._game_over_dialog = None

        self._score_manager = None
        self._uptime_manager = None
        self._name_label = None

        self._open_in_game_menu_button = None

        super().__init__('stage')

    def setup(self):
        self._paused_since = None
        self._total_paused_time = 0

        self._scene_objects = []

        self._in_game_menu_dialog = None

        self._game_over = False
        self._game_over_time = None
        self._game_over_dialog = None

        self._process_manager = ProcessManager(self, self._config)
        self._page_manager = PageManager(self, self._config)

        self._process_manager.setup()
        self._scene_objects.append(self._process_manager)

        self._page_manager.setup()
        self._scene_objects.append(self._page_manager)

        self._score_manager = ScoreManager(self)
        self._score_manager.view.set_xy(840, 10)
        self._scene_objects.append(self._score_manager)

        self._uptime_manager = UptimeManager(self)
        self._uptime_manager.view.set_xy(
            512 - self._uptime_manager.view.width // 2,
            10
        )
        self._scene_objects.append(self._uptime_manager)

        self._name_label = Label(self.name)
        self._name_label.view.set_xy(
            (
                self._uptime_manager.view.x
                + self._uptime_manager.view.width
                + self._score_manager.view.x
                - self._name_label.view.width
            ) // 2,
            self._score_manager.view.y
        )
        self._scene_objects.append(self._name_label)

        if not self._standalone:
            self._open_in_game_menu_button = Button(
                'Menu', self._open_in_game_menu, key_bind='escape')
            self._open_in_game_menu_button.view.set_xy(
                self.screen.get_width() - self._open_in_game_menu_button.view.width - 10, 10)
            self._scene_objects.append(self._open_in_game_menu_button)

        self._prepare_automation_script()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def standalone(self):
        return self._standalone

    @standalone.setter
    def standalone(self, value):
        self._standalone = value

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

    @property
    def uptime_manager(self):
        return self._uptime_manager

    @property
    def is_paused(self):
        return self._paused_since is not None

    @Scene.current_time.getter
    def current_time(self): # pylint: disable=invalid-overridden-method
        if self.is_paused:
            return self._paused_since
        return super().current_time - self._total_paused_time

    def _pause(self):
        if not self._paused_since:
            self._paused_since = self.current_time

    def _unpause(self):
        if self._paused_since:
            paused_since = self._paused_since
            self._paused_since = None
            self._total_paused_time += self.current_time - paused_since

    def _open_in_game_menu(self):
        if self._in_game_menu_dialog is None:
            self._pause()
            self._in_game_menu_dialog = InGameMenuDialog(
                self.setup, self._return_to_main_menu, self._close_in_game_menu)
            self._in_game_menu_dialog.view.set_xy(
                (self.screen.get_width() - self._in_game_menu_dialog.view.width) / 2,
                (self.screen.get_height() - self._in_game_menu_dialog.view.height) / 2)
            # Must be before menu button as both handles same key,
            # otherwise close will detect menu as open in same cycle
            menu_button_index = self._scene_objects.index(self._open_in_game_menu_button)
            self._scene_objects.insert(menu_button_index, self._in_game_menu_dialog)

    def _close_in_game_menu(self):
        if self._in_game_menu_dialog:
            self._unpause()
            self._scene_objects.remove(self._in_game_menu_dialog)
            self._in_game_menu_dialog = None

    def _return_to_main_menu(self):
        self.scene_manager.start_scene('main_menu')

    def _get_script_events(self):
        if self._script_callback is None:
            return []
        events = self._script_callback(game_monitor.get_events())
        game_monitor.clear_events()
        return events

    def _process_script_events(self):
        for event in self._get_script_events():
            try:
                if event['type'] == 'io_queue':
                    self._process_manager.io_queue.process_events()
                elif event['type'] == 'process':
                    process = self._process_manager.get_process(event['pid'])
                    if process is not None:
                        if process.has_cpu:
                            process.toggle()
                        else:
                            process.toggle(to_e_core=event.get('to_e_core', False))
                elif event['type'] == 'page':
                    self._page_manager.get_page(
                        event['pid'], event['idx']).request_swap()
            except Exception as exc: # pylint: disable=broad-exception-caught
                print(exc.__class__.__name__, *exc.args, event, file=sys.stderr)

    def _prepare_automation_script(self):
        # pylint: disable=exec-used
        self._script_callback = None
        if self._script is None:
            return

        # Add project root to sys.path so scripts can import from automation package
        project_root = dirname(dirname(abspath(self._script.co_filename)))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        num_cols = PageManager.get_num_cols()
        script_globals = {
            'num_cpus': self._config.cpu_config.total_threads,
            'num_ram_pages': num_cols * self._config.num_ram_rows,
            'num_swap_pages':
                num_cols * (PageManager.get_total_rows() - self._config.num_ram_rows),
            '__file__': self._script.co_filename,
        }
        script_globals['cpu_core_types'] = []
        for i in range(self._config.cpu_config.num_cores):
            for _ in range(self._config.cpu_config.num_threads_for_core[i]):
                script_globals['cpu_core_types'].append(
                    self._config.cpu_config.type_for_core[i].name
                )

        exec(self._script, script_globals)
        try:
            self._script_callback = script_globals['scheduler']
        except KeyError:
            pass

    def _check_game_over(self):
        if (
            self._process_manager.user_terminated_process_count
            == self._config.max_processes_terminated_by_user
        ):
            if not self._process_manager.any_process_in_motion:
                self._game_over = True

    def update(self, current_time, events):
        dialog = None

        if self._in_game_menu_dialog:
            dialog = self._in_game_menu_dialog
        elif self._game_over:
            display_game_over_dialog = self._game_over_time is not None and current_time - \
                self._game_over_time > ONE_SECOND
            if self._game_over_time is None:
                self._game_over_time = current_time
            elif display_game_over_dialog:
                if self._game_over_dialog is None:
                    self._game_over_dialog = GameOverDialog(
                        uptime = self._uptime_manager.uptime_text,
                        stage_name = self.name,
                        score = self._score_manager.score,
                        restart_game_fn = self.setup,
                        main_menu_fn = self._return_to_main_menu,
                        standalone = self._standalone)
                    self._game_over_dialog.view.set_xy(
                        (self.screen.get_width() -
                         self._game_over_dialog.view.width) / 2,
                        (self.screen.get_height() -
                         self._game_over_dialog.view.height) / 2
                    )
                    self._scene_objects.append(self._game_over_dialog)
                dialog = self._game_over_dialog

        if dialog is not None:
            dialog.update(current_time, events)
        else:
            self._process_script_events()
            for scene_object in self._scene_objects:
                scene_object.update(current_time, events)
            self._check_game_over()
