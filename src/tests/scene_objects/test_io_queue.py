import pytest

from engine.random import Random
from scene_objects.io_queue import IoQueue


class TestIoQueue:
    @pytest.fixture
    def io_queue(self):
        return IoQueue(min_waiting_time_ms=1000, max_waiting_time_ms=5000)

    def test_initial_state(self, io_queue):
        assert io_queue.event_count == 0
        assert io_queue.display_blink_color == False

    def test_wait_for_event_registers_waiter(self, io_queue, monkeypatch):
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        io_queue.wait_for_event(0, lambda: None, lambda: None)

        io_queue.update(6000, [])
        assert io_queue.event_count == 1

        io_queue.wait_for_event(6000, lambda: None, lambda: None)
        io_queue.update(11000, [])
        assert io_queue.event_count == 2

    def test_event_arrives_after_max_time(self, io_queue):
        arrival_callback_called = []

        io_queue.wait_for_event(0, lambda: arrival_callback_called.append(1), lambda: None)

        io_queue.update(6000, [])
        assert io_queue.event_count == 1
        assert arrival_callback_called == [1]

    def test_event_not_does_arrives_before_max_time(self, io_queue, monkeypatch):
        arrival_callback_called = []

        # Force random to NOT trigger the probabilistic event
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)

        io_queue.wait_for_event(0, lambda: arrival_callback_called.append(1), lambda: None)

        io_queue.update(4000, [])
        assert io_queue.event_count == 0
        assert arrival_callback_called == []

    def test_multiple_events_processed_in_order(self, io_queue, monkeypatch):
        arrival_callback_called = []

        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        io_queue.wait_for_event(0, lambda: arrival_callback_called.append(1), lambda: None)
        io_queue.wait_for_event(0, lambda: arrival_callback_called.append(2), lambda: None)

        io_queue.update(6000, [])
        assert io_queue.event_count == 1
        assert arrival_callback_called == [1]

        io_queue.update(11000, [])
        assert io_queue.event_count == 2
        assert arrival_callback_called == [1, 2]

    def test_probabilistic_event_arrives(self, io_queue, monkeypatch):
        arrival_callback_called = []

        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        io_queue.wait_for_event(0, lambda: arrival_callback_called.append(1), lambda: None)
        io_queue.wait_for_event(0, lambda: arrival_callback_called.append(2), lambda: None)

        io_queue.update(6000, [])
        assert io_queue.event_count == 1

        io_queue.update(7000, [])
        assert io_queue.event_count == 2
        assert arrival_callback_called == [1, 2]

    def test_no_event_before_min_waiting_time(self, io_queue, monkeypatch):
        arrival_callback_called = []

        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        io_queue.wait_for_event(0, lambda: arrival_callback_called.append(1), lambda: None)

        io_queue.update(500, [])
        assert io_queue.event_count == 0
        assert arrival_callback_called == []

    def test_handle_player_action_calls_delivery_callback(self, io_queue, monkeypatch):
        delivery_callback_called = []

        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        io_queue.wait_for_event(0, lambda: None, lambda: delivery_callback_called.append(1))
        io_queue.wait_for_event(0, lambda: None, lambda: delivery_callback_called.append(2))

        io_queue.update(6000, [])
        io_queue.update(11000, [])

        assert io_queue.event_count == 2
        assert delivery_callback_called == []

        io_queue.handle_player_action()
        assert delivery_callback_called == [1, 2]
        assert io_queue.event_count == 0

    def test_handle_player_action_empty_queue(self, io_queue):
        io_queue.handle_player_action()
        assert io_queue.event_count == 0

    def test_blink_color_false_when_no_events(self, io_queue):
        io_queue.update(0, [])
        assert io_queue.display_blink_color == False

        io_queue.update(1000, [])
        assert io_queue.display_blink_color == False

    def test_blink_color_toggles_when_events_present(self, io_queue, monkeypatch):
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        io_queue.wait_for_event(0, lambda: None, lambda: None)

        io_queue.update(6000, [])
        assert io_queue.event_count == 1

        io_queue.update(6000, [])
        assert io_queue.display_blink_color == False

        io_queue.update(6333, [])
        assert io_queue.display_blink_color == True

        io_queue.update(6666, [])
        assert io_queue.display_blink_color == False

    def test_delivery_callback_order(self, io_queue, monkeypatch):
        delivery_callback_called = []

        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        io_queue.wait_for_event(0, lambda: None, lambda: delivery_callback_called.append(1))
        io_queue.wait_for_event(0, lambda: None, lambda: delivery_callback_called.append(2))
        io_queue.wait_for_event(0, lambda: None, lambda: delivery_callback_called.append(3))

        io_queue.update(6000, [])
        io_queue.update(11000, [])
        io_queue.update(16000, [])

        io_queue.handle_player_action()
        assert delivery_callback_called == [1, 2, 3]

    def test_event_arrives_when_max_time_elapsed_regardless_of_probability(self, io_queue, monkeypatch):
        arrival_callback_called = []

        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)

        io_queue.wait_for_event(0, lambda: arrival_callback_called.append(1), lambda: None)

        io_queue.update(6000, [])
        assert io_queue.event_count == 1
        assert arrival_callback_called == [1]

    def test_probabilistic_event_fires_between_min_and_max_time(self, io_queue, monkeypatch):
        """
        Test that probabilistic events can fire after min_waiting_time_ms
        but before max_waiting_time_ms has elapsed.
        """
        arrival_callback_called = []

        # Force random to always trigger the probabilistic event
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        io_queue.wait_for_event(0, lambda: arrival_callback_called.append(1), lambda: None)

        # Update at 2500ms - this is after min_time (1000ms) but before max_time (5000ms)
        # The probabilistic event should fire here
        io_queue.update(2500, [])

        # The event should have arrived via probabilistic path
        assert io_queue.event_count == 1
        assert arrival_callback_called == [1]

    def test_event_arrival_via_max_time_emits_io_queue_event(self, io_queue, monkeypatch):
        """Test that IO_QUEUE event is emitted when event arrives via max waiting time."""
        import game_monitor

        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: max)

        io_queue.wait_for_event(0, lambda: None, lambda: None)

        game_monitor.clear_events()

        io_queue.update(6000, [])

        events = game_monitor.get_events()
        io_queue_events = [e for e in events if e.etype == 'IO_QUEUE']
        assert len(io_queue_events) == 1
        assert io_queue_events[0].io_count == 1
