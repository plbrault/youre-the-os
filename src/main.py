import sys, pygame

pygame.init()

size = width, height = 1920, 1080

black = 0, 0, 0

screen = pygame.display.set_mode(size)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    screen.fill(black)

    pygame.display.flip()
