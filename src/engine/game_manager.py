import asyncio
from typing import Union

import pygame

from engine.player_input import PlayerInput
from engine.player_input_type import PlayerInputType
from engine.scene import Scene
from engine.scene_manager import SceneManager
from engine.window_config import WindowConfig


_LEFT_MOUSE_BUTTON = 1
_RIGHT_MOUSE_BUTTON = 3


class GameManager():
    window_config: WindowConfig
    fps = 60

    @property
    def startup_scene(self):
        return self._startup_scene

    @startup_scene.setter
    def startup_scene(self, value : Union[Scene, str]):
        if isinstance(value, str) and self._scene_manager.get_scene(value) is None:
            scene = self._scene_manager.get_scene(value)
            if scene is None:
                raise ValueError(f'Scene not found: {value}')
        else:
            scene = value
        self._startup_scene = scene

    def __init__(self):
        self._scenes = None
        self._screen = None
        self._scene_manager = SceneManager()
        self._startup_scene = None

        self._mouse_left_down = False
        self._mouse_right_down = False
        self._shift_down = False

    def _init_pygame(self):
        pygame.init()
        pygame.font.init()

    def _init_screen(self):
        if self.window_config is None:
            raise ValueError('Property `window_config` needs to be set.')
        self._screen = pygame.display.set_mode(self.window_config.size)

        icon = pygame.image.load(self.window_config.icon_path)
        pygame.display.set_caption(self.window_config.title)
        pygame.display.set_icon(icon)
        self._scene_manager.screen = self._screen

    def register_scene(self, scene: Scene):
        self._scene_manager.register_scene(scene)

    def start_scene(self, scene: Union[Scene, str]):
        self._scene_manager.start_scene(scene, pygame.time.get_ticks())

    def _get_player_inputs(self):
        # pylint: disable=too-many-branches
        player_inputs = []
        mouse_motion_player_input = None

        def mouse_player_input_added():
            return any(
                player_input.type in (
                    PlayerInputType.MOUSE_LEFT_CLICK,
                    PlayerInputType.MOUSE_RIGHT_CLICK,
                    PlayerInputType.MOUSE_MOTION
                )
                for player_input in player_inputs
            )

        for pygame_event in pygame.event.get():
            if pygame_event.type == pygame.QUIT:
                player_inputs.append(PlayerInput(PlayerInputType.QUIT, {}))
            elif pygame_event.type == pygame.KEYDOWN:
                if pygame.key.name(pygame_event.key).endswith('shift'):
                    self._shift_down = True
            elif pygame_event.type == pygame.KEYUP:
                if pygame.key.name(pygame_event.key).endswith('shift'):
                    self._shift_down = False
                player_inputs.append(
                    PlayerInput(
                        PlayerInputType.KEY_UP, {
                            'key': pygame.key.name(
                                pygame_event.key), 'shift': self._shift_down}))
            elif (pygame_event.type == pygame.MOUSEBUTTONDOWN
                  and pygame_event.button == _LEFT_MOUSE_BUTTON):
                self._mouse_left_down = True
            elif (pygame_event.type == pygame.MOUSEBUTTONDOWN
                  and pygame_event.button == _RIGHT_MOUSE_BUTTON):
                self._mouse_right_down = True
            elif (pygame_event.type == pygame.MOUSEBUTTONUP
                  and pygame_event.button == _LEFT_MOUSE_BUTTON):
                self._mouse_left_down = False
                if mouse_player_input_added() and mouse_motion_player_input:
                    player_inputs.remove(mouse_motion_player_input)
                    mouse_motion_player_input = None
                if not mouse_player_input_added():
                    player_inputs.append(
                        PlayerInput(
                            PlayerInputType.MOUSE_LEFT_CLICK, {
                                'position': pygame_event.pos,
                                'shift': self._shift_down }))
            elif (pygame_event.type == pygame.MOUSEBUTTONUP
                  and pygame_event.button == _RIGHT_MOUSE_BUTTON):
                self._mouse_right_down = False
                if mouse_player_input_added() and mouse_motion_player_input:
                    player_inputs.remove(mouse_motion_player_input)
                    mouse_motion_player_input = None
                if not mouse_player_input_added():
                    player_inputs.append(
                        PlayerInput(
                            PlayerInputType.MOUSE_RIGHT_CLICK, {
                                'position': pygame_event.pos,
                                'shift': self._shift_down }))
            elif pygame_event.type == pygame.MOUSEMOTION and not mouse_player_input_added():
                player_input = PlayerInput(PlayerInputType.MOUSE_MOTION,
                                  {'position': pygame_event.pos,
                                   'left_button_down': self._mouse_left_down,
                                   'right_button_down': self._mouse_right_down,
                                   'shift': self._shift_down})
                player_inputs.append(player_input)
                mouse_motion_player_input = player_input
        return player_inputs

    async def _main_loop(self, ignore_player_inputs=False):
        clock = pygame.time.Clock()

        while True:
            player_inputs = self._get_player_inputs()
            for player_input in player_inputs:
                if player_input.type == PlayerInputType.QUIT:
                    return

            if ignore_player_inputs:
                player_inputs = []

            self._scene_manager.update(pygame.time.get_ticks(), player_inputs)

            self._scene_manager.current_scene.render()

            clock.tick(self.fps)

            await asyncio.sleep(0)

    async def play(self, ignore_player_inputs=False):
        self._init_pygame()
        self._init_screen()
        if self.startup_scene is None:
            raise ValueError('Property `startup_scene` needs to be set.')
        self.start_scene(self.startup_scene)

        await self._main_loop(ignore_player_inputs)
