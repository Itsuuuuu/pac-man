from src.tile import TileType, Tile
from enum import Enum
from src.ghost_algo import bfs_next_step, wall_from_tiles
import random

class Color(Enum):
	RED = "red"
	PINK = "pink"
	BLUE = "blue"
	ORANGE = "orange"

class Pacman:
	def __init__(self, x: int, y: int, invinsible: bool = False):
		self.x = x
		self.y = y
		self.spawn_x = x
		self.spawn_y = y
		self.direction = (0, 0)
		self.invinsible = invinsible

	# Pour faire avancer le pacman sur la prochaine case
	def move_to_next(self, direc_x: int, direc_y: int, tile_map: list[list[Tile]]):
		# Permet de convertir un déplacement en une direction (N, E, S, W)
		direction_flag = 0
		if (direc_x, direc_y) == (0, -1): direction_flag = 1
		elif (direc_x, direc_y) == (1, 0): direction_flag = 2
		elif(direc_x, direc_y) == (0, 1): direction_flag = 4
		elif (direc_x, direc_y) == (-1, 0): direction_flag = 8

		if direction_flag == 0:
			return
		
		current_tile = tile_map[self.y][self.x]
		# Verification mur, si non, déplacement
		if not current_tile.has_wall(direction_flag):
			self.x += direc_x
			self.y += direc_y
			self.direction = (direc_x, direc_y)
	
	# Si le Pacman se fait attraper par un ghost, il se fait tp au point de spawn
	def back_to_spawn(self):
		self.x = self.spawn_x
		self.y = self.spawn_y
		self.direction(0, 0)
	
	#Si le Pacman passe sur un super pacgum, on passe is_invinsible en true pour quelques secondes
	def is_invinsible(self):
		#mettre un timer 
		return self.invinsible


class Ghost:
	def __init__(self, x : int, y : int, current_zone: TileType = TileType.SPAWN, color: Color = Color.RED):
		self.x = x
		self.y = y
		self.spawn_x = x
		self.spawn_y = y
		self.current_zone = current_zone
		self.color = color
		self.is_dead = False

	#Doit devenir des petits yeux, et bfs vers la case de son spawn
	def back_to_spawn(self):
		self.is_dead = True
	
	def run_to_spawn(self, width: int, height: int) -> tuple[int, int]:
		if self.color == Color.RED:
			return(width -2, 1)
		elif self.color == Color.PINK:
			return(1, 1)
		elif self.color == Color.BLUE:
			return (width -2, height -2)
		else:
			return (1, height -2)

	# Empeche qu'une coordonnée sorte de la map
	def block(self, val: int, min_val: int, max_val: int) -> int:
		return max(min_val, min(val, max_val))
	
	def get_target(self, pacman: Pacman, blinky: 'Ghost', width: int, height: int) -> tuple[int, int]:
		if self.is_dead:
			return (self.spawn_x, self.spawn_y)
		
		# Si pacman est invinsible, les ghosts fuient dans leurs coin
		if pacman.invinsible:
			return self.run_to_spawn(width, height)
		
		# Cible pacman
		if self.color == Color.RED:
			return (pacman.x, pacman.y)
		
		# Vise 4 cases devant pacman
		elif self.color == Color.PINK:
			pac_direc_x, pac_direc_y = pacman.direction
			target_x = self.block(pacman.x + 4 * pac_direc_x, 0, width -1)
			target_y = self.block(pacman.y + 4 * pac_direc_y, 0, height -1)
			return (target_x, target_y)
		
		# Truc chiant entre blinky et pacman, il prend les cases entre pacman et rouge
		# et il double la distance, et cette case sera la cible
		elif self.color == Color.BLUE:
			if blinky is None:
				return (pacman.x, pacman.y)
			pacman_direc_x, pac_direc_y = pacman.direction
			pac_direc_x = pacman.x + 2 * pacman_direc_x
			pac_direc_y = pacman.y + 2 * pac_direc_y

			target_x = self.block(2 * pac_direc_x - blinky.x, 0, width - 1)
			target_y = self.block(2 * pac_direc_y - blinky.y, 0, height - 1)
			return (target_x, target_y)
		
		# Mouvement Aléatoire
		elif self.color == Color.ORANGE:
			target_x = random.randint(1, width -2)
			target_y = random.randint(1, height -2)
			return (target_x, target_y)

	# On met en paramètre Blinky car Inky à besoin de connaître sa position pour bouger
	def move(self, tile_map: list[list[Tile]], width: int, height: int, pacman: Pacman, blinky: 'Ghost'):
		target = self.get_target(pacman, blinky, width, height)
		has_wall = wall_from_tiles(tile_map)
		next_step = bfs_next_step(has_wall, width, height, (self.x, self.y), target)
		if next_step is not None:
			self.x, self.y = next_step
		if self.is_dead and (self.x, self.y) == (self.spawn_x, self.spawn_y):
			self.is_dead = False


