from src.config_parser import GameConfig

class GameSetting:
	def __init__(self, config: GameConfig, maze_grid: list[list[int]], entry: tuple[int, int], exit: tuple[int, int], shortest_path: str):
		self.config = config

		self.maze_grid = maze_grid
		self.width = config.level[0].width
		self.height = config.level[0].height

		self.pacman_spawn = entry
		# self.ghost_spawn = # dans les 4 coins et randomizé
		self.exit = exit

		self.current_lives = config.lives
		self.current_score = 0
		self.shortest_path = shortest_path
