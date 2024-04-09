import pygame.transform
from pygame import Surface

from pykanoid.settings import FONT_FILE_PATH
from pykanoid.status import Status
from pykanoid.utils import load_image


class Header:
    def __init__(self, status: Status):
        self.__status = status
        self.__life_asset = pygame.transform.scale(
            load_image("life/heart_48.png"), (24, 24)
        )
        self.__font = pygame.font.Font(FONT_FILE_PATH, 24)

    def update(self, status: Status):
        self.__status = status

    def render(self, surface: Surface):
        gap = 10
        for life in range(self.__status.lives):
            surface.blit(
                self.__life_asset, (gap + life * self.__life_asset.get_width(), gap)
            )
        score_surface = self.__font.render(
            str(self.__status.score), False, (255, 255, 255, 255)
        )
        surface.blit(
            score_surface,
            (surface.get_width() - score_surface.get_width() - gap, gap / 2),
        )
