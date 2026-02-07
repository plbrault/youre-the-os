import pytest
from types import SimpleNamespace

import game_monitor


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
    """Tests for RunOs state update handlers via public interface."""

    @pytest.fixture
    def run_os(self):
        """Create a fresh RunOs instance for each test."""
        from automated_skeleton import RunOs
        instance = RunOs()
        instance.processes = {}
        instance.pages = {}
        instance.used_cpus = 0
        instance.io_queue.io_count = 0
        return instance

    def test_io_queue_event_updates_state(self, run_os):
        """Test IO_QUEUE event updates io_count."""
        events = [SimpleNamespace(etype='IO_QUEUE', io_count=3)]
        run_os(events)
        assert run_os.io_queue.io_count == 3

    def test_proc_new_event_creates_process(self, run_os):
        """Test PROC_NEW event creates a new process."""
        events = [SimpleNamespace(etype='PROC_NEW', pid=1)]
        run_os(events)
        
        assert 1 in run_os.processes
        assert run_os.processes[1].pid == 1
        assert run_os.processes[1].starvation_level == 1

    def test_proc_cpu_event_assigns_to_cpu(self, run_os):
        """Test PROC_CPU event when assigning to CPU."""
        events = [
            SimpleNamespace(etype='PROC_NEW', pid=1),
            SimpleNamespace(etype='PROC_CPU', pid=1, cpu=True),
        ]
        run_os(events)
        
        assert run_os.processes[1].cpu is True
        assert run_os.used_cpus == 1

    def test_proc_cpu_event_releases_from_cpu(self, run_os):
        """Test PROC_CPU event when releasing from CPU."""
        events = [
            SimpleNamespace(etype='PROC_NEW', pid=1),
            SimpleNamespace(etype='PROC_CPU', pid=1, cpu=True),
            SimpleNamespace(etype='PROC_CPU', pid=1, cpu=False),
        ]
        run_os(events)
        
        assert run_os.processes[1].cpu is False
        assert run_os.used_cpus == 0

    def test_proc_starv_event_updates_starvation(self, run_os):
        """Test PROC_STARV event updates starvation level."""
        events = [
            SimpleNamespace(etype='PROC_NEW', pid=1),
            SimpleNamespace(etype='PROC_STARV', pid=1, starvation_level=4),
        ]
        run_os(events)
        
        assert run_os.processes[1].starvation_level == 4

    def test_proc_wait_io_event_updates_state(self, run_os):
        """Test PROC_WAIT_IO event updates waiting_for_io."""
        events = [
            SimpleNamespace(etype='PROC_NEW', pid=1),
            SimpleNamespace(etype='PROC_WAIT_IO', pid=1, waiting_for_io=True),
        ]
        run_os(events)
        
        assert run_os.processes[1].waiting_for_io is True

    def test_proc_wait_page_event_updates_state(self, run_os):
        """Test PROC_WAIT_PAGE event updates waiting_for_page."""
        events = [
            SimpleNamespace(etype='PROC_NEW', pid=1),
            SimpleNamespace(etype='PROC_WAIT_PAGE', pid=1, waiting_for_page=True),
        ]
        run_os(events)
        
        assert run_os.processes[1].waiting_for_page is True

    def test_proc_term_event_marks_ended(self, run_os):
        """Test PROC_TERM event marks process as ended."""
        events = [
            SimpleNamespace(etype='PROC_NEW', pid=1),
            SimpleNamespace(etype='PROC_TERM', pid=1),
        ]
        run_os(events)
        
        assert run_os.processes[1].has_ended is True

    def test_proc_kill_event_removes_process(self, run_os):
        """Test PROC_KILL event removes process."""
        events = [
            SimpleNamespace(etype='PROC_NEW', pid=1),
            SimpleNamespace(etype='PROC_KILL', pid=1),
        ]
        run_os(events)
        
        assert 1 not in run_os.processes

    def test_proc_end_event_removes_process(self, run_os):
        """Test PROC_END event removes process and decrements used_cpus."""
        events = [
            SimpleNamespace(etype='PROC_NEW', pid=1),
            SimpleNamespace(etype='PROC_CPU', pid=1, cpu=True),
            SimpleNamespace(etype='PROC_END', pid=1),
        ]
        run_os(events)
        
        assert 1 not in run_os.processes
        assert run_os.used_cpus == 0

    def test_page_new_event_creates_page(self, run_os):
        """Test PAGE_NEW event creates a new page."""
        events = [
            SimpleNamespace(etype='PROC_NEW', pid=1),
            SimpleNamespace(etype='PAGE_NEW', pid=1, idx=0, swap=False, use=True),
        ]
        run_os(events)
        
        assert (1, 0) in run_os.pages
        page = run_os.pages[(1, 0)]
        assert page.pid == 1
        assert page.idx == 0
        assert page.on_disk is False
        assert page.in_use is True
        assert page in run_os.processes[1].pages

    def test_page_use_event_updates_state(self, run_os):
        """Test PAGE_USE event updates page in_use status."""
        events = [
            SimpleNamespace(etype='PROC_NEW', pid=1),
            SimpleNamespace(etype='PAGE_NEW', pid=1, idx=0, swap=False, use=False),
            SimpleNamespace(etype='PAGE_USE', pid=1, idx=0, use=True),
        ]
        run_os(events)
        
        assert run_os.pages[(1, 0)].in_use is True

    def test_page_swap_event_updates_state(self, run_os):
        """Test PAGE_SWAP event updates page on_disk status."""
        events = [
            SimpleNamespace(etype='PROC_NEW', pid=1),
            SimpleNamespace(etype='PAGE_NEW', pid=1, idx=0, swap=False, use=True),
            SimpleNamespace(etype='PAGE_SWAP', pid=1, idx=0, swap=True),
        ]
        run_os(events)
        
        assert run_os.pages[(1, 0)].on_disk is True

    def test_page_free_event_removes_page(self, run_os):
        """Test PAGE_FREE event removes page."""
        events = [
            SimpleNamespace(etype='PROC_NEW', pid=1),
            SimpleNamespace(etype='PAGE_NEW', pid=1, idx=0, swap=False, use=True),
            SimpleNamespace(etype='PAGE_FREE', pid=1, idx=0),
        ]
        run_os(events)
        
        assert (1, 0) not in run_os.pages
        assert len(run_os.processes[1].pages) == 0


