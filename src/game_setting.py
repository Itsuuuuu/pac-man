from src.config_parser import GameConfig

class GameSetting:
	def __init__(self, config: GameConfig, maze_grid: list[list[int]], entry: tuple[int, int], exit: tuple[int, int], shortest_path: str, is_finished: bool = False):
		self.config = config
		self.is_finished = is_finished

		self.maze_grid = maze_grid
		self.width = config.level[0].width
		self.height = config.level[0].height

		self.pacman_spawn = entry
		self.exit = exit

		self.current_lives = config.lives
		self.current_score = 0
		self.shortest_path = shortest_path
