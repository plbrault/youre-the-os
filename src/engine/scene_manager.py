from dataclasses import dataclass
from typing import Optional, Union

from pygame import Surface

from engine.game_object import GameObject
from engine.scene import Scene


@dataclass
class _ContextEntry:
    context: GameObject
    start_time: int
    paused_time: int = 0


class SceneManager():
    def __init__(self):
        self._current_scene = None
        self._scenes = {}
        self._screen = None
        self._context_stack = []
        self._global_time = 0

    @property
    def current_scene(self):
        return self._current_scene

    @property
    def screen(self):
        return self._screen

    @screen.setter
    def screen(self, value: Surface):
        self._screen = value

    def register_scene(self, scene: Scene):
        self._scenes[scene.scene_id] = scene

    def get_scene(self, scene_id: str):
        if scene_id not in self._scenes:
            return None
        return self._scenes[scene_id]

    def update(self, global_time: int, events):
        self._global_time = global_time

        if not self._context_stack:
            return

        local_time = self._get_local_time()
        active_context = self._context_stack[-1].context
        scene_before_update = self._current_scene

        active_context.update(local_time, events)

        # Only re-update if the scene itself changed (not just modal push/pop)
        if self._current_scene != scene_before_update:
            local_time = self._get_local_time()
            active_context = self._context_stack[-1].context
            active_context.update(local_time, [])

    def _get_local_time(self) -> int:
        entry = self._context_stack[-1]
        return self._global_time - entry.start_time - entry.paused_time

    def push_context(self, context):
        if not self._context_stack:
            raise RuntimeError(
                'Cannot push context without an active root scene. Call start_scene() first.'
            )

        self._context_stack.append(_ContextEntry(context, self._global_time))

    def pop_context(self):
        if len(self._context_stack) <= 1:
            return None

        popped_entry = self._context_stack.pop()
        pause_duration = self._global_time - popped_entry.start_time

        if self._context_stack:
            self._context_stack[-1].paused_time += pause_duration

        return popped_entry.context

    def reset_current_context_time(self):
        if self._context_stack:
            self._context_stack[-1].start_time = self._global_time
            self._context_stack[-1].paused_time = 0

    def get_top_context(self) -> Optional[GameObject]:
        """Return the top context from the stack, or None if stack is empty."""
        if not self._context_stack:
            return None
        return self._context_stack[-1].context

    def start_scene(self, scene: Union[Scene, str], global_time: Optional[int] = None):
        if isinstance(scene, str):
            scene_id = scene
            if scene_id not in self._scenes:
                raise ValueError(f'Scene not found: {scene_id}')
            scene = self._scenes[scene_id]

        scene.scene_manager = self
        self._current_scene = scene

        start_time = global_time if global_time is not None else self._global_time
        self._context_stack = [_ContextEntry(scene, start_time)]

        if global_time is not None:
            self._global_time = global_time

        scene.reset()
