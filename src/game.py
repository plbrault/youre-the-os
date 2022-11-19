import sys, pygame

from game_objects.cpu import Cpu
from game_objects.process import Process
from lib.ui.color import Color
from lib.game_event import GameEvent
from lib.game_event_type import GameEventType

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()

        self._game_objects = []

        self.setup()
        self.main_loop()

    def setup(self):
        size = width, height = 1024, 768
        self._screen = pygame.display.set_mode(size)

        cpu_list = [
            Cpu(1),
            Cpu(2),
            Cpu(3),
            Cpu(4),
        ]
        for i, cpu in enumerate(cpu_list):
            x = 50 + i * cpu.view.width + i * 5
            y = 50
            cpu.view.setXY(x, y)
        self._game_objects.extend(cpu_list)        

        process = Process(cpu_list)
        process.view.setXY(50, 150)
        self._game_objects.append(process)
    
    def main_loop(self):
        while True:
            self.update(pygame.time.get_ticks())
            self.render()        

    def update(self, current_time):
        events = []

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                if (event.button == 1):
                    events.append(GameEvent(GameEventType.MOUSE_LEFT_CLICK, { 'position': event.pos }))

        for game_object in self._game_objects:
            game_object.update(current_time, events)

    def render(self):
        self._screen.fill(Color.BLACK)

        for game_object in self._game_objects:
            game_object.render(self._screen)

        pygame.display.flip()