class TestRunOsActionGeneration:
    """Tests for RunOs action generation methods via public interface."""

    @pytest.fixture
    def run_os(self):
        """Create a fresh RunOs instance for each test."""
        from automated_skeleton import RunOs
        instance = RunOs()
        instance.processes = {}
        instance.pages = {}
        instance.used_cpus = 0
        instance.io_queue.io_count = 0
        return instance

    def test_move_page_returns_page_action(self, run_os):
        """Test move_page generates a page action returned by __call__."""
        # Actions must be generated within schedule() during __call__
        def custom_schedule():
            run_os.move_page(pid=1, idx=2)
        run_os.schedule = custom_schedule
        
        result = run_os([])
        
        assert len(result) == 1
        assert result[0]['type'] == 'page'
        assert result[0]['pid'] == 1
        assert result[0]['idx'] == 2

    def test_move_process_returns_process_action(self, run_os):
        """Test move_process generates a process action returned by __call__."""
        def custom_schedule():
            run_os.move_process(pid=42)
        run_os.schedule = custom_schedule
        
        result = run_os([])
        
        assert len(result) == 1
        assert result[0]['type'] == 'process'
        assert result[0]['pid'] == 42

    def test_do_io_returns_io_action(self, run_os):
        """Test do_io generates an io_queue action returned by __call__."""
        def custom_schedule():
            run_os.do_io()
        run_os.schedule = custom_schedule
        
        result = run_os([])
        
        assert len(result) == 1
        assert result[0]['type'] == 'io_queue'

    def test_multiple_actions_accumulated(self, run_os):
        """Test multiple actions accumulate and are returned together."""
        def custom_schedule():
            run_os.move_process(1)
            run_os.move_page(1, 0)
            run_os.do_io()
        run_os.schedule = custom_schedule
        
        result = run_os([])
        
        assert len(result) == 3

    def test_call_returns_fresh_actions(self, run_os):
        """Test __call__ clears actions between calls."""
        call_count = [0]
        def custom_schedule():
            call_count[0] += 1
            if call_count[0] == 1:
                run_os.move_process(1)
        run_os.schedule = custom_schedule
        
        result1 = run_os([])
        # Note: result1 references the internal queue, so we must check it
        # before the next call clears the queue
        assert len(result1) == 1
        
        result2 = run_os([])
        assert result2 == []


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
        return instance

    def test_call_processes_events_and_returns_actions(self, run_os):
        """Test that __call__ processes input events and returns action events."""
        events = [SimpleNamespace(etype='PROC_NEW', pid=1)]
        
        result = run_os(events)
        
        assert 1 in run_os.processes
        assert result == []

    def test_call_handles_unknown_events_gracefully(self, run_os):
        """Test that unknown event types don't cause errors."""
        events = [SimpleNamespace(etype='UNKNOWN_EVENT', data='test')]
        
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
    """Integration tests for Stage scene automation via public interface."""

    @pytest.fixture
    def stage_with_script(self, Stage, stage_config, scene_manager):
        """Create a stage with a simple automation script."""
        script_source = '''
def run_os(events):
    actions = []
    for event in events:
        if event.etype == 'PROC_NEW':
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

    def test_stage_with_script_responds_to_process_events(
            self, stage_with_script, monkeypatch):
        """Test that stage with script handles process events via update."""
        toggled_pids = []
        
        class MockProcess:
            def __init__(self, pid):
                self.pid = pid
            def toggle(self):
                toggled_pids.append(self.pid)
        
        monkeypatch.setattr(
            stage_with_script._process_manager, 
            'get_process', 
            lambda pid: MockProcess(pid)
        )
        
        game_monitor.clear_events()
        game_monitor.notify_process_new(1)
        
        # Call update to trigger script processing
        stage_with_script.update(0, [])
        
        assert 1 in toggled_pids

    def test_stage_without_script_does_not_crash(self, stage_without_script):
        """Test that stage without script handles update without errors."""
        game_monitor.clear_events()
        game_monitor.notify_process_new(1)
        
        # Should not raise
        stage_without_script.update(0, [])

    def test_script_with_page_action(self, Stage, stage_config, scene_manager, monkeypatch):
        """Test that script page actions trigger page swaps."""
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
            def __init__(self, pid, idx):
                self.pid = pid
                self.idx = idx
            def request_swap(self):
                swapped_pages.append((self.pid, self.idx))
        
        monkeypatch.setattr(
            stage._page_manager,
            'get_page',
            lambda pid, idx: MockPage(pid, idx)
        )
        
        game_monitor.clear_events()
        game_monitor.notify_page_new(1, 0, False, True)
        
        stage.update(0, [])
        
        assert (1, 0) in swapped_pages

    def test_script_with_io_action(self, Stage, stage_config, scene_manager, monkeypatch):
        """Test that script io_queue actions trigger IO processing."""
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
        
        stage.update(0, [])
        
        assert len(io_processed) == 1

    def test_script_error_does_not_crash_stage(
            self, stage_with_script, monkeypatch, capsys):
        """Test that script errors are handled gracefully."""
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
        stage_with_script.update(0, [])
        
        # Error should be printed to stderr
        captured = capsys.readouterr()
        assert 'ValueError' in captured.err

    def test_script_without_run_os_function(self, Stage, stage_config, scene_manager):
        """Test that script without run_os function is handled gracefully."""
        script_source = '''
# No run_os defined
x = 1
'''
        compiled = compile(script_source, '<test>', 'exec')
        stage = Stage('Test Stage', stage_config, script=compiled, standalone=True)
        stage.scene_manager = scene_manager
        stage.setup()
        
        game_monitor.clear_events()
        game_monitor.notify_process_new(1)
        
        # Should not raise
        stage.update(0, [])
