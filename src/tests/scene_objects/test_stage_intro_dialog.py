import pygame
import pytest

from scene_objects.stage_intro_dialog import StageIntroDialog, TimerBadge, Section
from ui.color import Color
from window_size import WINDOW_SIZE


def _make_dialog(*, badges=()):
    dialog = StageIntroDialog(
        'Stage 1: 1998',
        (Section('Victory Conditions', ('Survive 6 minutes',)),),
        badges=badges,
    )
    dialog.view.set_xy(0, 0)
    return dialog


def _count_pixels_in_dialog(dialog, surface, expected_rgb):
    target = expected_rgb[:3]
    view = dialog.view
    match = 0
    for x in range(int(view.x), int(view.x + view.width)):
        for y in range(int(view.y), int(view.y + view.height)):
            if surface.get_at((x, y))[:3] == target:
                match += 1
    return match


class TestStageIntroDialogTimerBadge:
    @pytest.fixture
    def surface(self):
        return pygame.Surface(WINDOW_SIZE)

    def test_height_increases_when_timer_badge_added(self):
        without_badge = _make_dialog()
        with_timer_badge = _make_dialog(badges=(TimerBadge(6),))

        assert with_timer_badge.view.height > without_badge.view.height

    def test_timer_badge_renders_more_white_pixels_when_present(self, surface):
        baseline = _make_dialog()
        baseline.view.draw(surface)
        baseline_white = _count_pixels_in_dialog(baseline, surface, Color.WHITE)

        surface.fill(Color.BLACK)
        with_timer_badge = _make_dialog(badges=(TimerBadge(6),))
        with_timer_badge.view.draw(surface)
        badge_white = _count_pixels_in_dialog(with_timer_badge, surface, Color.WHITE)

        assert badge_white > baseline_white

    def test_timer_badge_renders_icon_pixels(self, surface):
        dialog = _make_dialog(badges=(TimerBadge(6),))
        dialog.view.draw(surface)

        assert _count_pixels_in_dialog(dialog, surface, Color.BLACK) > 0