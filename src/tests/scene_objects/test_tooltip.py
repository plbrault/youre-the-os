import pygame
import pytest

from engine.drawable import Drawable
from scene_objects.tooltip import Tooltip, TooltipAlignment
from ui.color import Color
from window_size import WINDOW_SIZE, WINDOW_WIDTH


class StubAnchorView(Drawable):
    @property
    def width(self):
        return 100

    @property
    def height(self):
        return 40

    def draw(self, surface):
        pass


class TestTooltip:
    @pytest.fixture
    def condition_state(self):
        return {'should_display': False}

    @pytest.fixture
    def tooltip(self, condition_state):
        return Tooltip(
            StubAnchorView(),
            'Tooltip text',
            condition=lambda: condition_state['should_display']
        )

    def test_initial_state(self, tooltip):
        assert tooltip.visible == False
        assert tooltip.opacity == 0

    def test_stays_hidden_when_condition_is_false(self, tooltip):
        tooltip.update(0, [])
        assert tooltip.visible == False
        assert tooltip.opacity == 0

    def test_shows_when_condition_becomes_true(self, condition_state, tooltip):
        condition_state['should_display'] = True

        tooltip.update(0, [])

        assert tooltip.visible == True
        assert tooltip.opacity == 0

    def test_fades_in_progressively_until_complete(self, condition_state, tooltip):
        condition_state['should_display'] = True
        tooltip.update(0, [])

        tooltip.update(125, [])
        assert tooltip.opacity == 0.5

        tooltip.update(250, [])
        assert tooltip.opacity == 1

        tooltip.update(400, [])
        assert tooltip.opacity == 1

    def test_fades_out_when_condition_becomes_false(self, condition_state, tooltip):
        condition_state['should_display'] = True
        tooltip.update(0, [])
        tooltip.update(250, [])
        condition_state['should_display'] = False

        tooltip.update(1000, [])
        assert tooltip.visible == True
        assert tooltip.opacity == 1

        tooltip.update(1125, [])
        assert tooltip.visible == True
        assert tooltip.opacity == 0.5

        tooltip.update(1250, [])
        assert tooltip.visible == False
        assert tooltip.opacity == 0

    def test_fades_out_from_partial_opacity(self, condition_state, tooltip):
        condition_state['should_display'] = True
        tooltip.update(0, [])
        condition_state['should_display'] = False

        tooltip.update(125, [])
        assert tooltip.opacity == 0.5

        tooltip.update(250, [])
        assert tooltip.opacity == 0.25

        tooltip.update(375, [])
        assert tooltip.visible == False
        assert tooltip.opacity == 0

    def test_interrupted_fade_out_fades_back_in(self, condition_state, tooltip):
        condition_state['should_display'] = True
        tooltip.update(0, [])
        tooltip.update(250, [])
        condition_state['should_display'] = False
        tooltip.update(1000, [])
        tooltip.update(1125, [])
        assert tooltip.opacity == 0.5
        condition_state['should_display'] = True

        tooltip.update(1125, [])
        assert tooltip.opacity == 0.5

        tooltip.update(1250, [])
        assert tooltip.opacity == 0.75

        tooltip.update(1375, [])
        assert tooltip.opacity == 1

    def test_fades_in_again_after_being_hidden(self, condition_state, tooltip):
        condition_state['should_display'] = True
        tooltip.update(0, [])
        condition_state['should_display'] = False
        tooltip.update(100, [])
        condition_state['should_display'] = True

        tooltip.update(600, [])
        assert tooltip.opacity == 0

        tooltip.update(725, [])
        assert tooltip.opacity == 0.5

        tooltip.update(850, [])
        assert tooltip.opacity == 1

    def test_hidden_before_first_update_even_with_true_condition(
            self, condition_state):
        condition_state['should_display'] = True
        tooltip = Tooltip(
            StubAnchorView(),
            'Tooltip text',
            condition=lambda: condition_state['should_display']
        )

        assert tooltip.visible == False
        assert tooltip.opacity == 0

    def test_children_updated_through_scene_object_update(
            self, condition_state, tooltip):
        child_condition_state = {'should_display': False}
        tooltip.children.append(Tooltip(
            StubAnchorView(),
            'Child text',
            condition=lambda: child_condition_state['should_display']
        ))
        child_condition_state['should_display'] = True

        tooltip.update(0, [])

        assert tooltip.children[0].visible == True


