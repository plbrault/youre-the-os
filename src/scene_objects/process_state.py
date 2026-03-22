from enum import Enum, auto

class ProcessState(Enum):
    RUNNING = auto()
    IDLE = auto()
    WAITING_FOR_IO = auto()
    IO_EVENT_AVAILABLE = auto()
    WAITING_FOR_PAGE = auto()
    ENDED = auto()
