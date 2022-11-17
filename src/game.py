import sys, pygame

from lib.gui.color import Color
from visual_components.cpu_core_component import CpuCoreComponent

pygame.init()
pygame.font.init()

size = width, height = 1920, 1080

cpu_core_1 = CpuCoreComponent(100, 100, 1)

screen = pygame.display.set_mode(size)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    screen.fill(Color.BLACK)

    cpu_core_1.draw(screen)

    pygame.display.flip()
