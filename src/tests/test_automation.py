"""Tests for the automation system.

This module tests:
1. game_monitor - event generation and collection
2. RunOs skeleton - state tracking and action generation
3. Stage integration - script execution and event processing
"""

import pytest
from types import SimpleNamespace

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
        assert len(game_monitor.get_events()) == 1
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
        game_monitor.notify_process_starvation(pid=1, level=3)
        events = game_monitor.get_events()
        assert len(events) == 1
        assert events[0].etype == 'PROC_STARV'
        assert events[0].pid == 1
        assert events[0].starvation_level == 3

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


class TestRunOsDataClasses:
    """Tests for the data classes used in the RunOs skeleton."""

    def test_page_dataclass(self):
        """Test Page dataclass properties."""
        # Import locally to avoid polluting module namespace
        import sys
        sys.path.insert(0, '..')
        from automated_skeleton import Page
        
        page = Page(pid=1, idx=2, on_disk=False, in_use=True)
        assert page.pid == 1
        assert page.idx == 2
        assert page.on_disk is False
        assert page.in_use is True
        assert page.key == (1, 2)

    def test_page_equality(self):
        """Test Page equality comparison with tuple."""
        from automated_skeleton import Page
        
        page = Page(pid=1, idx=2, on_disk=False, in_use=True)
        assert page == (1, 2)
        assert not (page == (1, 3))

    def test_process_dataclass(self):
        """Test Process dataclass properties."""
        from automated_skeleton import Process
        
        process = Process(pid=42)
        assert process.pid == 42
        assert process.cpu is False
        assert process.starvation_level == 1
        assert process.waiting_for_io is False
        assert process.waiting_for_page is False
        assert process.has_ended is False
        assert process.pages == []
        assert process.key == 42

    def test_process_equality(self):
        """Test Process equality comparison with int."""
        from automated_skeleton import Process
        
        process = Process(pid=42)
        assert process == 42
        assert not (process == 43)

    def test_io_queue_dataclass(self):
        """Test IoQueue dataclass."""
        from automated_skeleton import IoQueue
        
        io_queue = IoQueue()
        assert io_queue.io_count == 0
        
        io_queue.io_count = 5
        assert io_queue.io_count == 5


