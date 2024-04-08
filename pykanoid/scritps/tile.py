from enum import auto, StrEnum, unique


@unique
class TileColor(StrEnum):
    BLUE = auto()


@unique
class TileVariant(StrEnum):
    NORMAL = auto()
    GLOSSY = auto()


_SCORES = {TileColor.BLUE: 20}

_STRENGTH = {TileColor.BLUE: 1}


class Tile:
    def __init__(
        self,
        color: TileColor,
        position,
        variant: TileVariant = TileVariant.GLOSSY,
    ):
        self.color = color
        self.position = position
        self.variant = variant
        self.score = _SCORES[color]
        self.strength = _STRENGTH[color]
