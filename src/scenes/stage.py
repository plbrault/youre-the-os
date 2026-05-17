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

        self._process_manager = None
        self._page_manager = None

        self._stage_victory = False
        self._stage_defeat = False
        self._stage_completed = False
        self._stage_completed_time = None
        self._stage_completion_action_executed = False

        self._score_manager = None
        self._uptime_manager = None
        self._name_label = None

        self._open_in_game_menu_button = None

        super().__init__('stage')

    def setup(self):
        self._scene_objects = []

        self._stage_victory = False
        self._stage_defeat = False
        self._stage_completed = False
        self._stage_completed_time = None
        self._stage_completion_action_executed = False

        self._process_manager = ProcessManager(self, self._config)
        self._page_manager = PageManager(self, self._config)

        self._process_manager.setup()
        self._scene_objects.append(self._process_manager)

        self._page_manager.setup()
        self._scene_objects.append(self._page_manager)

        self._score_manager = ScoreManager(self)
        self._score_manager.view.set_xy(840, 10)
        self._scene_objects.append(self._score_manager)

        self._uptime_manager = UptimeManager()
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
    def stage_completed(self):
        return self._stage_completed

    @property
    def process_manager(self):
        return self._process_manager

    @property
    def page_manager(self):
        return self._page_manager

    @property
    def uptime_manager(self):
        return self._uptime_manager

    def check_victory(self, current_time: int) -> bool: # pylint: disable=unused-argument
        """
        This method is called each frame to check if the victory conditions have been met.
        By default, it always returns False, as the default stage cannot be won.
        Override in a subclass to implement victory conditions for a specific stage.
        :param current_time: The current time in milliseconds since the stage started.
                             Can be used to implement time-based victory conditions.
        """
        return False

    def check_defeat(self, current_time: int) -> bool: # pylint: disable=unused-argument
        """
        This method is called each frame to check if the defeat conditions have been met.
        By default, it returns True if the stage config's max_processes_terminated_by_user
        has been reached.
        Override in a subclass to change defeat conditions for a specific stage.
        :param current_time: The current time in milliseconds since the stage started.
                             Can be used to implement time-based defeat conditions.
        """
        return (
            self._process_manager.user_terminated_process_count
            >= self._config.max_processes_terminated_by_user
        )

    def on_victory(self):
        """
        This method is called once the stage is completed with a victory.
        Default implementation is empty.
        Override in a subclass to implement behavior for a specific stage.
        """

    def on_defeat(self):
        """
        This method is called once the stage is completed with a defeat.
        Default implementation opens the Game Over modal.
        Override in a subclass to implement a different behavior for a specific stage.
        """
        self.show_modal(GameOverDialog(
            uptime=self._uptime_manager.uptime_text,
            stage_name=self.name,
            score=self._score_manager.score,
            restart_game_fn=self.reset,
            main_menu_fn=self._return_to_main_menu,
            standalone=self._standalone))

    def _open_in_game_menu(self):
        self.show_modal(InGameMenuDialog(
            self.reset, self._return_to_main_menu))

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
                    self._process_manager.io_queue.handle_player_action()
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

    def _check_stage_completion(self, current_time):
        if not self._stage_completed:
            self._stage_victory = self.check_victory(current_time)
            self._stage_defeat = self.check_defeat(current_time)
            if (self._stage_victory or self._stage_defeat):
                if not self._process_manager.any_process_in_motion:
                    self._stage_completed = True
                    self._stage_completed_time = current_time

    def update(self, current_time, events):
        if self._stage_completed and not self._stage_completion_action_executed:
            if current_time - self._stage_completed_time > ONE_SECOND:
                if self._stage_victory:
                    self.on_victory()
                elif self._stage_defeat:
                    self.on_defeat()
                self._stage_completion_action_executed = True
                return

        self._process_script_events()
        for scene_object in list(self._scene_objects):
            scene_object.update(current_time, events)
        self._check_stage_completion(current_time)