class TestRunOsStateUpdates:
    """Tests for RunOs state update handlers."""

    @pytest.fixture
    def run_os(self):
        """Create a fresh RunOs instance for each test."""
        from automated_skeleton import RunOs
        # Create a new instance with fresh state
        instance = RunOs()
        instance.processes = {}
        instance.pages = {}
        instance.used_cpus = 0
        instance.io_queue.io_count = 0
        return instance

    def test_update_io_queue(self, run_os):
        """Test IO_QUEUE event updates io_count."""
        event = SimpleNamespace(etype='IO_QUEUE', io_count=3)
        run_os._update_IO_QUEUE(event)
        assert run_os.io_queue.io_count == 3

    def test_update_proc_new(self, run_os):
        """Test PROC_NEW event creates a new process."""
        event = SimpleNamespace(etype='PROC_NEW', pid=1)
        run_os._update_PROC_NEW(event)
        
        assert 1 in run_os.processes
        assert run_os.processes[1].pid == 1
        assert run_os.processes[1].starvation_level == 1

    def test_update_proc_cpu_assign(self, run_os):
        """Test PROC_CPU event when assigning to CPU."""
        # First create the process
        run_os._update_PROC_NEW(SimpleNamespace(etype='PROC_NEW', pid=1))
        
        # Assign to CPU
        event = SimpleNamespace(etype='PROC_CPU', pid=1, cpu=True)
        run_os._update_PROC_CPU(event)
        
        assert run_os.processes[1].cpu is True
        assert run_os.used_cpus == 1

    def test_update_proc_cpu_release(self, run_os):
        """Test PROC_CPU event when releasing from CPU."""
        # Create and assign process
        run_os._update_PROC_NEW(SimpleNamespace(etype='PROC_NEW', pid=1))
        run_os._update_PROC_CPU(SimpleNamespace(etype='PROC_CPU', pid=1, cpu=True))
        
        # Release from CPU
        event = SimpleNamespace(etype='PROC_CPU', pid=1, cpu=False)
        run_os._update_PROC_CPU(event)
        
        assert run_os.processes[1].cpu is False
        assert run_os.used_cpus == 0

    def test_update_proc_starv(self, run_os):
        """Test PROC_STARV event updates starvation level."""
        run_os._update_PROC_NEW(SimpleNamespace(etype='PROC_NEW', pid=1))
        
        event = SimpleNamespace(etype='PROC_STARV', pid=1, starvation_level=4)
        run_os._update_PROC_STARV(event)
        
        assert run_os.processes[1].starvation_level == 4

    def test_update_proc_wait_io(self, run_os):
        """Test PROC_WAIT_IO event updates waiting_for_io."""
        run_os._update_PROC_NEW(SimpleNamespace(etype='PROC_NEW', pid=1))
        
        event = SimpleNamespace(etype='PROC_WAIT_IO', pid=1, waiting_for_io=True)
        run_os._update_PROC_WAIT_IO(event)
        
        assert run_os.processes[1].waiting_for_io is True

    def test_update_proc_wait_page(self, run_os):
        """Test PROC_WAIT_PAGE event updates waiting_for_page."""
        run_os._update_PROC_NEW(SimpleNamespace(etype='PROC_NEW', pid=1))
        
        event = SimpleNamespace(etype='PROC_WAIT_PAGE', pid=1, waiting_for_page=True)
        run_os._update_PROC_WAIT_PAGE(event)
        
        assert run_os.processes[1].waiting_for_page is True

    def test_update_proc_term(self, run_os):
        """Test PROC_TERM event marks process as ended."""
        run_os._update_PROC_NEW(SimpleNamespace(etype='PROC_NEW', pid=1))
        
        event = SimpleNamespace(etype='PROC_TERM', pid=1)
        run_os._update_PROC_TERM(event)
        
        assert run_os.processes[1].has_ended is True

    def test_update_proc_kill(self, run_os):
        """Test PROC_KILL event removes process."""
        run_os._update_PROC_NEW(SimpleNamespace(etype='PROC_NEW', pid=1))
        
        event = SimpleNamespace(etype='PROC_KILL', pid=1)
        run_os._update_PROC_KILL(event)
        
        assert 1 not in run_os.processes

    def test_update_proc_end(self, run_os):
        """Test PROC_END event removes process and decrements used_cpus."""
        run_os._update_PROC_NEW(SimpleNamespace(etype='PROC_NEW', pid=1))
        run_os._update_PROC_CPU(SimpleNamespace(etype='PROC_CPU', pid=1, cpu=True))
        
        event = SimpleNamespace(etype='PROC_END', pid=1)
        run_os._update_PROC_END(event)
        
        assert 1 not in run_os.processes
        assert run_os.used_cpus == 0

    def test_update_page_new(self, run_os):
        """Test PAGE_NEW event creates a new page."""
        # First create a process
        run_os._update_PROC_NEW(SimpleNamespace(etype='PROC_NEW', pid=1))
        
        event = SimpleNamespace(etype='PAGE_NEW', pid=1, idx=0, swap=False, use=True)
        run_os._update_PAGE_NEW(event)
        
        assert (1, 0) in run_os.pages
        page = run_os.pages[(1, 0)]
        assert page.pid == 1
        assert page.idx == 0
        assert page.on_disk is False
        assert page.in_use is True
        assert page in run_os.processes[1].pages

    def test_update_page_use(self, run_os):
        """Test PAGE_USE event updates page in_use status."""
        run_os._update_PROC_NEW(SimpleNamespace(etype='PROC_NEW', pid=1))
        run_os._update_PAGE_NEW(SimpleNamespace(etype='PAGE_NEW', pid=1, idx=0, swap=False, use=False))
        
        event = SimpleNamespace(etype='PAGE_USE', pid=1, idx=0, use=True)
        run_os._update_PAGE_USE(event)
        
        assert run_os.pages[(1, 0)].in_use is True

    def test_update_page_swap(self, run_os):
        """Test PAGE_SWAP event updates page on_disk status."""
        run_os._update_PROC_NEW(SimpleNamespace(etype='PROC_NEW', pid=1))
        run_os._update_PAGE_NEW(SimpleNamespace(etype='PAGE_NEW', pid=1, idx=0, swap=False, use=True))
        
        event = SimpleNamespace(etype='PAGE_SWAP', pid=1, idx=0, swap=True)
        run_os._update_PAGE_SWAP(event)
        
        assert run_os.pages[(1, 0)].on_disk is True

    def test_update_page_free(self, run_os):
        """Test PAGE_FREE event removes page."""
        run_os._update_PROC_NEW(SimpleNamespace(etype='PROC_NEW', pid=1))
        run_os._update_PAGE_NEW(SimpleNamespace(etype='PAGE_NEW', pid=1, idx=0, swap=False, use=True))
        
        event = SimpleNamespace(etype='PAGE_FREE', pid=1, idx=0)
        run_os._update_PAGE_FREE(event)
        
        assert (1, 0) not in run_os.pages
        assert len(run_os.processes[1].pages) == 0


