import pygame
from pygame import Rect

from pykanoid.status import State
from pykanoid.tile import Tile
from pykanoid.utils import RANDOM_GENERATOR


class PhysicsEntity:
    def __init__(self, game, e_type, position, asset: pygame.Surface):
        self.game = game
        self.type = e_type
        self.position = list(position)
        self.asset = asset
        self.velocity = [0, 0]
        self.acceleration = 10

    def rect(self) -> pygame.Rect:
        return pygame.Rect(
            self.position[0],
            self.position[1],
            self.asset.get_width(),
            self.asset.get_height(),
        )

    def mask(self) -> pygame.Mask:
        return pygame.mask.from_surface(self.asset)

    def update(self, movement=(0, 0)):
        frame_movement = (
            (movement[0] + self.velocity[0]) * self.acceleration,
            (movement[1] + self.velocity[1]) * self.acceleration,
        )

        self.position[0] += frame_movement[0]
        self.position[1] += frame_movement[1]

    def render(self, surface):
        surface.blit(self.asset, self.position)


class Paddle(PhysicsEntity):

    def update(self, movement=(0, 0)):
        super().update(movement)

        if self.position[0] <= 0:
            self.position[0] = 0
        if self.position[0] >= self.game.GAME_AREA_SIZE[0] - self.asset.get_width():
            self.position[0] = self.game.GAME_AREA_SIZE[0] - self.asset.get_width()


class Ball(PhysicsEntity):
    __INITIAL_ACCELERATION = 3
    __HIT_THRESHOLD = 7
    __MAX_ACCELERATION = 15
    __COLLISION_THRESHOLD = 5

    def __init__(self, game, e_type, position, size):
        super().__init__(game, e_type, position, size)

        self.acceleration = self.__INITIAL_ACCELERATION
        self.paddle_hits = 0

    def launch(self):
        self.velocity = [RANDOM_GENERATOR.choice((-1, 1)), -1]

    def reset(self):
        self.acceleration = self.__INITIAL_ACCELERATION
        self.paddle_hits = 0
        self.velocity = [0, 0]
        self.position = [
            self.game.paddle.position[0]
            + self.game.paddle.asset.get_width() / 2
            - self.asset.get_width() / 2,
            self.game.paddle.position[1] - self.asset.get_height(),
        ]

    def update(self, movement=(0, 0)):
        entity_rect: pygame.Rect = self.rect()
        paddle_rect: pygame.Rect = self.game.paddle.rect()

        entity_rect.centerx = paddle_rect.centerx
        self.position[0] = entity_rect.x

    def move(self):
        if self.paddle_hits >= self.__HIT_THRESHOLD:
            self.acceleration *= 1.15
            self.paddle_hits = 0

        if self.acceleration >= self.__MAX_ACCELERATION:
            self.acceleration = self.__MAX_ACCELERATION

        self.position[0] += self.velocity[0] * self.acceleration
        self.position[1] += self.velocity[1] * self.acceleration

        entity_rect: pygame.Rect = self.rect()
        paddle_rect: pygame.Rect = self.game.paddle.rect()

        entity_mask: pygame.Mask = self.mask()
        paddle_mask: pygame.Mask = self.game.paddle.mask()

        if paddle_mask.overlap(
            entity_mask,
            (
                self.position[0] - self.game.paddle.position[0],
                self.position[1] - self.game.paddle.position[1],
            ),
        ):
            # check if collision was from above
            if (
                abs(entity_rect.bottom - paddle_rect.top) < self.__COLLISION_THRESHOLD
                and entity_rect.centery <= paddle_rect.centery
                and self.velocity[1] > 0
            ):
                self.velocity[1] *= -1
                self.paddle_hits += 1
            # check if collision was from bellow
            if (
                abs(entity_rect.top - paddle_rect.bottom) < self.__COLLISION_THRESHOLD
                and entity_rect.centery >= paddle_rect.centery
                and self.velocity[1] < 0
            ):
                self.velocity[1] *= -1
            # check if collision was from the left
            if (
                abs(entity_rect.right - paddle_rect.left)
                < self.__COLLISION_THRESHOLD * 2
                and self.velocity[0] > 0
            ):
                self.velocity[0] *= -1
            # check if collision was from the right
            if (
                abs(entity_rect.left - paddle_rect.right)
                < self.__COLLISION_THRESHOLD * 2
                and self.velocity[0] < 0
            ):
                self.velocity[0] *= -1

        if (
            self.position[0] <= 0
            or self.position[0] >= self.game.GAME_AREA_SIZE[0] - self.asset.get_width()
        ):
            self.velocity[0] *= -1

        if self.position[1] <= 0:
            self.velocity[1] *= -1

        if self.position[1] >= self.game.GAME_AREA_SIZE[1] - self.asset.get_height():
            self.game.status.set_state(State.LIFE_LOST)

        tiles: list[Tile] = self.game.tilemap.tile_list()
        tile_recs: list[Rect] = self.game.tilemap.rects()

        collision_tile_index = entity_rect.collidelist(tile_recs)

        if collision_tile_index > 0:
            self.game.tilemap.trigger_hit(tiles[collision_tile_index])
            tile_rec: Rect = tile_recs[collision_tile_index]

            # check if collision was from above
            if (
                abs(entity_rect.bottom - tile_rec.top) < self.__COLLISION_THRESHOLD
                and self.velocity[1] > 0
            ):
                self.velocity[1] *= -1
            # check if collision was from bellow
            if (
                abs(entity_rect.top - tile_rec.bottom) < self.__COLLISION_THRESHOLD
                and self.velocity[1] < 0
            ):
                self.velocity[1] *= -1
            # check if collision was from the left
            if (
                abs(entity_rect.right - tile_rec.left) < self.__COLLISION_THRESHOLD
                and self.velocity[0] > 0
            ):
                self.velocity[0] *= -1
            # check if collision was from the right
            if (
                abs(entity_rect.left - tile_rec.right) < self.__COLLISION_THRESHOLD
                and self.velocity[0] < 0
            ):
                self.velocity[0] *= -1
