import sys
import time

import pygame

from pykanoid.scritps.entities import Ball, Paddle
from pykanoid.scritps.header import Header
from pykanoid.settings import *
from pykanoid.scritps.status import Status, State
from pykanoid.scritps.tilemap import Tilemap
from pykanoid.scritps.utils import load_image, load_images, RANDOM_GENERATOR


class Game:
    __PADDLE_OFFSET_Y = 100

    HEADER_AREA_SIZE = (WINDOW_WIDTH, 44)
    GAME_AREA_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT - HEADER_AREA_SIZE[1])

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pykanoid")

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.header_surface = pygame.Surface(self.HEADER_AREA_SIZE)
        self.game_surface = pygame.Surface(self.GAME_AREA_SIZE)

        self.clock = pygame.time.Clock()

        self.status = Status()

        self.movement = [False, False]

        self.assets = {
            "paddle": load_image("paddleBlu.png"),
            "ball": load_image("ballGrey.png"),
        }

        self.header = Header(self.status)

        asset_paddle = self.assets["paddle"]
        self.paddle = Paddle(
            self,
            "paddle",
            (
                self.GAME_AREA_SIZE[0] / 2 - asset_paddle.get_width() / 2,
                self.GAME_AREA_SIZE[1] - self.__PADDLE_OFFSET_Y,
            ),
            asset_paddle,
        )

        asset_ball = self.assets["ball"]
        self.ball = Ball(
            self,
            "ball",
            (
                self.GAME_AREA_SIZE[0] / 2 - asset_ball.get_width() / 2,
                self.paddle.position[1] - asset_ball.get_height(),
            ),
            asset_ball,
        )

        self.ball_initial_direction = RANDOM_GENERATOR.randrange(-1, 1)

        self.tilemap = Tilemap(self)

    def run(self):
        last_time = time.time_ns()
        while True:
            dt = time.time_ns() - last_time
            last_time = time.time_ns()

            self.game_surface.fill(BACKGROUND_COLOR)
            self.header_surface.fill(BACKGROUND_COLOR)

            if self.status.state == State.IDLE:
                self.ball.update()
            elif self.status.state == State.START:
                self.status.set_state(State.IDLE)
            elif self.status.state == State.PLAYING:
                self.ball.move()
            elif self.status.state == State.PAUSED:
                pass
            elif self.status.state == State.LIFE_LOST:
                self.ball.reset()
                if self.status.lives == 0:
                    self.status.set_state(State.GAME_LOST)
                else:
                    self.status.set_state(State.IDLE)
            elif self.status.state == State.GAME_LOST:
                self.status.set_state(State.RESET)
            elif self.status.state == State.GAME_WON:
                self.status.set_state(State.RESET)
            elif self.status.state == State.NEXT_LEVEL:
                pass
            elif self.status.state == State.LEVEL_CLEARED:
                self.status.set_state(State.GAME_WON)
            elif self.status.state == State.RESET:
                self.tilemap = Tilemap(self)
                self.status.set_state(State.START)

            self.header.update(self.status)
            self.header.render(self.header_surface)

            self.tilemap.render(self.game_surface)

            self.paddle.update((self.movement[1] - self.movement[0], 0))
            self.paddle.render(self.game_surface)

            self.ball.render(self.game_surface)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
                    if event.key == pygame.K_SPACE and self.status.state == State.IDLE:
                        self.status.set_state(State.PLAYING)
                        self.ball.start()

            self.screen.blit(self.header_surface, (0, 0))
            self.screen.blit(self.game_surface, (0, self.HEADER_AREA_SIZE[1]))

            # pygame.draw.line(
            #     self.screen,
            #     'Grey',
            #     (0, self.HEADER_AREA_SIZE[1]),
            #     (self.HEADER_AREA_SIZE[0], self.HEADER_AREA_SIZE[1]),
            #     1,
            # )

            pygame.display.update()
            self.clock.tick(60)