class TestRunOsActionGeneration:
    """Tests for RunOs action generation methods."""

    @pytest.fixture
    def run_os(self):
        """Create a fresh RunOs instance for each test."""
        from automated_skeleton import RunOs
        instance = RunOs()
        instance.processes = {}
        instance.pages = {}
        instance.used_cpus = 0
        instance.io_queue.io_count = 0
        instance._event_queue = []
        return instance

    def test_move_page_creates_event(self, run_os):
        """Test move_page adds a page event to the queue."""
        run_os.move_page(pid=1, idx=2)
        
        assert len(run_os._event_queue) == 1
        event = run_os._event_queue[0]
        assert event['type'] == 'page'
        assert event['pid'] == 1
        assert event['idx'] == 2

    def test_move_process_creates_event(self, run_os):
        """Test move_process adds a process event to the queue."""
        run_os.move_process(pid=42)
        
        assert len(run_os._event_queue) == 1
        event = run_os._event_queue[0]
        assert event['type'] == 'process'
        assert event['pid'] == 42

    def test_do_io_creates_event(self, run_os):
        """Test do_io adds an io_queue event."""
        run_os.do_io()
        
        assert len(run_os._event_queue) == 1
        event = run_os._event_queue[0]
        assert event['type'] == 'io_queue'

    def test_multiple_actions(self, run_os):
        """Test multiple actions accumulate correctly."""
        run_os.move_process(1)
        run_os.move_page(1, 0)
        run_os.do_io()
        
        assert len(run_os._event_queue) == 3

    def test_call_clears_event_queue(self, run_os):
        """Test __call__ clears the event queue before processing."""
        # Add some events manually
        run_os._event_queue.append({'type': 'old_event'})
        
        # Call with empty events
        result = run_os([])
        
        # Queue should be cleared and return empty
        assert result == []


