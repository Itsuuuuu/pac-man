from typing import Any
import json
import sys
from mazegenerator import MazeGenerator
from src.config_parser import GameConfig
from src.game_setting import GameSetting
import time
import ui


def load_json(filepath: str) -> Any:
	try:
		cleaned_lines = []
		with open(filepath, 'r' ) as file:
			for line in file:
				line = line.strip()
				if not line or line.startswith('#'):
					continue
				cleaned_lines.append(line)
		json_content = "\n".join(cleaned_lines)
		return json.loads(json_content)

	except FileNotFoundError:
		print(f"Error: {filepath} not found", file=sys.stderr)
		sys.exit(1)
	except json.JSONDecodeError:
		print(
			f"Error: {filepath} invalid JSON",
			file=sys.stderr
		)
	sys.exit(1)

def debug_print_game(game: GameSetting):
	"""Fonction de debug temporaire pour afficher le labyrinthe et valider les spawns"""
	print("\n=== TEST DE COMPILATION ET D'INITIALISATION ===")
	print(f"Labyrinthe chargé ! Taille : {game.width}x{game.height}")
	print(f"Nombre total de Pacgums placés : {game.pacgum}")
	print(f"Position de Pacman : ({game.pacman.x}, {game.pacman.y})")
	print("Positions de départ des fantômes :")
	for ghost in game.ghosts:
		print(f"  - {ghost.color.value.upper()} : ({ghost.x}, {ghost.y})")
	print("==============================================\n")

	# Dessin de la map dans la console
	print("Aperçu de la carte générée (P = Pacman, G = Fantômes, # = Murs pleins, . = Pacgums, O = Super Pacgums) :")
	for y in range(game.height):
		row_str = ""
		for x in range(game.width):
			tile = game.tile_map[y][x]
			
			# On regarde qui est sur la case
			if game.pacman.x == x and game.pacman.y == y:
				row_str += " P "  # Pacman
			elif any(g.x == x and g.y == y for g in game.ghosts):
				row_str += " G "  # Un fantôme
			elif tile.walls == 15:
				row_str += "###"  # Case bloquée / Mur plein
			elif tile.content.value == "superpacgum":
				row_str += " O "  # Super Pacgum
			elif tile.content.value == "pacgum":
				row_str += " . "  # Pacgum normal
			else:
				row_str += "   "  # Case vide autorisée
		print(row_str)
	print("\nLa compilation est OK et le placement dynamique fonctionne ! 🚀\n")


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

	ui.init()
	screen = ui.display.set_mode((width * 20, height * 20))
	ui.display.set_caption("Pac-Man")
	clock = ui.time.Clock()
	direc_x, direc_y = 0, 0

	while not game.is_finished:
		clock.tick(10)


if __name__ == "__main__":
	try:
		main()
	except Exception as error:
		# TEMPORAIRE
		import traceback
		# TEMPORAIRE
		traceback.print_exc()
		# ON GARDE 
		print("Error usage : python3 pac-man.py config.json")

