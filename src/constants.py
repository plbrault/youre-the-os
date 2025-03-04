ONE_SECOND = 1000
ONE_MINUTE = 60 * ONE_SECOND

FRAMERATE = 60

MAX_PROCESSES = 42

LAST_ALIVE_STARVATION_LEVEL = 5
DEAD_STARVATION_LEVEL = 6

MIN_CPU_COUNT = 1
MAX_CPU_COUNT = 16
MIN_PROCESSES_AT_STARTUP = 1
MAX_PROCESSES_AT_STARTUP = 42
MIN_RAM_ROWS = 1
MAX_RAM_ROWS = 11

MAX_PAGES_PER_PROCESS = 4

SWAP_DELAY_NAMES_TO_MS = {
    'Low': 100,
    'Medium': 250,
    'High': 500,
    'Higher': 1000
}

SWAP_DELAY_MS_TO_NAMES = {value: key for key, value in SWAP_DELAY_NAMES_TO_MS.items()}

SWAP_DELAY_NAMES = list(SWAP_DELAY_NAMES_TO_MS.keys())
