from enum import auto, StrEnum, unique


@unique
class TileColor(StrEnum):
    GREEN = auto()
    BLUE = auto()
    YELLOW = auto()
    PURPLE = auto()
    RED = auto()
    GREY = auto()


@unique
class TileVariant(StrEnum):
    NORMAL = auto()
    GLOSSY = auto()


_SCORES = {
    TileColor.GREEN: 20,
    TileColor.BLUE: 23,
    TileColor.YELLOW: 29,
    TileColor.PURPLE: 38,
    TileColor.RED: 50,
    TileColor.GREY: 0,
}

_STRENGTH = {
    TileColor.GREEN: 1,
    TileColor.BLUE: 2,
    TileColor.YELLOW: 3,
    TileColor.PURPLE: 4,
    TileColor.RED: 5,
    TileColor.GREY: -1,
}


class Tile:
    def __init__(
        self,
        color: TileColor,
        position,
        variant: TileVariant = TileVariant.NORMAL,
    ):
        self.color = color
        self.position = position
        self.variant = variant
        self.strength = _STRENGTH[color]
        self.score = _SCORES[color]

    def get_next_tile(self):
        colors = list(_STRENGTH)
        index = colors.index(self.color) - 1

        if index < 0:
            return None

        return Tile(colors[index], self.position, self.variant)
