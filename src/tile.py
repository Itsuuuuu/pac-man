from enum import Enum

class TileType(Enum):
	SPAWN = "spawn"
	AUTORISED_CASE = "autorised_case"
	RESERVED_CASE = "reserved_case"

class Tile:
	def __init__(self,  x: int, y: int, zone_type: TileType = TileType.AUTORISED_CASE):
		self.zone_type = zone_type
		self.x = x
		self.y = y
