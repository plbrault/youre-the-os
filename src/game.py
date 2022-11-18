import sys, pygame

from game_objects.cpu import Cpu
from game_objects.process import Process
from lib.ui.color import Color

pygame.init()
pygame.font.init()

size = width, height = 1024, 768

cpus = [
  Cpu(1),
  Cpu(2),
  Cpu(3),
  Cpu(4),
]

for i, cpu in enumerate(cpus):
    x = 50 + i * 50 + i * 5
    y = 50
    cpu.view.setXY(x, y)

process = Process()
process.view.setXY(50, 100)

screen = pygame.display.set_mode(size)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    for cpu in cpus:
        cpu.update(pygame.time.get_ticks())
    process.update(pygame.time.get_ticks())

    screen.fill(Color.BLACK)

    for cpu in cpus:
        cpu.render(screen)

    process.render(screen)

    pygame.display.flip()
