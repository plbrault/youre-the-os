import pytest

import game_monitor

class TestGameMonitor:
    """Tests for the game_monitor module that collects game notifications."""

    def setup_method(self):
        """Clear notifications before each test."""
        game_monitor.clear_notifications()

    def teardown_method(self):
        """Clear notifications after each test."""
        game_monitor.clear_notifications()

    def test_clear_notifications(self):
        """Test that clear_notifications removes all notifications."""
        game_monitor.notify_process_new(1)
        game_monitor.notify_page_new(1, 0, False, True)
        assert len(game_monitor.get_notifications()) == 2
        game_monitor.clear_notifications()
        assert len(game_monitor.get_notifications()) == 0

    def test_get_notifications_returns_list(self):
        """Test that get_notifications returns a list."""
        notifications = game_monitor.get_notifications()
        assert isinstance(notifications, list)

    # IO Queue notifications
    def test_notify_io_event_count(self):
        """Test IO queue count notification generation."""
        game_monitor.notify_io_event_count(5)
        notifications = game_monitor.get_notifications()
        assert len(notifications) == 1
        assert notifications[0].etype == 'IO_QUEUE'
        assert notifications[0].io_count == 5

    # Page notifications
    def test_notify_page_new(self):
        """Test new page notification generation."""
        game_monitor.notify_page_new(pid=1, idx=0, swap=False, use=True)
        notifications = game_monitor.get_notifications()
        assert len(notifications) == 1
        assert notifications[0].etype == 'PAGE_NEW'
        assert notifications[0].pid == 1
        assert notifications[0].idx == 0
        assert notifications[0].swap is False
        assert notifications[0].use is True

    def test_notify_page_use(self):
        """Test page use status change notification generation."""
        game_monitor.notify_page_use(pid=1, idx=2, use=True)
        notifications = game_monitor.get_notifications()
        assert len(notifications) == 1
        assert notifications[0].etype == 'PAGE_USE'
        assert notifications[0].pid == 1
        assert notifications[0].idx == 2
        assert notifications[0].use is True

    def test_notify_page_swap_queue(self):
        """Test page swap queue notification generation."""
        game_monitor.notify_page_swap_queue(pid=1, idx=0, waiting=True)
        notifications = game_monitor.get_notifications()
        assert len(notifications) == 1
        assert notifications[0].etype == 'PAGE_SWAP_QUEUE'
        assert notifications[0].pid == 1
        assert notifications[0].idx == 0
        assert notifications[0].waiting is True

    def test_notify_page_swap_queue_cancelled(self):
        """Test page swap queue cancelled notification generation."""
        game_monitor.notify_page_swap_queue(pid=1, idx=0, waiting=False)
        notifications = game_monitor.get_notifications()
        assert len(notifications) == 1
        assert notifications[0].etype == 'PAGE_SWAP_QUEUE'
        assert notifications[0].pid == 1
        assert notifications[0].idx == 0
        assert notifications[0].waiting is False

    def test_notify_page_swap_start(self):
        """Test page swap start notification generation."""
        game_monitor.notify_page_swap_start(pid=1, idx=0)
        notifications = game_monitor.get_notifications()
        assert len(notifications) == 1
        assert notifications[0].etype == 'PAGE_SWAP_START'
        assert notifications[0].pid == 1
        assert notifications[0].idx == 0

    def test_notify_page_swap(self):
        """Test page swap notification generation."""
        game_monitor.notify_page_swap(pid=1, idx=0, swap=True)
        notifications = game_monitor.get_notifications()
        assert len(notifications) == 1
        assert notifications[0].etype == 'PAGE_SWAP'
        assert notifications[0].pid == 1
        assert notifications[0].idx == 0
        assert notifications[0].swap is True

    def test_notify_page_free(self):
        """Test page free notification generation."""
        game_monitor.notify_page_free(pid=1, idx=0)
        notifications = game_monitor.get_notifications()
        assert len(notifications) == 1
        assert notifications[0].etype == 'PAGE_FREE'
        assert notifications[0].pid == 1
        assert notifications[0].idx == 0

    # Process notifications
    def test_notify_process_new(self):
        """Test new process notification generation."""
        game_monitor.notify_process_new(pid=42)
        notifications = game_monitor.get_notifications()
        assert len(notifications) == 1
        assert notifications[0].etype == 'PROC_NEW'
        assert notifications[0].pid == 42

    def test_notify_process_cpu(self):
        """Test process CPU status change notification generation."""
        game_monitor.notify_process_cpu(pid=1, cpu=True)
        notifications = game_monitor.get_notifications()
        assert len(notifications) == 1
        assert notifications[0].etype == 'PROC_CPU'
        assert notifications[0].pid == 1
        assert notifications[0].cpu is True

    def test_notify_process_starvation(self):
        """Test process starvation level notification generation."""
        game_monitor.notify_process_starvation(pid=1, level=3, time_to_termination=30000)
        notifications = game_monitor.get_notifications()
        assert len(notifications) == 1
        assert notifications[0].etype == 'PROC_STARV'
        assert notifications[0].pid == 1
        assert notifications[0].starvation_level == 3
        assert notifications[0].time_to_termination == 30000

    def test_notify_process_wait_io(self):
        """Test process waiting for IO notification generation."""
        game_monitor.notify_process_wait_io(pid=1, value=True)
        notifications = game_monitor.get_notifications()
        assert len(notifications) == 1
        assert notifications[0].etype == 'PROC_WAIT_IO'
        assert notifications[0].pid == 1
        assert notifications[0].waiting_for_io is True

    def test_notify_process_wait_page(self):
        """Test process waiting for page notification generation."""
        game_monitor.notify_process_wait_page(pid=1, value=True)
        notifications = game_monitor.get_notifications()
        assert len(notifications) == 1
        assert notifications[0].etype == 'PROC_WAIT_PAGE'
        assert notifications[0].pid == 1
        assert notifications[0].waiting_for_page is True

    def test_notify_process_terminated(self):
        """Test process terminated notification generation."""
        game_monitor.notify_process_terminated(pid=1)
        notifications = game_monitor.get_notifications()
        assert len(notifications) == 1
        assert notifications[0].etype == 'PROC_TERM'
        assert notifications[0].pid == 1

    def test_notify_process_killed(self):
        """Test process killed notification generation."""
        game_monitor.notify_process_killed(pid=1)
        notifications = game_monitor.get_notifications()
        assert len(notifications) == 1
        assert notifications[0].etype == 'PROC_KILL'
        assert notifications[0].pid == 1

    def test_notify_process_end(self):
        """Test process end notification generation."""
        game_monitor.notify_process_end(pid=1)
        notifications = game_monitor.get_notifications()
        assert len(notifications) == 1
        assert notifications[0].etype == 'PROC_END'
        assert notifications[0].pid == 1

    def test_multiple_notifications_in_sequence(self):
        """Test that multiple notifications accumulate correctly."""
        game_monitor.notify_process_new(1)
        game_monitor.notify_page_new(1, 0, False, True)
        game_monitor.notify_process_cpu(1, True)
        
        notifications = game_monitor.get_notifications()
        assert len(notifications) == 3
        assert notifications[0].etype == 'PROC_NEW'
        assert notifications[1].etype == 'PAGE_NEW'
        assert notifications[2].etype == 'PROC_CPU'
