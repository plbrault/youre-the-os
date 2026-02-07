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
        from automation.api import Page
        
        page = Page(pid=1, idx=2, on_disk=False, in_use=True)
        assert page.pid == 1
        assert page.idx == 2
        assert page.on_disk is False
        assert page.in_use is True
        assert page.key == (1, 2)

    def test_page_equality(self):
        """Test Page equality comparison with tuple."""
        from automation.api import Page
        
        page = Page(pid=1, idx=2, on_disk=False, in_use=True)
        assert page == (1, 2)
        assert not (page == (1, 3))

    def test_process_dataclass(self):
        """Test Process dataclass properties."""
        from automation.api import Process
        
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
        from automation.api import Process
        
        process = Process(pid=42)
        assert process == 42
        assert not (process == 43)

    def test_io_queue_dataclass(self):
        """Test IoQueue dataclass."""
        from automation.api import IoQueue
        
        io_queue = IoQueue()
        assert io_queue.io_count == 0
        
        io_queue.io_count = 5
        assert io_queue.io_count == 5


class TestRunOsStateUpdates:
    """Tests for RunOs state update handlers via public interface."""

    @pytest.fixture
    def run_os(self):
        """Create a fresh RunOs instance for each test."""
        from automation.api import RunOs
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
        from automation.api import RunOs
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
        from automation.api import RunOs
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


