import pytest

import pygame

from constants import LAST_ALIVE_STARVATION_LEVEL
from config.process_config import ProcessConfig
from scene_objects.process import Process, ProcessState, StateEvent
from ui.color import Color
from window_size import WINDOW_SIZE


class TestProcessView:
    @pytest.fixture
    def surface(self):
        return pygame.Surface(WINDOW_SIZE)

    @pytest.fixture
    def process_config(self):
        return ProcessConfig(
            io_probability=0,
            graceful_termination_probability=0,
            time_between_starvation_levels_ms=10000
        )

    @pytest.fixture
    def starved_process(self, stage, process_config):
        """Drives an idle process to the last starvation level."""
        process = Process(1, stage, process_config)
        for i in range(0, LAST_ALIVE_STARVATION_LEVEL):
            process.update(i * process.time_between_starvation_levels, [])
            assert process.starvation_level == i + 1
        return process

    def test_draws_countdown_bar_when_starvation_level_5_and_idle(
            self, starved_process, surface):
        starved_process.view.draw(surface)

        assert surface.get_at((5, 60))[:3] == Color.BLUE
        assert surface.get_at((61, 60))[:3] == Color.BLUE

    def test_does_not_draw_countdown_bar_when_awaiting_io_event_on_cpu(
            self, starved_process, surface):
        starved_process.use_cpu()
        starved_process.apply_state_transition(StateEvent.REQUEST_IO)

        assert starved_process.state == ProcessState.BLOCKED_ON_CPU_IO_REQUESTED
        assert starved_process.starvation_level == LAST_ALIVE_STARVATION_LEVEL

        starved_process.view.draw(surface)

        for column in range(2, 32):
            assert surface.get_at((column, 60))[:3] != Color.BLUE
            assert surface.get_at((column, 61))[:3] != Color.BLUE

    def test_does_not_draw_countdown_bar_when_awaiting_io_event_off_cpu(
            self, starved_process, surface):
        starved_process.use_cpu()
        starved_process.apply_state_transition(StateEvent.REQUEST_IO)
        starved_process.yield_cpu()

        assert starved_process.state == ProcessState.BLOCKED_OFF_CPU_IO_REQUESTED
        assert starved_process.starvation_level == LAST_ALIVE_STARVATION_LEVEL

        starved_process.view.draw(surface)

        for column in range(2, 32):
            assert surface.get_at((column, 60))[:3] != Color.BLUE
            assert surface.get_at((column, 61))[:3] != Color.BLUE