class TestRunOsIntegration:
    """Integration tests for RunOs __call__ method."""

    @pytest.fixture
    def run_os(self):
        """Create a fresh RunOs instance for each test."""
        from automated_skeleton import RunOs
        instance = RunOs()
        instance.processes = {}
        instance.pages = {}
        instance.used_cpus = 0
        instance.io_queue.io_count = 0
        instance._event_queue = []
        return instance

    def test_call_processes_events_and_returns_actions(self, run_os):
        """Test that __call__ processes input events and returns action events."""
        # Simulate a new process event
        events = [SimpleNamespace(etype='PROC_NEW', pid=1)]
        
        result = run_os(events)
        
        # Process should be tracked
        assert 1 in run_os.processes
        # No actions by default (schedule is empty)
        assert result == []

    def test_call_handles_unknown_events_gracefully(self, run_os):
        """Test that unknown event types don't cause errors."""
        events = [SimpleNamespace(etype='UNKNOWN_EVENT', data='test')]
        
        # Should not raise
        result = run_os(events)
        assert result == []

    def test_full_process_lifecycle(self, run_os):
        """Test a complete process lifecycle through events."""
        events = [
            SimpleNamespace(etype='PROC_NEW', pid=1),
            SimpleNamespace(etype='PAGE_NEW', pid=1, idx=0, swap=False, use=False),
            SimpleNamespace(etype='PROC_CPU', pid=1, cpu=True),
            SimpleNamespace(etype='PAGE_USE', pid=1, idx=0, use=True),
            SimpleNamespace(etype='PROC_TERM', pid=1),
            SimpleNamespace(etype='PAGE_USE', pid=1, idx=0, use=False),
            SimpleNamespace(etype='PROC_CPU', pid=1, cpu=False),
        ]
        
        run_os(events)
        
        # Process should still exist (not ended yet)
        assert 1 in run_os.processes
        assert run_os.processes[1].has_ended is True
        assert run_os.processes[1].cpu is False
        assert run_os.used_cpus == 0

    def test_process_killed_cleans_up(self, run_os):
        """Test that PROC_KILL properly cleans up process and its pages."""
        events = [
            SimpleNamespace(etype='PROC_NEW', pid=1),
            SimpleNamespace(etype='PAGE_NEW', pid=1, idx=0, swap=False, use=True),
            SimpleNamespace(etype='PAGE_NEW', pid=1, idx=1, swap=False, use=True),
            SimpleNamespace(etype='PAGE_FREE', pid=1, idx=0),
            SimpleNamespace(etype='PAGE_FREE', pid=1, idx=1),
            SimpleNamespace(etype='PROC_KILL', pid=1),
        ]
        
        run_os(events)
        
        assert 1 not in run_os.processes
        assert (1, 0) not in run_os.pages
        assert (1, 1) not in run_os.pages