class TestGameObjectsEmitEvents:
    """Tests that real game objects emit events to game_monitor.
    
    These tests verify that the actual game objects (ProcessManager, PageManager, etc.)
    call the appropriate game_monitor.notify_* functions when state changes occur.
    """

    def test_process_manager_emits_process_new_event(self, stage):
        """Test that ProcessManager._create_process emits PROC_NEW event."""
        game_monitor.clear_events()
        
        # Create a process using the internal method
        # (this is what gets called during gameplay)
        stage.process_manager._create_process()
        
        events = game_monitor.get_events()
        proc_new_events = [e for e in events if e.etype == 'PROC_NEW']
        
        assert len(proc_new_events) >= 1, "ProcessManager._create_process should emit PROC_NEW event"
        assert proc_new_events[0].pid == 1, "First process should have pid=1"

    def test_process_emits_page_new_event_when_using_cpu(self, stage, monkeypatch):
        """Test that Process emits PAGE_NEW event when it starts using CPU and creates pages."""
        # Create a process
        stage.process_manager._create_process()
        process = stage.process_manager.get_process(1)
        
        # Ensure CPU is available
        cpu = stage.process_manager._cpu_manager.select_free_cpu()
        assert cpu is not None, "Need a free CPU for this test"
        
        game_monitor.clear_events()
        
        # When process uses CPU for the first time, it creates pages
        process.use_cpu()
        
        events = game_monitor.get_events()
        page_new_events = [e for e in events if e.etype == 'PAGE_NEW']
        
        assert len(page_new_events) >= 1, "Process.use_cpu should emit PAGE_NEW events when creating pages"

    def test_io_queue_emits_io_queue_event_on_process(self, stage):
        """Test that IoQueue emits IO_QUEUE event when processing events."""
        io_queue = stage.process_manager.io_queue
        
        # Add a subscriber so there's something to process
        callback_called = []
        io_queue.wait_for_event(lambda: callback_called.append(True))
        
        # Simulate time passing so event becomes available
        io_queue._event_count = 1
        
        game_monitor.clear_events()
        
        # Process events - this should emit IO_QUEUE event
        io_queue.process_events()
        
        events = game_monitor.get_events()
        io_queue_events = [e for e in events if e.etype == 'IO_QUEUE']
        
        assert len(io_queue_events) >= 1, "IoQueue.process_events should emit IO_QUEUE event"
        assert io_queue_events[0].io_count == 0, "After processing, io_count should be 0"

    def test_process_emits_cpu_event_when_toggled(self, stage):
        """Test that Process emits PROC_CPU event when toggled on/off CPU."""
        # Create a process
        stage.process_manager._create_process()
        process = stage.process_manager.get_process(1)
        
        game_monitor.clear_events()
        
        # Toggle process (should assign to CPU)
        process.toggle()
        
        events = game_monitor.get_events()
        proc_cpu_events = [e for e in events if e.etype == 'PROC_CPU']
        
        assert len(proc_cpu_events) >= 1, "Process.toggle should emit PROC_CPU event"

    def test_process_emits_starvation_event_when_level_changes(self, stage):
        """Test that Process emits PROC_STARV event when starvation level changes."""
        # Create a process
        stage.process_manager._create_process()
        process = stage.process_manager.get_process(1)
        
        # Put process on CPU first
        process.toggle()
        
        game_monitor.clear_events()
        
        # Simulate enough time passing for happiness (starvation -> 0)
        # by calling _update_starvation_level with appropriate timing
        process._last_state_change_time = 0
        process._update_starvation_level(process.cpu.process_happiness_ms + 1)
        
        events = game_monitor.get_events()
        starv_events = [e for e in events if e.etype == 'PROC_STARV']
        
        assert len(starv_events) >= 1, "Process should emit PROC_STARV when starvation level changes"

    def test_process_emits_wait_page_event(self, stage):
        """Test that Process emits PROC_WAIT_PAGE event when waiting for page."""
        # Create a process and put on CPU (creates pages)
        stage.process_manager._create_process()
        process = stage.process_manager.get_process(1)
        process.toggle()
        
        # Ensure process has pages
        assert len(process._pages) > 0, "Process should have pages after using CPU"
        
        # Swap a page to disk
        page = process._pages[0]
        page._on_disk = True
        
        game_monitor.clear_events()
        
        # Check for unavailable pages (should trigger wait_page event)
        process._handle_unavailable_pages()
        
        events = game_monitor.get_events()
        wait_page_events = [e for e in events if e.etype == 'PROC_WAIT_PAGE']
        
        assert len(wait_page_events) >= 1, "Process should emit PROC_WAIT_PAGE when waiting for page"

    def test_page_emits_swap_event_when_swap_completes(self, stage):
        """Test that Page emits PAGE_SWAP event when swap completes."""
        # Create a process and put on CPU (creates pages)
        stage.process_manager._create_process()
        process = stage.process_manager.get_process(1)
        process.toggle()
        
        # Get a page
        page = process._pages[0]
        
        game_monitor.clear_events()
        
        # Request swap
        page.request_swap()
        
        # Run update loop until swap completes
        current_time = 0
        max_iterations = 1000
        for _ in range(max_iterations):
            stage.page_manager.update(current_time, [])
            page.update(current_time, [])
            current_time += 100
            if page.on_disk:
                break
        
        events = game_monitor.get_events()
        swap_events = [e for e in events if e.etype == 'PAGE_SWAP']
        
        assert len(swap_events) >= 1, "Page should emit PAGE_SWAP when swap completes"

    def test_process_emits_page_free_when_killed(self, stage):
        """Test that Process emits PAGE_FREE events when killed."""
        # Create a process and put on CPU (creates pages)
        stage.process_manager._create_process()
        process = stage.process_manager.get_process(1)
        process.toggle()
        
        num_pages = len(process._pages)
        assert num_pages > 0, "Process should have pages"
        
        game_monitor.clear_events()
        
        # Kill the process
        process._terminate_by_user()
        
        events = game_monitor.get_events()
        page_free_events = [e for e in events if e.etype == 'PAGE_FREE']
        
        assert len(page_free_events) == num_pages, \
            f"Process should emit PAGE_FREE for all {num_pages} pages when killed"

    def test_process_emits_proc_kill_when_killed(self, stage):
        """Test that Process emits PROC_KILL event when killed."""
        # Create a process
        stage.process_manager._create_process()
        process = stage.process_manager.get_process(1)
        
        game_monitor.clear_events()
        
        # Kill the process
        process._terminate_by_user()
        
        events = game_monitor.get_events()
        kill_events = [e for e in events if e.etype == 'PROC_KILL']
        
        assert len(kill_events) >= 1, "Process should emit PROC_KILL when killed"

    def test_process_emits_proc_term_when_gracefully_terminated(self, stage):
        """Test that Process emits PROC_TERM event when gracefully terminated."""
        # Create a process and put on CPU
        stage.process_manager._create_process()
        process = stage.process_manager.get_process(1)
        process.toggle()
        
        game_monitor.clear_events()
        
        # Gracefully terminate the process
        process._terminate_gracefully()
        
        events = game_monitor.get_events()
        term_events = [e for e in events if e.etype == 'PROC_TERM']
        
        assert len(term_events) >= 1, "Process should emit PROC_TERM when gracefully terminated"

    def test_process_emits_proc_end_when_terminated_and_yields_cpu(self, stage):
        """Test that Process emits PROC_END event when terminated process yields CPU."""
        # Create a process and put on CPU
        stage.process_manager._create_process()
        process = stage.process_manager.get_process(1)
        process.toggle()
        
        # Gracefully terminate
        process._terminate_gracefully()
        
        game_monitor.clear_events()
        
        # Yield CPU (this should trigger PROC_END)
        process.yield_cpu()
        
        events = game_monitor.get_events()
        end_events = [e for e in events if e.etype == 'PROC_END']
        
        assert len(end_events) >= 1, "Process should emit PROC_END when terminated process yields CPU"


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
            stage_with_script.process_manager, 
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
            stage.page_manager,
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
            stage.process_manager.io_queue,
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
            stage_with_script.process_manager,
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

