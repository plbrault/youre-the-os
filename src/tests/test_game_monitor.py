import pytest

import game_monitor

class TestGameMonitor:
    """Tests for the game_monitor module that collects game events."""

    def setup_method(self):
        """Clear events before each test."""
        game_monitor.clear_events()

    def teardown_method(self):
        """Clear events after each test."""
        game_monitor.clear_events()

    def test_clear_events(self):
        """Test that clear_events removes all events."""
        game_monitor.notify_process_new(1)
        game_monitor.notify_page_new(1, 0, False, True)
        assert len(game_monitor.get_events()) == 2
        game_monitor.clear_events()
        assert len(game_monitor.get_events()) == 0

    def test_get_events_returns_list(self):
        """Test that get_events returns a list."""
        events = game_monitor.get_events()
        assert isinstance(events, list)

    # IO Queue events
    def test_notify_io_event_count(self):
        """Test IO queue count event generation."""
        game_monitor.notify_io_event_count(5)
        events = game_monitor.get_events()
        assert len(events) == 1
        assert events[0].etype == 'IO_QUEUE'
        assert events[0].io_count == 5

    # Page events
    def test_notify_page_new(self):
        """Test new page event generation."""
        game_monitor.notify_page_new(pid=1, idx=0, swap=False, use=True)
        events = game_monitor.get_events()
        assert len(events) == 1
        assert events[0].etype == 'PAGE_NEW'
        assert events[0].pid == 1
        assert events[0].idx == 0
        assert events[0].swap is False
        assert events[0].use is True

    def test_notify_page_use(self):
        """Test page use status change event generation."""
        game_monitor.notify_page_use(pid=1, idx=2, use=True)
        events = game_monitor.get_events()
        assert len(events) == 1
        assert events[0].etype == 'PAGE_USE'
        assert events[0].pid == 1
        assert events[0].idx == 2
        assert events[0].use is True

    def test_notify_page_swap_queue(self):
        """Test page swap queue event generation."""
        game_monitor.notify_page_swap_queue(pid=1, idx=0, waiting=True)
        events = game_monitor.get_events()
        assert len(events) == 1
        assert events[0].etype == 'PAGE_SWAP_QUEUE'
        assert events[0].pid == 1
        assert events[0].idx == 0
        assert events[0].waiting is True

    def test_notify_page_swap_queue_cancelled(self):
        """Test page swap queue cancelled event generation."""
        game_monitor.notify_page_swap_queue(pid=1, idx=0, waiting=False)
        events = game_monitor.get_events()
        assert len(events) == 1
        assert events[0].etype == 'PAGE_SWAP_QUEUE'
        assert events[0].pid == 1
        assert events[0].idx == 0
        assert events[0].waiting is False

    def test_notify_page_swap_start(self):
        """Test page swap start event generation."""
        game_monitor.notify_page_swap_start(pid=1, idx=0)
        events = game_monitor.get_events()
        assert len(events) == 1
        assert events[0].etype == 'PAGE_SWAP_START'
        assert events[0].pid == 1
        assert events[0].idx == 0

    def test_notify_page_swap(self):
        """Test page swap event generation."""
        game_monitor.notify_page_swap(pid=1, idx=0, swap=True)
        events = game_monitor.get_events()
        assert len(events) == 1
        assert events[0].etype == 'PAGE_SWAP'
        assert events[0].pid == 1
        assert events[0].idx == 0
        assert events[0].swap is True

    def test_notify_page_free(self):
        """Test page free event generation."""
        game_monitor.notify_page_free(pid=1, idx=0)
        events = game_monitor.get_events()
        assert len(events) == 1
        assert events[0].etype == 'PAGE_FREE'
        assert events[0].pid == 1
        assert events[0].idx == 0

    # Process events
    def test_notify_process_new(self):
        """Test new process event generation."""
        game_monitor.notify_process_new(pid=42)
        events = game_monitor.get_events()
        assert len(events) == 1
        assert events[0].etype == 'PROC_NEW'
        assert events[0].pid == 42

    def test_notify_process_cpu(self):
        """Test process CPU status change event generation."""
        game_monitor.notify_process_cpu(pid=1, cpu=True)
        events = game_monitor.get_events()
        assert len(events) == 1
        assert events[0].etype == 'PROC_CPU'
        assert events[0].pid == 1
        assert events[0].cpu is True

    def test_notify_process_starvation(self):
        """Test process starvation level event generation."""
        game_monitor.notify_process_starvation(pid=1, level=3, time_to_termination=30000)
        events = game_monitor.get_events()
        assert len(events) == 1
        assert events[0].etype == 'PROC_STARV'
        assert events[0].pid == 1
        assert events[0].starvation_level == 3
        assert events[0].time_to_termination == 30000

    def test_notify_process_wait_io(self):
        """Test process waiting for IO event generation."""
        game_monitor.notify_process_wait_io(pid=1, value=True)
        events = game_monitor.get_events()
        assert len(events) == 1
        assert events[0].etype == 'PROC_WAIT_IO'
        assert events[0].pid == 1
        assert events[0].waiting_for_io is True

    def test_notify_process_wait_page(self):
        """Test process waiting for page event generation."""
        game_monitor.notify_process_wait_page(pid=1, value=True)
        events = game_monitor.get_events()
        assert len(events) == 1
        assert events[0].etype == 'PROC_WAIT_PAGE'
        assert events[0].pid == 1
        assert events[0].waiting_for_page is True

    def test_notify_process_terminated(self):
        """Test process terminated event generation."""
        game_monitor.notify_process_terminated(pid=1)
        events = game_monitor.get_events()
        assert len(events) == 1
        assert events[0].etype == 'PROC_TERM'
        assert events[0].pid == 1

    def test_notify_process_killed(self):
        """Test process killed event generation."""
        game_monitor.notify_process_killed(pid=1)
        events = game_monitor.get_events()
        assert len(events) == 1
        assert events[0].etype == 'PROC_KILL'
        assert events[0].pid == 1

    def test_notify_process_end(self):
        """Test process end event generation."""
        game_monitor.notify_process_end(pid=1)
        events = game_monitor.get_events()
        assert len(events) == 1
        assert events[0].etype == 'PROC_END'
        assert events[0].pid == 1

    def test_multiple_events_in_sequence(self):
        """Test that multiple events accumulate correctly."""
        game_monitor.notify_process_new(1)
        game_monitor.notify_page_new(1, 0, False, True)
        game_monitor.notify_process_cpu(1, True)
        
        events = game_monitor.get_events()
        assert len(events) == 3
        assert events[0].etype == 'PROC_NEW'
        assert events[1].etype == 'PAGE_NEW'
        assert events[2].etype == 'PROC_CPU'
