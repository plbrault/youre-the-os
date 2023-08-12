_easy_difficulty = {
    'name': 'Easy',
    'config': {
        'num_cpus': 4,
        'num_processes_at_startup': 14,
        'num_ram_rows': 8,
        'new_process_probability': 0.05,
        'io_probability': 0.05
    }
}

_normal_difficulty = {
    'name': 'Normal',
    'config': {
        'num_cpus': 4,
        'num_processes_at_startup': 14,
        'num_ram_rows': 5,
        'new_process_probability': 0.05,
        'io_probability': 0.1
    }
}

_hard_difficulty = {
    'name': 'Hard',
    'config': {
        'num_cpus': 8,
        'num_processes_at_startup': 28,
        'num_ram_rows': 6,
        'new_process_probability': 0.1,
        'io_probability': 0.1
    }
}

_harder_difficulty = {
    'name': 'Harder',
    'config': {
        'num_cpus': 12,
        'num_processes_at_startup': 35,
        'num_ram_rows': 6,
        'new_process_probability': 0.2,
        'io_probability': 0.2
    }
}

_insane_difficulty = {
    'name': 'Insane',
    'config': {
        'num_cpus': 16,
        'num_processes_at_startup': 42,
        'num_ram_rows': 4,
        'new_process_probability': 1,
        'io_probability': 0.3
    }
}

difficulty_levels = [
    _easy_difficulty,
    _normal_difficulty,
    _hard_difficulty,
    _harder_difficulty,
    _insane_difficulty
]

default_difficulty = _normal_difficulty
