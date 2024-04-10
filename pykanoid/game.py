import sys
import time

import pygame

from pykanoid.entities import Ball, Paddle
from pykanoid.header import Header
from pykanoid.settings import *
from pykanoid.status import Status, State
from pykanoid.tilemap import Tilemap
from pykanoid.utils import load_image, RANDOM_GENERATOR


class Game:
    __PADDLE_OFFSET_Y = 100

    HEADER_AREA_SIZE = (WINDOW_WIDTH, 40)
    GAME_AREA_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT - HEADER_AREA_SIZE[1])

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pykanoid")

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.header_surface = pygame.Surface(self.HEADER_AREA_SIZE)
        self.game_surface = pygame.Surface(self.GAME_AREA_SIZE)

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

        self.__font = pygame.font.Font(FONT_FILE_PATH, 36)
        self.start_instructions_surface = self.__font.render(
            "Press ENTER to start", False, "White"
        )

        self.life_lost_sound = pygame.mixer.Sound("data/audio/life_lost.wav")
        self.life_lost_sound.set_volume(0.4)

    def run(self):
        previous_time = time.time()
        while True:
            dt = time.time() - previous_time
            previous_time = time.time()

            self.game_surface.fill(BACKGROUND_COLOR)
            self.header_surface.fill(BACKGROUND_COLOR)

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
                    if event.key == pygame.K_RETURN and self.status.state == State.IDLE:
                        self.status.set_state(State.START)
                    if (
                        event.key == pygame.K_SPACE
                        and self.status.state == State.WAITING_BALL_RELEASE
                    ):
                        self.ball.launch()
                        self.status.set_state(State.PLAYING)

            self.paddle.update(dt, (self.movement[1] - self.movement[0], 0))

            if self.status.state == State.IDLE:
                self.game_surface.blit(
                    self.start_instructions_surface,
                    (
                        self.game_surface.get_rect().centerx
                        - self.start_instructions_surface.get_width() / 2,
                        self.game_surface.get_height() - self.__PADDLE_OFFSET_Y * 2.5,
                    ),
                )
                self.ball.update(dt)
            elif self.status.state == State.START:
                self.tilemap.generate_random()
                self.status.set_state(State.WAITING_BALL_RELEASE)
            elif self.status.state == State.PLAYING:
                self.ball.update(dt)
            elif self.status.state == State.LIFE_LOST:
                self.ball.reset()
                if self.status.lives == 0:
                    self.status.set_state(State.GAME_LOST)
                else:
                    self.life_lost_sound.play()
                    self.status.set_state(State.WAITING_BALL_RELEASE)
            elif self.status.state == State.LEVEL_CLEARED:
                self.status.set_state(State.GAME_WON)
            elif self.status.state == State.WAITING_BALL_RELEASE:
                self.ball.update(dt)
            elif self.status.state == State.GAME_LOST:
                self.status.set_state(State.IDLE)
            elif self.status.state == State.GAME_WON:
                self.status.set_state(State.IDLE)
            elif self.status.state == State.NEXT_LEVEL:
                pass

            self.header.update(self.status)

            self.header.render(self.header_surface)
            self.tilemap.render(self.game_surface)
            self.paddle.render(self.game_surface)
            self.ball.render(self.game_surface)

            self.screen.blit(self.header_surface, (0, 0))
            self.screen.blit(self.game_surface, (0, self.HEADER_AREA_SIZE[1]))

            pygame.display.update()
