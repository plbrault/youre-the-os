_normal_difficulty = {
    'name': 'Normal',
    'config': {
        'num_cpus': 4,
        'num_processes_at_startup': 12,
        'num_ram_rows': 5,
        'io_probability': 0.1
    }
}

difficulty_levels = [
    _normal_difficulty
]

default_difficulty = _normal_difficulty
