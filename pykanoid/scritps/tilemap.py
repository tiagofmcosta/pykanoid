import pygame
from pygame import Surface

from pykanoid.scritps.tile import Tile, TileColor
from pykanoid.scritps.utils import load_images, RANDOM_GENERATOR
from pykanoid.settings import *

NEIGHBOR_OFFSETS = [
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, -1),
    (0, 0),
    (0, 1),
    (1, -1),
    (1, 0),
    (1, 1),
]


class Tilemap:
    def __init__(self, game):
        self.game = game
        self.tile_size = (64, 32)
        self.grid_size = (self.game.game_surface.get_width() // self.tile_size[0], 12)
        self.tilemap: dict[tuple[int, int], Tile] = {}
        self.offgrid_tiles = []

        self.__assets: dict[str, dict[TileColor, dict[str, Surface]]] = {"tiles": {}}
        for t_color in TileColor:
            self.__assets["tiles"][t_color] = load_images("tiles/%s" % t_color)

        colors = [c for c in list(TileColor) if c != TileColor.GREY]

        for x in range(self.grid_size[0]):
            for y in range(self.grid_size[1]):
                location = (x, y)
                self.tilemap[location] = Tile(RANDOM_GENERATOR.choice(colors), location)

    def tiles_around(self, position):
        tile_loc = (
            int(position[0] // self.tile_size[0]),
            int(position[1] // self.tile_size[1]),
        )
        tiles = []
        for offset in NEIGHBOR_OFFSETS:
            check_loc = (tile_loc[0] + offset[0], tile_loc[1] + offset[1])
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        return tiles

    def rects(self, tiles):
        rects = []
        for tile in tiles:
            rects.append(
                pygame.Rect(
                    tile.position[0] * self.tile_size[0],
                    tile.position[1] * self.tile_size[1],
                    self.tile_size[0],
                    self.tile_size[1],
                )
            )
        return rects

    def trigger_hit(self, tile: Tile):
        if tile.strength > 0:
            self.game.status.update_score(tile.score)
            next_tile = tile.get_next_tile()

            if next_tile:
                self.tilemap[tile.position] = tile.get_next_tile()
            else:
                del self.tilemap[tile.position]

    def render(self, surface: pygame.Surface):
        for tile in self.offgrid_tiles:
            surface.blit(
                self.__assets["tiles"][tile.color][tile.variant + ".png"],
                tile.position,
            )

        for position in self.tilemap:
            tile = self.tilemap[position]
            image = self.__assets["tiles"][tile.color][tile.variant + ".png"]
            pygame.draw.rect(
                image,
                BACKGROUND_COLOR,
                [
                    0,
                    0,
                    self.tile_size[0],
                    self.tile_size[1],
                ],
                1,
            )
            surface.blit(
                image,
                (
                    tile.position[0] * self.tile_size[0],
                    tile.position[1] * self.tile_size[1],
                ),
            )
