import sys, pygame

pygame.init()
pygame.font.init()

size = width, height = 1920, 1080

black = 0, 0, 0
green = 0, 255, 0

cpu_font = pygame.font.SysFont('Arial', 10)
text_surface = cpu_font.render('CPU 1', False, green)

screen = pygame.display.set_mode(size)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    screen.fill(black)

    pygame.draw.rect(screen, green, pygame.Rect(100, 100, 64, 64))
    pygame.draw.rect(screen, black, pygame.Rect(102, 102, 60, 60))

    pygame.draw.rect(screen, green, pygame.Rect(170, 100, 64, 64))
    pygame.draw.rect(screen, black, pygame.Rect(172, 102, 60, 60))

    pygame.draw.rect(screen, green, pygame.Rect(240, 100, 64, 64))
    pygame.draw.rect(screen, black, pygame.Rect(242, 102, 60, 60))

    pygame.draw.rect(screen, green, pygame.Rect(310, 100, 64, 64))
    pygame.draw.rect(screen, black, pygame.Rect(312, 102, 60, 60))

    screen.blit(text_surface, (100, 100))

    pygame.display.flip()
