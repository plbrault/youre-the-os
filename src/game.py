import sys, pygame

from game_objects.cpu import Cpu
from game_objects.process import Process
from lib.ui.color import Color
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

        cpus = [
            Cpu(1),
            Cpu(2),
            Cpu(3),
            Cpu(4),
        ]
        for i, cpu in enumerate(cpus):
            x = 50 + i * cpu.view.width + i * 5
            y = 50
            cpu.view.setXY(x, y)
        self._game_objects.extend(cpus)        

        process = Process()
        process.view.setXY(50, 150)
        self._game_objects.append(process)
    
    def main_loop(self):
        while True:
            self.update(pygame.time.get_ticks())
            self.render()        

    def update(self, current_time):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        for game_object in self._game_objects:
            game_object.update(current_time)

    def render(self):
        self._screen.fill(Color.BLACK)

        for game_object in self._game_objects:
            game_object.render(self._screen)

        pygame.display.flip()
