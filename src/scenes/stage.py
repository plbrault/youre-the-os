import sys
from enum import Enum, auto
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


class StageState(Enum):
    STARTING = auto()
    PLAYING = auto()
    AWAITING_VICTORY = auto()
    AWAITING_DEFEAT = auto()
    VICTORY = auto()
    DEFEAT = auto()
    ENDED = auto()


class StateEvent(Enum):
    START = auto()
    VICTORY_DETECTED = auto()
    DEFEAT_DETECTED = auto()
    PROCESSES_SETTLED = auto()
    DELAY_ELAPSED = auto()


class Stage(Scene):
    StageState = StageState

    _state_transitions = {
        StageState.STARTING: {
            StateEvent.START: StageState.PLAYING,
        },
        StageState.PLAYING: {
            StateEvent.VICTORY_DETECTED: StageState.AWAITING_VICTORY,
            StateEvent.DEFEAT_DETECTED: StageState.AWAITING_DEFEAT,
        },
        StageState.AWAITING_VICTORY: {
            StateEvent.PROCESSES_SETTLED: StageState.VICTORY,
        },
        StageState.AWAITING_DEFEAT: {
            StateEvent.PROCESSES_SETTLED: StageState.DEFEAT,
        },
        StageState.VICTORY: {
            StateEvent.DELAY_ELAPSED: StageState.ENDED,
        },
        StageState.DEFEAT: {
            StateEvent.DELAY_ELAPSED: StageState.ENDED,
        },
    }

    def __init__(self, name: str, config : StageConfig,
                 *, script=None, standalone=False):
        self._name = name

        self._config = config
        self._script = script
        self._script_callback = None
        self._standalone = standalone

        self._process_manager = None
        self._page_manager = None

        self._state = StageState.STARTING
        self._last_update_time = 0
        self._last_state_change_time = None
        self._defeat_reason = None

        self._score_manager = None
        self._uptime_manager = None
        self._name_label = None

        self._open_in_game_menu_button = None

        super().__init__('stage')

    def setup(self):
        self._scene_objects = []

        self._state = StageState.STARTING
        self._last_update_time = 0
        self._last_state_change_time = None
        self._defeat_reason = None

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
    def state(self):
        return self._state

    @property
    def stage_completed(self):
        return self._state in (
            StageState.VICTORY,
            StageState.DEFEAT,
            StageState.ENDED,
        )

    @property
    def process_manager(self):
        return self._process_manager

    @property
    def page_manager(self):
        return self._page_manager

    @property
    def uptime_manager(self):
        return self._uptime_manager

    def check_victory(self) -> bool:
        """
        This method is called each frame to check if the victory conditions have been met.
        By default, it always returns False, as the default stage cannot be won.
        Override in a subclass to implement victory conditions for a specific stage.
        `check_victory` is always called AFTER `check_defeat`, and only if `check_defeat`
        did not detect a defeat.
        Time-based conditions should use `self.uptime_manager.uptime_ms`.
        """
        return False

    def check_defeat(self) -> bool | tuple[bool, str]:
        """
        This method is called each frame to check if the defeat conditions have been met.
        By default, it returns True if the stage config's max_processes_terminated_by_user
        has been reached.
        Override in a subclass to change defeat conditions for a specific stage.
        `check_defeat` is always called BEFORE `check_victory`.
        Time-based conditions should use `self.uptime_manager.uptime_ms`.
        :returns: A boolean indicating whether the defeat condition has been met,
                  or a tuple (bool, str) where the first element is the defeat flag
                  and the second element is a string describing the reason.
        """
        return (
            self._process_manager.user_terminated_process_count
            >= self._config.max_processes_terminated_by_user
        )

    def on_start(self):
        """
        This method is called on the first frame after the start of the stage.
        It is empty by default.
        Override in a subclass to implement desired behavior in a specific stage.
        """

    def on_victory(self):
        """
        This method is called once the stage is completed with a victory.
        Default implementation is empty.
        Override in a subclass to implement behavior for a specific stage.
        """

    def on_defeat(self, reason: str | None = None): # pylint: disable=unused-argument
        """
        This method is called once the stage is completed with a defeat.
        Default implementation opens the Game Over modal.
        Override in a subclass to implement a different behavior for a specific stage.
        :param reason: Optional string describing the reason for the defeat, as provided
                       by check_defeat. May be None. Not used by the default implementation.
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

    def apply_state_transition(self, event: StateEvent):
        transitions = self._state_transitions.get(self._state, {})
        if event in transitions:
            new_state = transitions[event]
            if new_state != self._state:
                self._state = new_state
                self._last_state_change_time = self._last_update_time

    def _update_playing(self, current_time, events):
        self._process_script_events()
        for scene_object in list(self._scene_objects):
            scene_object.update(current_time, events)
        check_result = self.check_defeat()
        if isinstance(check_result, tuple):
            defeated = check_result[0]
        else:
            defeated = check_result
        if defeated:
            if isinstance(check_result, tuple):
                self._defeat_reason = check_result[1]
            self.apply_state_transition(StateEvent.DEFEAT_DETECTED)
        elif self.check_victory():
            self.apply_state_transition(StateEvent.VICTORY_DETECTED)

    def _update_awaiting_result(self, current_time, events):
        for scene_object in list(self._scene_objects):
            scene_object.update(current_time, events)
        if not self._process_manager.any_process_in_motion:
            self.apply_state_transition(StateEvent.PROCESSES_SETTLED)

    def update(self, current_time, events):
        self._last_update_time = current_time

        if self._state == StageState.STARTING:
            self.on_start()
            self.apply_state_transition(StateEvent.START)

        if self._state == StageState.PLAYING:
            self._update_playing(current_time, events)
        elif self._state in (StageState.AWAITING_VICTORY, StageState.AWAITING_DEFEAT):
            self._update_awaiting_result(current_time, events)
        elif self._state == StageState.VICTORY:
            if current_time - self._last_state_change_time > ONE_SECOND:
                self.on_victory()
                self.apply_state_transition(StateEvent.DELAY_ELAPSED)
        elif self._state == StageState.DEFEAT:
            if current_time - self._last_state_change_time > ONE_SECOND:
                self.on_defeat(self._defeat_reason)
                self.apply_state_transition(StateEvent.DELAY_ELAPSED)
