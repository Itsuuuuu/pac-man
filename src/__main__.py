from typing import Any
import json
import sys
from mazegenerator import MazeGenerator
from src.config_parser import GameConfig
from src.game_setting import GameSetting
import time
import pygame


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

	# Récupérer les autres données
	lives = config_data['lives']
	is_finished = config_data.get('is_finished', False)
	pacgum = config_data['pacgum']
	current_score = config_data.get('current_score', 0)

	# Tuple pour MazeGenerator()
	size = (width, height)

	# La map se créer
	maze_gen = MazeGenerator(size=size, seed=config.seed)

	game = GameSetting(
		config = config,
		width = width,
		height = height,
		seed = seed,
		lives = lives,
		maze_grid = maze_gen.maze,
		pacgum = pacgum,
		is_finished = is_finished,
		current_score = current_score, 
	)

	pygame.init()
	screen = pygame.display.set_mode((width * 20, height * 20))
	pygame.display.set_caption("Pac-Man")
	clock = pygame.time.Clock()
	direc_x, direc_y = 0, 0

	while not game.is_finished:
		clock.tick(10)



if __name__ == "__main__":
	try:
		main()
	except Exception as error:
		print("Error usage : python3 pac-man.py config.json")

