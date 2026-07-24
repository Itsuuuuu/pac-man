from src.config_parser import GameConfig
from src.tile import Tile, TileType, Pacgum
from src.characters import Ghost, Color, Pacman
import random
from collections import deque

# Y mettre les règles du jeu / fonctionnement globalement
class GameSetting:
	def __init__(self, config: GameConfig, width: int, height: int, seed: int, lives: int,  current_score: int, maze_grid: list[list[int]], pacgum: int , is_finished: bool = False):
		self.config = config
		self.width = width
		self.height = height
		self.seed = seed
		self.lives = lives
		self.current_lives = lives
		self.current_score = current_score
		self.pacgum = 0
		self.pacman = None
		self.is_finished = is_finished
		self.ghosts: list[Ghost] = []

		# Liste vierge pour recevoir le Tile de la map
		self.tile_map = []

		#Construction de la map
		self.build_map(maze_grid)
		
		# Récupérer les cases
		self.spawn_entities()

	def build_map(self, maze_grid: list[list[int]]):
		# list vide pour être remplie de list
		self.tile_map = []

		# Parcours de la matrice
		available_coords = []
		for y, row in enumerate(maze_grid):
			tile_row = []

			random.seed(self.seed)
			for x, tile in enumerate(row):
				if tile == 15:
					zone = TileType.RESERVED_CASE
					gum = Pacgum.NOTHING
				else:
					zone = TileType.AUTORISED_CASE
					gum = Pacgum.NOTHING
					available_coords.append((x,y))

				tile = Tile(x=x, y=y, walls_value=tile, zone_type=zone, content=gum)
				tile_row.append(tile)
			self.tile_map.append(tile_row)

		corners = [
			(0,0),
			(self.width -1, 0),
			(self.width -1, self.height - 1),
			(0, self.height - 1)
		]

		for corner in corners:
			if corner in available_coords:
				available_coords.remove(corner)
			corner_x, corner_y = corner
			self.tile_map[corner_y][corner_x].content = Pacgum.SUPERPACGUM

		choosen_coords = random.sample(available_coords, self.config.pacgum)
		for x, y in choosen_coords:
			self.tile_map[y][x].content = Pacgum.PACGUM
			self.pacgum +=1
		return (self.tile_map)
		
	
	def find_nearest_spawn(self, start_x: int, start_y: int) -> tuple[int, int]:
		if self.tile_map[start_y][start_x].zone_type == TileType.AUTORISED_CASE:
			return start_x, start_y
		
		queue = deque([(start_x, start_y)])
		visited = {(start_x, start_y)}

		directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
		while queue:
			current_x, current_y = queue.popleft()
			for direc_x, direc_y in directions:
				new_x, new_y = current_x + direc_x, current_y + direc_y
				if 0 <= new_x < self.width and 0 <= new_y < self.height:
					if (new_x, new_y) not in visited:
						visited.add((new_x, new_y))
						if self.tile_map[new_y][new_x].zone_type == TileType.AUTORISED_CASE:
							return new_x, new_y
						queue.append((new_x, new_y))
		return start_x, start_y

	def spawn_entities(self):
		self.ghosts = []

		# Définition des 4 coins avec décalage pour les ghosts
		ghosts_spawn = [
			{"color": Color.RED, "corner": (1,0), "offset": (0,0)},
			{"color": Color.PINK, "corner": (self.width - 1, 0), "offset": (0, 1)},
			{"color": Color.BLUE, "corner": (self.width -1, self.height -1), "offset": (-1, 0)},
			{"color": Color.ORANGE, "corner": (0, self.height - 1), "offset": (0, -1)}
		]

		# Placer les ghosts dynamiquement
		for spawn in ghosts_spawn:
			corner_x, corner_y = spawn["corner"]
			offset_x, offset_y = spawn["offset"]

			spawn_x = corner_x + offset_x
			spawn_y = corner_y + offset_y

			# Modification de la case autorisée en spawn
			self.tile_map[spawn_y][spawn_x].zone_type = TileType.SPAWN

			# Pour supprimer les pacgums sur les cases spawn
			if self.tile_map[spawn_y][spawn_x].content == Pacgum.PACGUM:
				self.tile_map[spawn_y][spawn_x].content = Pacgum.NOTHING
				self.pacgum -= 1

			# Créer et ajouter le fantomes
			new_ghost = Ghost(x=spawn_x, y=spawn_y, color=spawn["color"])
			self.ghosts.append(new_ghost)

		# Placer le pacman au centre
		center_x = self.width // 2
		center_y = self.height // 2

		spawn_x, spawn_y = self.find_nearest_spawn(center_x, center_y)

		self.tile_map[spawn_y][spawn_x].zone_type = TileType.SPAWN
		if self.tile_map[spawn_y][spawn_x].content == Pacgum.PACGUM:
			self.tile_map[spawn_y][spawn_x].content = Pacgum.NOTHING
			self.pacgum -= 1
		self.pacman = Pacman(x=spawn_x, y=spawn_y)

	def update(self, direc_x: int, direc_y: int):
		self.pacman.move_to_next(direc_x, direc_y, self.tile_map)
		blinky = None

		# Trouver Blinky
		for ghost in self.ghosts:
			if ghost.color == Color.RED:
				blinky = ghost

		# Déplacer les ghosts
		for ghost in self.ghosts:
			ghost.move(self.tile_map, self.width, self.height, self.pacman, blinky)