class TestAutoModule:
    """Tests for the auto.py module functions."""

    @pytest.fixture
    def temp_script(self, tmp_path):
        """Create a temporary script file."""
        script_file = tmp_path / "test_script.py"
        script_file.write_text("def run_os(events): return []\n")
        return str(script_file)

    @pytest.fixture
    def temp_sandbox_module(self, tmp_path, monkeypatch):
        """Create a temporary sandbox module with a stage."""
        module_dir = tmp_path / "test_sandbox"
        module_dir.mkdir()
        (module_dir / "__init__.py").write_text("")

        stage_file = module_dir / "test_config.py"
        stage_file.write_text('''
from config.stage_config import StageConfig
from config.cpu_config import CpuConfig
from scenes.stage import Stage

config = StageConfig(
    cpu_config=CpuConfig(num_cores=2),
    num_processes_at_startup=5,
    num_ram_rows=4,
)
stage = Stage("Test Sandbox", config)
''')
        monkeypatch.syspath_prepend(str(tmp_path))
        return "test_sandbox.test_config"

    def test_parse_arguments_default_difficulty(self, temp_script, monkeypatch):
        """Test parse_arguments with default (normal) difficulty."""
        import sys
        from auto import parse_arguments
        from config.difficulty_levels import default_difficulty

        monkeypatch.setattr(sys, 'argv', ['auto', temp_script])
        filename, result = parse_arguments()

        assert filename == temp_script
        config, name = result
        assert config == default_difficulty.config
        assert "NORMAL" in name.upper()

    def test_parse_arguments_easy_difficulty(self, temp_script, monkeypatch):
        """Test parse_arguments with --easy flag."""
        import sys
        from auto import parse_arguments
        from config.difficulty_levels import difficulty_levels_map

        monkeypatch.setattr(sys, 'argv', ['auto', temp_script, '--easy'])
        filename, result = parse_arguments()

        config, name = result
        assert config == difficulty_levels_map['easy'].config
        assert "EASY" in name.upper()

    def test_parse_arguments_hard_difficulty(self, temp_script, monkeypatch):
        """Test parse_arguments with --hard flag."""
        import sys
        from auto import parse_arguments
        from config.difficulty_levels import difficulty_levels_map

        monkeypatch.setattr(sys, 'argv', ['auto', temp_script, '--hard'])
        filename, result = parse_arguments()

        config, name = result
        assert config == difficulty_levels_map['hard'].config
        assert "HARD" in name.upper()

    def test_parse_arguments_harder_difficulty(self, temp_script, monkeypatch):
        """Test parse_arguments with --harder flag."""
        import sys
        from auto import parse_arguments
        from config.difficulty_levels import difficulty_levels_map

        monkeypatch.setattr(sys, 'argv', ['auto', temp_script, '--harder'])
        filename, result = parse_arguments()

        config, name = result
        assert config == difficulty_levels_map['harder'].config
        assert "HARDER" in name.upper()

    def test_parse_arguments_insane_difficulty(self, temp_script, monkeypatch):
        """Test parse_arguments with --insane flag."""
        import sys
        from auto import parse_arguments
        from config.difficulty_levels import difficulty_levels_map

        monkeypatch.setattr(sys, 'argv', ['auto', temp_script, '--insane'])
        filename, result = parse_arguments()

        config, name = result
        assert config == difficulty_levels_map['insane'].config
        assert "INSANE" in name.upper()

    def test_parse_arguments_sandbox_with_stage(self, temp_script, temp_sandbox_module, monkeypatch):
        """Test parse_arguments with --sandbox flag loads stage from module."""
        import sys
        from auto import parse_arguments
        from scenes.stage import Stage

        monkeypatch.setattr(sys, 'argv', ['auto', temp_script, '--sandbox', temp_sandbox_module])
        filename, result = parse_arguments()

        assert isinstance(result, Stage)
        assert result.name == "Test Sandbox"

    def test_parse_arguments_sandbox_not_found(self, temp_script, monkeypatch, capsys):
        """Test parse_arguments with --sandbox for non-existent module."""
        import sys
        from auto import parse_arguments

        monkeypatch.setattr(sys, 'argv', ['auto', temp_script, '--sandbox', 'nonexistent.module'])

        with pytest.raises(SystemExit) as exc_info:
            parse_arguments()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "not found" in captured.err

    def test_parse_arguments_sandbox_missing_stage(self, temp_script, tmp_path, monkeypatch, capsys):
        """Test parse_arguments with --sandbox when module has no stage."""
        import sys
        from auto import parse_arguments

        module_dir = tmp_path / "bad_sandbox"
        module_dir.mkdir()
        (module_dir / "__init__.py").write_text("")
        (module_dir / "no_stage.py").write_text("x = 1\n")
        monkeypatch.syspath_prepend(str(tmp_path))

        monkeypatch.setattr(sys, 'argv', ['auto', temp_script, '--sandbox', 'bad_sandbox.no_stage'])

        with pytest.raises(SystemExit) as exc_info:
            parse_arguments()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "stage" in captured.err

    def test_compile_auto_script_absolute_path(self, temp_script):
        """Test compile_auto_script with absolute path."""
        from auto import compile_auto_script

        compiled = compile_auto_script(temp_script)
        assert compiled is not None
        assert hasattr(compiled, 'co_filename')

    def test_compile_auto_script_relative_path(self, tmp_path, monkeypatch):
        """Test compile_auto_script with relative path."""
        from auto import compile_auto_script
        import os

        script_file = tmp_path / "rel_script.py"
        script_file.write_text("def run_os(events): return []\n")

        monkeypatch.chdir(tmp_path)
        os.makedirs("../subdir", exist_ok=True)
        rel_script = tmp_path.parent / "subdir" / "script.py"
        rel_script.write_text("def run_os(events): return []\n")

        compiled = compile_auto_script(str(rel_script))
        assert compiled is not None
