import pygame

from pykanoid.scritps.status import State, Status
from pykanoid.scritps.utils import RANDOM_GENERATOR


class PhysicsEntity:
    def __init__(self, game, e_type, position, asset: pygame.Surface):
        self.game = game
        self.type = e_type
        self.position = list(position)
        self.asset = asset
        self.velocity = [0, 0]
        self.acceleration = 5

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
        # rect = self.rect()
        # pygame.draw.line(
        #     surface,
        #     "Yellow",
        #     (rect.centerx, rect.centery - 25),
        #     (rect.centerx, rect.centery + 25),
        # )


class Paddle(PhysicsEntity):

    def update(self, movement=(0, 0)):
        super().update(movement)

        if self.position[0] <= 0:
            self.position[0] = 0
        if self.position[0] >= self.game.GAME_AREA_SIZE[0] - self.asset.get_width():
            self.position[0] = self.game.GAME_AREA_SIZE[0] - self.asset.get_width()


class Ball(PhysicsEntity):
    def __init__(self, game, e_type, position, size):
        super().__init__(game, e_type, position, size)
        self.acceleration = 3

    def start(self):
        self.velocity = [RANDOM_GENERATOR.choice((-1, 1)), -1]

    def reset(self):
        self.velocity = [0, 0]
        self.position = [
            self.game.paddle.position[0]
            + self.game.paddle.asset.get_width() / 2
            - self.asset.get_width() / 2,
            self.game.paddle.position[1] - self.asset.get_height(),
        ]

    def update(self, movement=(0, 0)):
        self.position = [
            self.game.paddle.position[0]
            + self.game.paddle.asset.get_width() / 2
            - self.asset.get_width() / 2,
            self.game.paddle.position[1] - self.asset.get_height(),
        ]

    def move(self):
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
            if entity_rect.bottom <= paddle_rect.centery:
                entity_rect.bottom = paddle_rect.top
                self.position[1] = entity_rect.y
                self.velocity[1] *= -1
            else:
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

        tiles = self.game.tilemap.tiles_around(self.position)
        tile_recs = self.game.tilemap.rects(tiles)
        tile_collision = entity_rect.collidelist(tile_recs)

        if tile_collision > 0:
            self.game.tilemap.trigger_hit(tiles[tile_collision])
            self.velocity[1] *= -1
