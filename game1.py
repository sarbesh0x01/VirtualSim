from pydantic import PydanticUndefinedAnnotation
import pygame
from pygame.base import init
from pygame.display import flip


pygame.init()

screen = pygame.display.set_mode([500, 500])

running = True


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        screen.fill((0, 0, 0))

    pygame.draw.circle(screen, (0, 0, 255), (250, 250), 75)
    pygame.display.flip()


pygame.quit()
