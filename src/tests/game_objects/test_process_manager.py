import pytest

from game_objects.cpu import Cpu
from game_objects.io_queue import IoQueue
from game_objects.process_manager import ProcessManager
from game_objects.process_slot import ProcessSlot

class TestProcessManager:
    def test_setup(self, stage):
        process_manager = ProcessManager(stage)
        process_manager.setup()

        assert process_manager.stage == stage

        assert len(process_manager.cpu_list) == 4
        for cpu in process_manager.cpu_list:
            assert isinstance(cpu, Cpu)

        assert len(process_manager.process_slots) == 42
        for process_slot in process_manager.process_slots:
            assert isinstance(process_slot, ProcessSlot)

        assert isinstance(process_manager.io_queue, IoQueue)

        assert process_manager.user_terminated_process_count == 0
        