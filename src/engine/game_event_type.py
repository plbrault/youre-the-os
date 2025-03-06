from enum import Enum

GameEventType = Enum('GameEventType', [
    'KEY_UP',
    'MOUSE_LEFT_CLICK',
    'MOUSE_MOTION',
    'QUIT'
])
