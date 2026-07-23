import sys
from mazegenerator import MazeGenerator
from src.config_parser import GameConfig
from src.game_setting import GameSetting
from src.tile import Pacgum


def load_config(filepath):
	import json
	try:
		with open(filepath, "r") as file:
			return json.load(file)
	except FileNotFoundError:
		print(f"Error: {filepath} not found", file=sys.stderr)
		sys.exit(1)
	except json.JSONDecodeError:
		print(f"Error: {filepath} invalid JSON", file=sys.stderr)
		sys.exit(1)


def build_game(config_path):
	config_data = load_config(config_path)
	config = GameConfig(**config_data)

	width = config_data["level"][0]["width"]
	height = config_data["level"][0]["height"]
	seed = config_data["seed"]
	lives = config_data["lives"]
	pacgum = config_data["pacgum"]
	current_score = config_data.get("current_score", 0)
	is_finished = config_data.get("is_finished", False)

	maze_gen = MazeGenerator(size=(width, height), seed=config.seed)

	game = GameSetting(
		config=config,
		width=width,
		height=height,
		seed=seed,
		lives=lives,
		maze_grid=maze_gen.maze,
		pacgum=pacgum,
		is_finished=is_finished,
		current_score=current_score,
	)
	return game


def main():
	if len(sys.argv) < 2:
		print("Error usage: python3 main.py config.json", file=sys.stderr)
		sys.exit(1)

	game = build_game(sys.argv[1])

	print(f"Level (width x height) : {game.width}x{game.height}")
	print(f"Lives : {game.current_lives}")
	print(f"Score : {game.current_score}")
	print(f"Pacgum restants : {game.pacgum}")

	print(f"\nPacman position : ({game.pacman.x}, {game.pacman.y})")

	print("\nGhosts :")
	for ghost in game.ghosts:
		print(f"  {ghost.color.value} -> ({ghost.x}, {ghost.y})")

	print("\nCoordonnees des pacgums normaux :")
	for row in game.tile_map:
		for tile in row:
			if tile.content == Pacgum.PACGUM:
				print(f"  ({tile.x}, {tile.y})")

	print("\nCoordonnees des superpacgums :")
	for row in game.tile_map:
		for tile in row:
			if tile.content == Pacgum.SUPERPACGUM:
				print(f"  ({tile.x}, {tile.y})")

	print("\nMurs de la grille (x, y) -> N/E/S/W :")
	for row in game.tile_map:
		for tile in row:
			walls = ""
			walls += "N" if tile.wall_north else "-"
			walls += "E" if tile.wall_east else "-"
			walls += "S" if tile.wall_south else "-"
			walls += "W" if tile.wall_west else "-"
			print(f"  ({tile.x}, {tile.y}) -> {walls}")


if __name__ == "__main__":
	main()