class TestStageAutomationIntegration:
    """Tests for Stage scene automation integration."""

    @pytest.fixture
    def stage_with_script(self, Stage, stage_config, scene_manager):
        """Create a stage with a simple automation script."""
        # Simple script that exposes a run_os function
        script_source = '''
def run_os(events):
    actions = []
    for event in events:
        if event.etype == 'PROC_NEW':
            # Respond to new process by toggling it
            actions.append({'type': 'process', 'pid': event.pid})
    return actions
'''
        compiled = compile(script_source, '<test>', 'exec')
        stage = Stage('Test Stage', stage_config, script=compiled, standalone=True)
        stage.scene_manager = scene_manager
        stage.setup()
        return stage

    @pytest.fixture
    def stage_without_script(self, Stage, stage_config, scene_manager):
        """Create a stage without an automation script."""
        stage = Stage('Test Stage', stage_config, script=None, standalone=True)
        stage.scene_manager = scene_manager
        stage.setup()
        return stage

    def test_stage_prepares_script_callback(self, stage_with_script):
        """Test that _prepare_automation_script sets up the callback."""
        assert stage_with_script._script_callback is not None
        assert callable(stage_with_script._script_callback)

    def test_stage_without_script_has_no_callback(self, stage_without_script):
        """Test that stage without script has no callback."""
        assert stage_without_script._script_callback is None

    def test_get_script_events_returns_empty_without_callback(self, stage_without_script):
        """Test _get_script_events returns empty list when no callback."""
        result = stage_without_script._get_script_events()
        assert result == []

    def test_script_receives_globals(self, Stage, stage_config, scene_manager):
        """Test that script receives expected global variables."""
        received_globals = {}
        script_source = '''
received_globals['num_cpus'] = num_cpus
received_globals['num_ram_pages'] = num_ram_pages
received_globals['num_swap_pages'] = num_swap_pages
def run_os(events):
    return []
'''
        # We need to pass the dict through the script
        script_source = f'''
def run_os(events):
    return []
# Store globals for testing
_test_globals = {{
    'num_cpus': num_cpus,
    'num_ram_pages': num_ram_pages,
    'num_swap_pages': num_swap_pages
}}
'''
        compiled = compile(script_source, '<test>', 'exec')
        stage = Stage('Test Stage', stage_config, script=compiled, standalone=True)
        stage.scene_manager = scene_manager
        stage.setup()
        
        # The script should have been executed with globals
        assert stage._script_callback is not None

    def test_script_with_missing_run_os(self, Stage, stage_config, scene_manager):
        """Test that script without run_os doesn't crash."""
        script_source = '''
# No run_os defined
x = 1
'''
        compiled = compile(script_source, '<test>', 'exec')
        stage = Stage('Test Stage', stage_config, script=compiled, standalone=True)
        stage.scene_manager = scene_manager
        stage.setup()
        
        # Should not have a callback
        assert stage._script_callback is None

    def test_process_script_events_handles_process_action(
            self, stage_with_script, monkeypatch):
        """Test _process_script_events handles process toggle actions."""
        # Mock the process manager
        toggled_pids = []
        
        class MockProcess:
            def toggle(self):
                toggled_pids.append(self.pid)
            pid = 1
        
        mock_process = MockProcess()
        monkeypatch.setattr(
            stage_with_script._process_manager, 
            'get_process', 
            lambda pid: mock_process
        )
        
        # Add a PROC_NEW event to game_monitor
        game_monitor.clear_events()
        game_monitor.notify_process_new(1)
        
        # Process script events
        stage_with_script._process_script_events()
        
        # The script should have responded with a toggle action
        assert 1 in toggled_pids

    def test_process_script_events_handles_page_action(
            self, Stage, stage_config, scene_manager, monkeypatch):
        """Test _process_script_events handles page swap actions."""
        script_source = '''
def run_os(events):
    actions = []
    for event in events:
        if event.etype == 'PAGE_NEW':
            actions.append({'type': 'page', 'pid': event.pid, 'idx': event.idx})
    return actions
'''
        compiled = compile(script_source, '<test>', 'exec')
        stage = Stage('Test Stage', stage_config, script=compiled, standalone=True)
        stage.scene_manager = scene_manager
        stage.setup()
        
        swapped_pages = []
        
        class MockPage:
            def request_swap(self):
                swapped_pages.append((self.pid, self.idx))
            pid = 1
            idx = 0
        
        mock_page = MockPage()
        monkeypatch.setattr(
            stage._page_manager,
            'get_page',
            lambda pid, idx: mock_page
        )
        
        game_monitor.clear_events()
        game_monitor.notify_page_new(1, 0, False, True)
        
        stage._process_script_events()
        
        assert (1, 0) in swapped_pages

    def test_process_script_events_handles_io_action(
            self, Stage, stage_config, scene_manager, monkeypatch):
        """Test _process_script_events handles io_queue actions."""
        script_source = '''
def run_os(events):
    actions = []
    for event in events:
        if event.etype == 'IO_QUEUE' and event.io_count > 0:
            actions.append({'type': 'io_queue'})
    return actions
'''
        compiled = compile(script_source, '<test>', 'exec')
        stage = Stage('Test Stage', stage_config, script=compiled, standalone=True)
        stage.scene_manager = scene_manager
        stage.setup()
        
        io_processed = []
        
        monkeypatch.setattr(
            stage._process_manager.io_queue,
            'process_events',
            lambda: io_processed.append(True)
        )
        
        game_monitor.clear_events()
        game_monitor.notify_io_event_count(5)
        
        stage._process_script_events()
        
        assert len(io_processed) == 1

    def test_process_script_events_handles_exceptions(
            self, stage_with_script, monkeypatch, capsys):
        """Test _process_script_events catches and logs exceptions."""
        def raise_error(pid):
            raise ValueError("Test error")
        
        monkeypatch.setattr(
            stage_with_script._process_manager,
            'get_process',
            raise_error
        )
        
        game_monitor.clear_events()
        game_monitor.notify_process_new(1)
        
        # Should not raise
        stage_with_script._process_script_events()
        
        # Error should be printed to stderr
        captured = capsys.readouterr()
        assert 'ValueError' in captured.err
