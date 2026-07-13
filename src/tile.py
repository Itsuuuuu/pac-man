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
	def __init__(self,  x: int, y: int, walls: int = 15, zone_type: TileType = TileType.AUTORISED_CASE, content: Pacgum = Pacgum.NOTHING):
		self.x = x
		self.y = y
		self.walls = walls
		self.zone_type = zone_type
		self.content = content
	
	def has_wall(self, direction: int) -> bool:
		return bool(self.walls & direction)
