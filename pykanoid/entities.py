import pygame
from pygame import Rect, Surface

from pykanoid.status import State
from pykanoid.tile import Tile
from pykanoid.utils import RANDOM_GENERATOR


class PhysicsEntity:
    def __init__(self, game, e_type, position, asset: Surface):
        self.game = game
        self.type = e_type
        self.position = list(position)
        self.asset = asset
        self.velocity = [0, 0]
        self.acceleration = 0

    def rect(self) -> pygame.Rect:
        return pygame.Rect(
            self.position[0],
            self.position[1],
            self.asset.get_width(),
            self.asset.get_height(),
        )

    def mask(self) -> pygame.Mask:
        return pygame.mask.from_surface(self.asset)

    def update(self, dt, movement=(0, 0)):
        frame_movement = (
            (movement[0] + self.velocity[0]) * self.acceleration,
            (movement[1] + self.velocity[1]) * self.acceleration,
        )

        self.position[0] += frame_movement[0] * dt
        self.position[1] += frame_movement[1] * dt

    def render(self, surface):
        surface.blit(self.asset, self.position)


class Paddle(PhysicsEntity):
    def __init__(self, game, e_type, position, asset: Surface):
        super().__init__(game, e_type, position, asset)

        self.acceleration = 500

    def update(self, dt, movement=(0, 0)):
        super().update(dt, movement)

        if self.position[0] <= 0:
            self.position[0] = 0
        if self.position[0] >= self.game.GAME_AREA_SIZE[0] - self.asset.get_width():
            self.position[0] = self.game.GAME_AREA_SIZE[0] - self.asset.get_width()


class Ball(PhysicsEntity):
    __INITIAL_ACCELERATION_RATIO = 0.45
    __MAX_ACCELERATION_RATIO = 0.7
    __HIT_THRESHOLD_RATIO = 0.03
    __COLLISION_THRESHOLD = 5

    def __init__(self, game, e_type, position, asset: Surface):
        super().__init__(game, e_type, position, asset)

        self.__initial_acceleration = (
            self.game.paddle.acceleration * self.__INITIAL_ACCELERATION_RATIO
        )
        self.__max_acceleration = (
            self.game.paddle.acceleration * self.__MAX_ACCELERATION_RATIO
        )

        self.active = False
        self.velocity = [RANDOM_GENERATOR.choice((-1, 1)), -1]
        self.paddle_hits = 0
        self.acceleration = self.__initial_acceleration

    def launch(self):
        self.active = True

    def reset(self):
        self.active = False
        self.acceleration = self.__initial_acceleration
        self.paddle_hits = 0
        self.__position_on_paddle()

    def update(self, dt, movement=(0, 0)):
        if self.active:
            self.__move(dt)
        else:
            self.__position_on_paddle()

    def __position_on_paddle(self):
        entity_rect: pygame.Rect = self.rect()
        paddle_rect: pygame.Rect = self.game.paddle.rect()

        entity_rect.midbottom = paddle_rect.midtop
        self.position = pygame.math.Vector2(entity_rect.topleft)

    def __move(self, dt):
        if self.paddle_hits >= self.acceleration * self.__HIT_THRESHOLD_RATIO:
            self.acceleration *= 1.15
            self.paddle_hits = 0

        if self.acceleration >= self.__max_acceleration:
            self.acceleration = self.__max_acceleration

        self.position[0] += self.velocity[0] * self.acceleration * dt
        self.position[1] += self.velocity[1] * self.acceleration * dt

        entity_rect: pygame.Rect = self.rect()
        paddle_rect: pygame.Rect = self.game.paddle.rect()

        entity_mask: pygame.Mask = self.mask()
        paddle_mask: pygame.Mask = self.game.paddle.mask()

        # check collision with paddle
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

        # check collision with game edges
        # check if colliding with the bottom
        if entity_rect.bottom >= self.game.GAME_AREA_SIZE[1] and self.velocity[1] > 0:
            self.game.status.set_state(State.LIFE_LOST)
        # check if colliding with the top
        if entity_rect.top <= 0 and self.velocity[1] < 0:
            self.velocity[1] *= -1
        # check if colliding with the left
        if entity_rect.left <= 0 and self.velocity[0] < 0:
            self.velocity[0] *= -1
        # check if colliding with the right
        if entity_rect.right >= self.game.GAME_AREA_SIZE[0] and self.velocity[0] > 0:
            self.velocity[0] *= -1

        # check collision with tiles
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
