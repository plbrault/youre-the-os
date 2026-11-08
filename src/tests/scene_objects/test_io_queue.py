import pytest

from engine.random import Random
from scene_objects.io_queue import IoQueue


class TestIoQueue:
    @pytest.fixture
    def io_queue(self):
        return IoQueue(min_waiting_time_ms=1000, max_waiting_time_ms=5000)

    def test_initial_state(self, io_queue):
        assert io_queue.io_event_count == 0
        assert io_queue.wasted_action_count == 0
        assert io_queue.display_blink_color == False

    def test_wait_for_io_event_registers_waiter(self, io_queue, monkeypatch):
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        io_queue.wait_for_io_event(0, lambda: None, lambda: None)

        io_queue.update(6000, [])
        assert io_queue.io_event_count == 1

        io_queue.wait_for_io_event(6000, lambda: None, lambda: None)
        io_queue.update(11000, [])
        assert io_queue.io_event_count == 2

    def test_io_event_arrives_after_max_time(self, io_queue):
        arrival_callback_called = []

        io_queue.wait_for_io_event(0, lambda: arrival_callback_called.append(1), lambda: None)

        io_queue.update(6000, [])
        assert io_queue.io_event_count == 1
        assert arrival_callback_called == [1]

    def test_io_event_not_does_arrives_before_max_time(self, io_queue, monkeypatch):
        arrival_callback_called = []

        # Force random to NOT trigger the probabilistic io event
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)

        io_queue.wait_for_io_event(0, lambda: arrival_callback_called.append(1), lambda: None)

        io_queue.update(4000, [])
        assert io_queue.io_event_count == 0
        assert arrival_callback_called == []

    def test_multiple_io_events_processed_in_order(self, io_queue, monkeypatch):
        arrival_callback_called = []

        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        io_queue.wait_for_io_event(0, lambda: arrival_callback_called.append(1), lambda: None)
        io_queue.wait_for_io_event(0, lambda: arrival_callback_called.append(2), lambda: None)

        io_queue.update(6000, [])
        assert io_queue.io_event_count == 1
        assert arrival_callback_called == [1]

        io_queue.update(11000, [])
        assert io_queue.io_event_count == 2
        assert arrival_callback_called == [1, 2]

    def test_probabilistic_io_event_arrives(self, io_queue, monkeypatch):
        arrival_callback_called = []

        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        io_queue.wait_for_io_event(0, lambda: arrival_callback_called.append(1), lambda: None)
        io_queue.wait_for_io_event(0, lambda: arrival_callback_called.append(2), lambda: None)

        io_queue.update(6000, [])
        assert io_queue.io_event_count == 1

        io_queue.update(7000, [])
        assert io_queue.io_event_count == 2
        assert arrival_callback_called == [1, 2]

    def test_no_io_event_before_min_waiting_time(self, io_queue, monkeypatch):
        arrival_callback_called = []

        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        io_queue.wait_for_io_event(0, lambda: arrival_callback_called.append(1), lambda: None)

        io_queue.update(500, [])
        assert io_queue.io_event_count == 0
        assert arrival_callback_called == []

    def test_handle_player_action_calls_delivery_callback(self, io_queue, monkeypatch):
        delivery_callback_called = []

        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        io_queue.wait_for_io_event(0, lambda: None, lambda: delivery_callback_called.append(1))
        io_queue.wait_for_io_event(0, lambda: None, lambda: delivery_callback_called.append(2))

        io_queue.update(6000, [])
        io_queue.update(11000, [])

        assert io_queue.io_event_count == 2
        assert delivery_callback_called == []

        io_queue.handle_player_action()
        assert delivery_callback_called == [1, 2]
        assert io_queue.io_event_count == 0

    def test_handle_player_action_empty_queue(self, io_queue):
        io_queue.handle_player_action()
        assert io_queue.io_event_count == 0
        assert io_queue.wasted_action_count == 1

    def test_blink_color_false_when_no_io_events(self, io_queue):
        io_queue.update(0, [])
        assert io_queue.display_blink_color == False

        io_queue.update(1000, [])
        assert io_queue.display_blink_color == False

    def test_blink_color_toggles_when_io_events_present(self, io_queue, monkeypatch):
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        io_queue.wait_for_io_event(0, lambda: None, lambda: None)

        io_queue.update(6000, [])
        assert io_queue.io_event_count == 1

        io_queue.update(6000, [])
        assert io_queue.display_blink_color == False

        io_queue.update(6333, [])
        assert io_queue.display_blink_color == True

        io_queue.update(6666, [])
        assert io_queue.display_blink_color == False

    def test_delivery_callback_order(self, io_queue, monkeypatch):
        delivery_callback_called = []

        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        io_queue.wait_for_io_event(0, lambda: None, lambda: delivery_callback_called.append(1))
        io_queue.wait_for_io_event(0, lambda: None, lambda: delivery_callback_called.append(2))
        io_queue.wait_for_io_event(0, lambda: None, lambda: delivery_callback_called.append(3))

        io_queue.update(6000, [])
        io_queue.update(11000, [])
        io_queue.update(16000, [])

        io_queue.handle_player_action()
        assert delivery_callback_called == [1, 2, 3]

    def test_io_event_arrives_when_max_time_elapsed_regardless_of_probability(self, io_queue, monkeypatch):
        arrival_callback_called = []

        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)

        io_queue.wait_for_io_event(0, lambda: arrival_callback_called.append(1), lambda: None)

        io_queue.update(6000, [])
        assert io_queue.io_event_count == 1
        assert arrival_callback_called == [1]

    def test_probabilistic_io_event_fires_between_min_and_max_time(self, io_queue, monkeypatch):
        """
        Test that probabilistic io notifications can fire after min_waiting_time_ms
        but before max_waiting_time_ms has elapsed.
        """
        arrival_callback_called = []

        # Force random to always trigger the probabilistic io event
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        io_queue.wait_for_io_event(0, lambda: arrival_callback_called.append(1), lambda: None)

        # Update at 2500ms - this is after min_time (1000ms) but before max_time (5000ms)
        # The probabilistic io event should fire here
        io_queue.update(2500, [])

        # The io event should have arrived via probabilistic path
        assert io_queue.io_event_count == 1
        assert arrival_callback_called == [1]

    def test_io_event_arrival_via_max_time_emits_io_queue_notification(self, io_queue, monkeypatch):
        """Test that IO_QUEUE event is emitted when event arrives via max waiting time."""
        import game_monitor

        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)

        io_queue.wait_for_io_event(0, lambda: None, lambda: None)

        game_monitor.clear_notifications()

        io_queue.update(6000, [])

        notifications = game_monitor.get_notifications()
        io_queue_notifications = [e for e in notifications if e.etype == 'IO_QUEUE']
        assert len(io_queue_notifications) == 1
        assert io_queue_notifications[0].io_count == 1

    def test_wasted_action_count_does_not_increment_when_io_events_pending(self, io_queue, monkeypatch):
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        io_queue.wait_for_io_event(0, lambda: None, lambda: None)
        io_queue.update(6000, [])

        assert io_queue.io_event_count == 1
        io_queue.handle_player_action()
        assert io_queue.wasted_action_count == 0

    def test_wasted_action_count_increments_each_time(self, io_queue):
        io_queue.handle_player_action()
        assert io_queue.wasted_action_count == 1
        io_queue.handle_player_action()
        assert io_queue.wasted_action_count == 2
        io_queue.handle_player_action()
        assert io_queue.wasted_action_count == 3

    def test_tooltip_condition_false_initially(self, io_queue):
        io_queue.update(0, [])
        assert io_queue.should_display_tooltip == False

    def test_tooltip_condition_false_when_not_blinking(self, io_queue):
        io_queue.update(30000, [])
        assert io_queue.should_display_tooltip == False

    def test_tooltip_condition_false_before_30_seconds_of_blinking(
            self, io_queue, monkeypatch):
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        io_queue.wait_for_io_event(0, lambda: None, lambda: None)

        io_queue.update(1000, [])
        io_queue.update(30999, [])

        assert io_queue.should_display_tooltip == False

    def test_tooltip_condition_true_after_30_seconds_of_blinking(
            self, io_queue, monkeypatch):
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        io_queue.wait_for_io_event(0, lambda: None, lambda: None)

        io_queue.update(1000, [])
        io_queue.update(31000, [])

        assert io_queue.should_display_tooltip == True

    def test_tooltip_condition_stays_true_while_blinking_continues(
            self, io_queue, monkeypatch):
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        io_queue.wait_for_io_event(0, lambda: None, lambda: None)

        io_queue.update(1000, [])
        io_queue.update(31000, [])
        io_queue.update(31033, [])

        assert io_queue.should_display_tooltip == True

    def test_tooltip_condition_false_after_player_action(
            self, io_queue, monkeypatch):
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        io_queue.wait_for_io_event(0, lambda: None, lambda: None)

        io_queue.update(1000, [])
        io_queue.update(31000, [])
        io_queue.handle_player_action()

        assert io_queue.should_display_tooltip == False

    def test_tooltip_condition_true_again_after_clicking_before_threshold(
            self, io_queue, monkeypatch):
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        io_queue.wait_for_io_event(0, lambda: None, lambda: None)
        io_queue.update(1000, [])
        io_queue.handle_player_action()

        io_queue.wait_for_io_event(1000, lambda: None, lambda: None)
        io_queue.update(31000, [])
        io_queue.update(61000, [])

        assert io_queue.should_display_tooltip == True

    def test_tooltip_condition_never_true_again_after_being_displayed_once(
            self, io_queue, monkeypatch):
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        io_queue.wait_for_io_event(0, lambda: None, lambda: None)
        io_queue.update(1000, [])
        io_queue.update(31000, [])
        assert io_queue.should_display_tooltip == True
        io_queue.handle_player_action()

        io_queue.wait_for_io_event(31000, lambda: None, lambda: None)
        io_queue.update(61000, [])
        io_queue.update(91000, [])

        assert io_queue.should_display_tooltip == False

    def test_cancel_waiter_removes_waiter_before_event_arrival(self, io_queue, monkeypatch):
        """A canceled waiter must not have its I/O event arrive."""
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        arrival_callback_called = []
        waiter = io_queue.wait_for_io_event(
            0, lambda: arrival_callback_called.append(1), lambda: None)

        io_queue.cancel_waiter(waiter)
        io_queue.update(6000, [])

        assert io_queue.io_event_count == 0
        assert arrival_callback_called == []

    def test_cancel_waiter_keeps_queue_ordering_consistent(self, io_queue, monkeypatch):
        """After canceling an unarrived waiter, remaining waiters still arrive in order."""
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        arrivals = []
        first_waiter = io_queue.wait_for_io_event(
            0, lambda: arrivals.append('first'), lambda: None)
        io_queue.cancel_waiter(first_waiter)
        io_queue.wait_for_io_event(0, lambda: arrivals.append('second'), lambda: None)

        io_queue.update(6000, [])

        assert io_queue.io_event_count == 1
        assert arrivals == ['second']

    def test_cancel_waiter_on_arrived_waiter_decrements_io_event_count(
            self, io_queue, monkeypatch):
        """Canceling a waiter whose event already arrived must drop the pending event."""
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        waiter = io_queue.wait_for_io_event(0, lambda: None, lambda: None)
        io_queue.update(6000, [])
        assert io_queue.io_event_count == 1

        import game_monitor

        game_monitor.clear_notifications()
        io_queue.cancel_waiter(waiter)

        assert io_queue.io_event_count == 0
        notifications = game_monitor.get_notifications()
        io_queue_notifications = [e for e in notifications if e.etype == 'IO_QUEUE']
        assert len(io_queue_notifications) == 1
        assert io_queue_notifications[0].io_count == 0

    def test_cancel_waiter_on_arrived_waiter_clears_tooltip_trigger(
            self, io_queue, monkeypatch):
        """Once the last pending event is canceled, the I/O events tooltip must not trigger."""
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        waiter = io_queue.wait_for_io_event(0, lambda: None, lambda: None)
        io_queue.update(1000, [])
        io_queue.update(31000, [])
        assert io_queue.should_display_tooltip == True

        io_queue.cancel_waiter(waiter)

        assert io_queue.io_event_count == 0
        assert io_queue.should_display_tooltip == False

    def test_click_after_canceled_arrived_waiter_is_recorded_as_wasted(
            self, io_queue, monkeypatch):
        """After the canceled waiter removed the phantom event, a click is a wasteful action."""
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        waiter = io_queue.wait_for_io_event(0, lambda: None, lambda: None)
        io_queue.update(6000, [])
        io_queue.cancel_waiter(waiter)

        io_queue.handle_player_action()

        assert io_queue.io_event_count == 0
        assert io_queue.wasted_action_count == 1

    def test_delivery_after_cancellation_serves_remaining_waiters(
            self, io_queue, monkeypatch):
        """Canceling an arrived waiter must not prevent other events from being delivered."""
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        deliveries = []
        canceled_waiter = io_queue.wait_for_io_event(
            0, lambda: None, lambda: deliveries.append('canceled'))
        io_queue.wait_for_io_event(
            0, lambda: None, lambda: deliveries.append('remaining'))

        io_queue.update(6000, [])
        io_queue.update(11000, [])
        assert io_queue.io_event_count == 2

        io_queue.cancel_waiter(canceled_waiter)
        assert io_queue.io_event_count == 1

        io_queue.handle_player_action()

        assert io_queue.io_event_count == 0
        assert deliveries == ['remaining']

    def test_cancel_waiter_is_no_op_for_unknown_token(self, io_queue, monkeypatch):
        """Canceling a token that was never subscribed must silently do nothing."""
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        io_queue.wait_for_io_event(0, lambda: None, lambda: None)
        io_queue.update(6000, [])
        assert io_queue.io_event_count == 1

        import game_monitor

        game_monitor.clear_notifications()
        io_queue.cancel_waiter(object())

        assert io_queue.io_event_count == 1
        assert game_monitor.get_notifications() == []
