from src.config_parser import GameConfig
from src.tile import Tile, TileType, Pacgum
from src.characters import Ghost, Color, Pacman

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

	def build_map(self, tile_map):
		# self.tile_map = []
		# for y, row in enumerate(tile_row):
		# 	tile_row = []
		# 	for x, walls in enumerate(row):
		# 		# 1. Analyser 'val' pour trouver le bon TileType et le bon Pacgum
		# 		# Si val == 15 -> zone_type = TileType.RESERVED_CASE, content = Pacgum.NOTHING
		# 		# Sinon -> zone_type = TileType.AUTORISED_CASE, content = Pacgum.PACGUM
		# 		# (Et si c'est une Pacgum, tu fais self.pacgum += 1 !)
				
		# 		# 2. Instancier l'objet Tile avec les bons paramètres
		# 		# tile = Tile(x=x, y=y, zone_type=..., content=...)
				
		# 		# 3. L'ajouter à la ligne en cours
		# 		# tile_row.append(tile)
		# 		...
		# 	self.tile_map.append(tile_row)
		...
		
	
	def spawn_entities(self):
		...












