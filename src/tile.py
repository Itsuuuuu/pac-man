from enum import Enum


class TileType(Enum):
    SPAWN = "spawn"
    AUTORISED_CASE = "autorised_case"
    RESERVED_CASE = "reserved_case"


class Pacgum(Enum):
    PACGUM = "pacgum"
    SUPERPACGUM = "superpacgum"
    NOTHING = "nothing"


class Tile:
    def __init__(
        self,
        x: int,
        y: int,
        walls_value: int = 15,
        zone_type: TileType = TileType.AUTORISED_CASE,
        content: Pacgum = Pacgum.NOTHING,
    ) -> None:
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.content = content
        self.walls = walls_value

        self.wall_north = bool(walls_value & 1)
        self.wall_east = bool(walls_value & 2)
        self.wall_south = bool(walls_value & 4)
        self.wall_west = bool(walls_value & 8)

    def has_wall(self, direction: int) -> bool:
        return bool(self.walls & direction)
