import sys, pygame

from game_objects.cpu import Cpu
from game_objects.process import Process
from lib.ui.color import Color
class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()

        size = width, height = 1024, 768

        self._cpus = [
            Cpu(1),
            Cpu(2),
            Cpu(3),
            Cpu(4),
        ]

        for i, cpu in enumerate(self._cpus):
            x = 50 + i * cpu.view.width + i * 5
            y = 50
            cpu.view.setXY(x, y)

        self._process = Process()
        self._process.view.setXY(50, 150)

        self._screen = pygame.display.set_mode(size)

        while True:
            self.update(pygame.time.get_ticks())
            self.render()

    def update(self, current_time):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        for cpu in self._cpus:
            cpu.update(current_time)

        self._process.update(pygame.time.get_ticks())

    def render(self):
        self._screen.fill(Color.BLACK)

        for cpu in self._cpus:
            cpu.render(self._screen)

        self._process.render(self._screen)

        pygame.display.flip()
