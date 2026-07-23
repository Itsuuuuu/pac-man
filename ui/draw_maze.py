import pygame
import json
import sys

from mazegenerator import MazeGenerator
from src.config_parser import GameConfig
from src.game_setting import GameSetting
from src.tile import Pacgum


TILE_SIZE = 40
MAZE_OFFSET_X = 50
MAZE_OFFSET_Y = 50

GHOST_COLOR_MAP = {
	"red": (255, 0, 0),
	"pink": (255, 182, 193),
	"blue": (0, 255, 255),
	"orange": (255, 165, 0),
}


def load_config(filepath):
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

def draw_maze(screen, game):
	for row in game.tile_map:
		for tile in row:
			px = MAZE_OFFSET_X + tile.x * TILE_SIZE
			py = MAZE_OFFSET_Y + tile.y * TILE_SIZE

			if tile.wall_north:
				pygame.draw.line(screen, (0, 0, 255), (px, py), (px + TILE_SIZE, py), 3)
			if tile.wall_south:
				pygame.draw.line(screen, (0, 0, 255), (px, py + TILE_SIZE), (px + TILE_SIZE, py + TILE_SIZE), 3)
			if tile.wall_east:
				pygame.draw.line(screen, (0, 0, 255), (px + TILE_SIZE, py), (px + TILE_SIZE, py + TILE_SIZE), 3)
			if tile.wall_west:
				pygame.draw.line(screen, (0, 0, 255), (px, py), (px, py + TILE_SIZE), 3)

			center = (px + TILE_SIZE // 2, py + TILE_SIZE // 2)
			if tile.content == Pacgum.PACGUM:
				pygame.draw.circle(screen, (255, 255, 200), center, 4)
			elif tile.content == Pacgum.SUPERPACGUM:
				pygame.draw.circle(screen, (255, 255, 200), center, 10)


def draw_entities(screen, game):
	pacman = game.pacman
	px = MAZE_OFFSET_X + pacman.x * TILE_SIZE + TILE_SIZE // 2
	py = MAZE_OFFSET_Y + pacman.y * TILE_SIZE + TILE_SIZE // 2
	pygame.draw.circle(screen, (255, 255, 0), (px, py), TILE_SIZE // 2 - 4)

	for ghost in game.ghosts:
		gx = MAZE_OFFSET_X + ghost.x * TILE_SIZE + TILE_SIZE // 2
		gy = MAZE_OFFSET_Y + ghost.y * TILE_SIZE + TILE_SIZE // 2
		color = GHOST_COLOR_MAP.get(ghost.color.value, (255, 255, 255))
		pygame.draw.circle(screen, color, (gx, gy), TILE_SIZE // 2 - 4)


def draw_game_screen(screen, game):
	draw_maze(screen, game)
	draw_entities(screen, game)