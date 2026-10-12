import pytest

from constants import ONE_SECOND
from engine.random import Random
from scene_objects.custom_settings_dialog import CustomSettingsDialog
from scene_objects.process import ProcessState, ProcessType


class TestCustomSettingsDialog:
    @pytest.fixture
    def dialog(self):
        return CustomSettingsDialog(lambda: None)

    @pytest.fixture
    def running_priority_process(self, dialog, stage_custom_config):
        def create_running_priority_process(graceful_termination_option):
            dialog.graceful_termination_selector.selected_option = graceful_termination_option
            dialog.num_processes_at_startup_selector.selected_option = '1'
            dialog.new_process_probability_selector.selected_option = '0 %'
            dialog.priority_process_probability_selector.selected_option = '100 %'
            dialog.io_probability_selector.selected_option = '0 %'

            stage = stage_custom_config(dialog.config)
            # The first process at startup is created 50 ms after setup
            stage.update(50, [])
            process = stage.process_manager.get_process(1)
            process.use_cpu()

            return process, stage
        return create_running_priority_process

    def test_config_graceful_termination_probability_when_yes_selected(self, dialog):
        dialog.graceful_termination_selector.selected_option = 'Yes'

        assert dialog.config.graceful_termination_probability == 0.01

    def test_config_priority_process_graceful_termination_probability_when_yes_selected(self, dialog):
        dialog.graceful_termination_selector.selected_option = 'Yes'

        assert dialog.config.priority_process_graceful_termination_probability == 0.01

    def test_config_graceful_termination_probability_when_no_selected(self, dialog):
        dialog.graceful_termination_selector.selected_option = 'No'

        assert dialog.config.graceful_termination_probability == 0

    def test_config_priority_process_graceful_termination_probability_when_no_selected(self, dialog):
        dialog.graceful_termination_selector.selected_option = 'No'

        assert dialog.config.priority_process_graceful_termination_probability == 0

    def test_priority_process_can_terminate_gracefully_when_yes_selected(
            self, running_priority_process, monkeypatch):
        process, stage = running_priority_process('Yes')

        # Cause the random number generator to always provoke graceful termination
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        assert process.type == ProcessType.PRIORITY

        stage.update(50 + ONE_SECOND, [])

        assert process.has_ended_gracefully == True
        assert process.state == ProcessState.ENDED

    def test_priority_process_cannot_terminate_gracefully_when_no_selected(
            self, running_priority_process, monkeypatch):
        process, stage = running_priority_process('No')

        # Cause the random number generator to always provoke graceful termination when allowed
        monkeypatch.setattr(Random, 'get_number', lambda self, min, max: min)

        assert process.type == ProcessType.PRIORITY

        stage.update(50 + ONE_SECOND, [])

        assert process.has_ended_gracefully == False
        assert process.state == ProcessState.RUNNING
