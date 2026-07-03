from typing import Any
import json
import sys
from mazegenerator import MazeGenerator
from src.config_parser import GameConfig
from src.game_setting import GameSetting


def main():
	if len(sys.argv) < 2:
		print("Error usage: python3 pac-man.py config.json", file=sys.stderr)
		exit(1)

	
	config_path = sys.argv[1]
	# Ici j'ai toutes les informations qui viennent du config json
	config_data = load_json(config_path)

	# les ** servent pour unpacking + Validation Pydantic
	config = GameConfig(**config_data)

	#Isoler les données pour width, height et seed
	width = config_data['level'][0]['width']
	height = config_data['level'][0]['height']
	seed = config_data['seed']

	# Tuple pour MazeGenerator()
	size = (width, height)

	maze_gen = MazeGenerator(size=size, seed=config.seed)

	game = GameSetting(
		config = config,
		maze_grid = maze_gen.maze,
		entry = maze_gen.maze_entry,
		exit = maze_gen.maze_exit,
		shortest_path = maze_gen.shortest_path
	)

	print(f"Game initialisé avec succès ! Taille : {game.width}x{game.height}, Vies : {game.current_lives}")















	

	print(f"width: {width}")
	print(f"height: {height}")
	print(f"seed: {seed}")



	

	maze = maze_gen.maze
	maze_entry = maze_gen.maze_entry
	maze_exit = maze_gen.maze_exit
	maze_path = maze_gen.shortest_path

	print(f"maze: {maze}")
	print(f"maze_entry: {maze_entry}")
	print(f"maze_exit: {maze_exit}")
	print(f"maze_path: {maze_path}")

	# print("Config load successfully.", config_data)


def load_json(filepath: str) -> Any:
	try:
		with open(filepath, 'r' ) as file:
			return json.load(file)
		for line in file:
			line = line.strip()
			if not line or line.startswith('#'):
				continue

	except FileNotFoundError:
		print(f"Error: {filepath} not found", file=sys.stderr)
		sys.exit(1)
	except json.JSONDecodeError:
		print(
			f"Error: {filepath} invalid JSON",
			file=sys.stderr
		)
		sys.exit(1)

# def load_map(...: ...) -> ??:
# 	...



if __name__ == "__main__":
	main()
	# try:
	# 	main()
	# except Exception as error:
	# 	print("Error usage : python3 pac-man.py config.json")












# 		 Voir pour level [], sachant que:
#  				Create a simple 20x20 maze
# 						maze_gen = MazeGenerator(width=20, height=20)

# 				# Get the maze structure
#  						maze_grid = maze_gen.maze
#  						shortest_path = maze_gen.shortest_path

#  						print(f"Maze dimensions: {len(maze_grid[0])}x{len(maze_grid)}")
#  						print(f"Entry: {maze_gen.maze_entry}, Exit: {maze_gen.maze_exit}")
#  						print(f"Shortest path length: {len(shortest_path)}")
# 
# 
# 			 #### Constructor
# 
# 						```python
# 						MazeGenerator(size=(20,20), entry_cell=(0,0), exit_cell=(0,0), perfect=False, seed=0)