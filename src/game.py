import sys, pygame

from game_logic.process import Process
from lib.ui.color import Color
from visual_components.cpu_component import CpuComponent
from visual_components.process_component import ProcessComponent

pygame.init()
pygame.font.init()

size = width, height = 1024, 768

cpu_components = [
  CpuComponent(50, 50, 1),
  CpuComponent(55 + CpuComponent.WIDTH, 50, 2),
  CpuComponent(60 + (2 * CpuComponent.WIDTH), 50, 3),
  CpuComponent(65 + (3 * CpuComponent.WIDTH), 50, 4)
]

process = Process()

process_component = ProcessComponent(50, 200, process)

screen = pygame.display.set_mode(size)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    process.update(pygame.time.get_ticks())

    screen.fill(Color.BLACK)

    for cpu_component in cpu_components:
        cpu_component.draw(screen)

    process_component.draw(screen)

    pygame.display.flip()
