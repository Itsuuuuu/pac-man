from tile import TileType, Tile
from enum import Enum


class Color(Enum):
	RED = "red"
	PINK = "pink"
	BLUE = "blue"
	ORANGE = "orange"

class Pacman:
	def __init__(self, x: int, y: int, current_zone: Tile, invinsible: bool = False):
		self.x = x
		self.y = y
		self.current_zone = current_zone
		self.invinsible = invinsible

	# Pour faire avancer le pacman sur la prochaine case
	def move_to_next(self):
		...
	
	# Si le Pacman se fait attraper par un ghost, il se fait tp au point de spawn
	def back_to_spawn(self):
		...
	
	#Si le Pacman passe sur un super pacgum, on passe is_invinsible en true pour quelques secondes
	def is_invisible(self):
		...


class Ghost:
	def __init__(self, x : int, y : int, current_zone: TileType = TileType.SPAWN, color: Color = Color):
		self.x = x
		self.y = y
		self.current_zone = current_zone

	#Doit devenir des petits yeux, et bfs vers la case de son spawn
	def back_to_spawn(self):
		...
