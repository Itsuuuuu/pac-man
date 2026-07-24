from typing import Any
import json
import sys

from mazegenerator import MazeGenerator
from src.config_parser import GameConfig
from src.game_setting import GameSetting


def load_json(filepath: str) -> Any:
	"""Charge un fichier JSON en ignorant les lignes vides et les commentaires (#)."""
	try:
		cleaned_lines = []
		with open(filepath, "r") as file:
			for line in file:
				line = line.strip()
				if not line or line.startswith("#"):
					continue
				cleaned_lines.append(line)
		return json.loads("\n".join(cleaned_lines))

	except FileNotFoundError:
		print(f"Error: {filepath} not found", file=sys.stderr)
		sys.exit(1)
	except json.JSONDecodeError:
		print(f"Error: {filepath} invalid JSON", file=sys.stderr)
		sys.exit(1)


def build_game(config_path: str) -> GameSetting:
	"""Construit une partie complète (config + labyrinthe + entites) depuis un fichier de config."""
	config_data = load_json(config_path)

	# Les ** servent pour l'unpacking + la validation Pydantic
	config = GameConfig(**config_data)

	width = config_data["level"][0]["width"]
	height = config_data["level"][0]["height"]
	seed = config_data["seed"]
	lives = config_data["lives"]
	pacgum = config_data["pacgum"]
	current_score = config_data.get("current_score", 0)
	is_finished = config_data.get("is_finished", False)

	# Generation du labyrinthe
	maze_gen = MazeGenerator(size=(width, height), seed=config.seed)

	return GameSetting(
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
