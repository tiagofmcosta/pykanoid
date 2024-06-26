import pygame

from pykanoid.settings import WINDOW_HEIGHT

pygame.init()

__font = pygame.font.Font(None, 30)


def debug(info, y=WINDOW_HEIGHT - 30, x=10):
    display_surface = pygame.display.get_surface()
    debug_surface = __font.render(str(info), True, "White")
    debug_rect = debug_surface.get_rect(topleft=(x, y))
    pygame.draw.rect(display_surface, "Black", debug_rect)
    display_surface.blit(debug_surface, debug_rect)
