from typing import Any
import json
import sys
from mazegenerator import MazeGenerator


def main():
	if len(sys.argv) < 2:
		print("Error usage: python3 pac-man.py config.json", file=sys.stderr)
		exit(1)

	maze_gen = MazeGenerator()
	maze_grid = maze_gen.maze
	shortest_path = maze_gen.shortest_path

	print(f"Maze dimensions: {len(maze_grid[0])}x{len(maze_grid)}")
	print(f"Entry: {maze_gen.maze_entry}, Exit: {maze_gen.maze_exit}")
	print(f"Shortest path length: {len(shortest_path)}")

	config_path = sys.argv[1]
	config_data = load_json(config_path)
	print("Config load successfully.", config_data)


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