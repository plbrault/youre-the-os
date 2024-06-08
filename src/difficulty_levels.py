from constants import MAX_PROCESSES

_easy_difficulty = {
    'name': 'Easy',
    'config': {
        'num_cpus': 4,
        'num_processes_at_startup': 14,
        'max_processes': MAX_PROCESSES,
        'num_ram_rows': 8,
        'new_process_probability': 0.05,
        'priority_process_probability': 0.01,
        'io_probability': 0.01,
        'graceful_termination_probability': 0.01
    }
}

_normal_difficulty = {
    'name': 'Normal',
    'config': {
        'num_cpus': 4,
        'max_processes': MAX_PROCESSES,
        'num_processes_at_startup': 14,
        'num_ram_rows': 5,
        'new_process_probability': 0.05,
        'priority_process_probability': 0.02,
        'io_probability': 0.05,
        'graceful_termination_probability': 0.01
    }
}

_hard_difficulty = {
    'name': 'Hard',
    'config': {
        'num_cpus': 8,
        'max_processes': MAX_PROCESSES,
        'num_processes_at_startup': 28,
        'num_ram_rows': 6,
        'new_process_probability': 0.1,
        'priority_process_probability': 0.05,
        'io_probability': 0.1,
        'graceful_termination_probability': 0.01
    }
}

_harder_difficulty = {
    'name': 'Harder',
    'config': {
        'num_cpus': 12,
        'max_processes': MAX_PROCESSES,
        'num_processes_at_startup': 35,
        'num_ram_rows': 6,
        'new_process_probability': 0.2,
        'priority_process_probability': 0.1,
        'io_probability': 0.2,
        'graceful_termination_probability': 0.01
    }
}

_insane_difficulty = {
    'name': 'Insane',
    'config': {
        'num_cpus': 16,
        'max_processes': MAX_PROCESSES,
        'num_processes_at_startup': 42,
        'num_ram_rows': 4,
        'new_process_probability': 1,
        'priority_process_probability': 0.1,
        'io_probability': 0.3,
        'graceful_termination_probability': 0.01
    }
}

difficulty_levels = [
    _easy_difficulty,
    _normal_difficulty,
    _hard_difficulty,
    _harder_difficulty,
    _insane_difficulty
]

difficulty_levels_map = {
    level['name'].lower(): level for level in difficulty_levels
}

default_difficulty = _normal_difficulty