class TestTooltipView:
    @pytest.fixture
    def surface(self):
        return pygame.Surface(WINDOW_SIZE)

    @pytest.fixture
    def anchor_view(self):
        anchor_view = StubAnchorView()
        anchor_view.set_xy(50, 10)
        return anchor_view

    @pytest.fixture
    def tooltip(self, anchor_view):
        return Tooltip(anchor_view, 'Tooltip text', condition=lambda: True)

    @pytest.fixture
    def view(self, tooltip):
        return tooltip.view

    def test_width_wraps_long_text_to_maximum(self, anchor_view):
        view = Tooltip(anchor_view, 'a' * 100, condition=lambda: True).view
        assert view.width <= 400 + 2 * 10

    def test_default_alignment_positions_below_and_centered_on_anchor(
            self, anchor_view):
        view = Tooltip(anchor_view, 'Tip', condition=lambda: True).view

        assert view.y == anchor_view.y + anchor_view.height + 3
        assert anchor_view.x + anchor_view.width // 2 == view.x + view.width // 2

    def test_right_alignment_positions_arrow_near_top_pointing_at_anchor(
            self, anchor_view):
        tooltip = Tooltip(
            anchor_view, 'Tooltip text',
            condition=lambda: True, alignment=TooltipAlignment.RIGHT)
        view = tooltip.view

        assert view.x == anchor_view.x + anchor_view.width + 3
        assert view.y == anchor_view.y + anchor_view.height // 2 - 20

    def test_right_alignment_arrow_extends_width(self, anchor_view):
        below = Tooltip(
            anchor_view, 'Tooltip text', condition=lambda: True).view
        right = Tooltip(
            anchor_view, 'Tooltip text',
            condition=lambda: True, alignment=TooltipAlignment.RIGHT).view

        assert right.width == below.width + 14

    def test_below_alignment_arrow_extends_height(self, anchor_view):
        below = Tooltip(
            anchor_view, 'Tooltip text', condition=lambda: True).view
        right = Tooltip(
            anchor_view, 'Tooltip text',
            condition=lambda: True, alignment=TooltipAlignment.RIGHT).view

        assert below.height == right.height + 14

    def test_position_clamped_to_screen_boundaries(self):
        anchor_view = StubAnchorView()
        anchor_view.set_xy(1200, 0)
        view = Tooltip(
            anchor_view, 'a' * 100,
            condition=lambda: True, alignment=TooltipAlignment.RIGHT).view

        assert view.x >= 3
        assert view.x + view.width <= WINDOW_WIDTH - 3
        assert view.y >= 3

    def test_draw_nothing_when_fully_transparent(self, surface, anchor_view):
        tooltip = Tooltip(anchor_view, 'Tooltip text', condition=lambda: False)
        tooltip.update(250, [])
        tooltip.view.draw(surface)

        assert surface.get_at(
            (tooltip.view.x + 3, tooltip.view.y + tooltip.view.height // 2)
        )[:3] == Color.BLACK

    def test_draw_renders_translucent_panel_at_full_opacity(
            self, surface, tooltip, view):
        tooltip.update(0, [])
        tooltip.update(250, [])
        view.draw(surface)

        assert surface.get_at(
            (view.x + 3, view.y + view.height // 2))[:3] == (180, 180, 159)
        assert surface.get_at(
            (view.x, view.y + view.height // 2))[:3] == (98, 88, 28)

    def test_draw_renders_semi_transparent_panel_mid_fade(
            self, surface, tooltip, view):
        tooltip.update(0, [])
        tooltip.update(125, [])
        view.draw(surface)

        assert surface.get_at(
            (view.x + 3, view.y + view.height // 2))[:3] == (90, 90, 79)

    def test_draw_renders_arrow_pointing_up_at_anchor(
            self, surface, tooltip, view):
        tooltip.update(0, [])
        tooltip.update(250, [])
        view.draw(surface)

        assert surface.get_at(
            (view.x + view.width // 2, view.y + 2))[:3] == (180, 180, 159)

    def test_draw_renders_arrow_pointing_left_at_anchor(
            self, surface, anchor_view):
        tooltip = Tooltip(
            anchor_view, 'Tooltip text',
            condition=lambda: True, alignment=TooltipAlignment.RIGHT)
        tooltip.update(0, [])
        tooltip.update(250, [])
        tooltip.view.draw(surface)
        view = tooltip.view

        assert surface.get_at(
            (view.x + 2, view.y + 20))[:3] == (180, 180, 159)
        assert surface.get_at(
            (view.x + 2, view.y + view.height // 2))[:3] == Color.BLACK
