from typing import Any
import json
import sys
from mazegenerator import MazeGenerator


def main():
	if len(sys.argv) < 2:
		print("Error usage: python3 pac-man.py config.json", file=sys.stderr)
		exit(1)




	print(dir(mazegenerator))
	# print()
	generator = mazegenerator.MazeGenerator()
	
	# 1. On lance la génération du labyrinthe
	generator.generate()
	
	# 2. On récupère la map stockée dans l'attribut prévu à cet effet
	ma_map = generator.maze  # Si 'maze' est vide, on testera generator._maze
	
	print("--- Infos Labyrinthe ---")
	print(f"Type de l'attribut maze : {type(ma_map)}")
	
	# 3. Si c'est bien une matrice (liste de listes) ou une liste de chaînes, on mesure :
	if hasattr(ma_map, '__len__') and len(ma_map) > 0:
		print(f"Hauteur (lignes) : {len(ma_map)}")
		print(f"Largeur (colonnes) : {len(ma_map[0])}")
		print("\nAperçu des 3 premières lignes :")
		for ligne in ma_map[:3]:
			print(ligne)
	else:
		# Si 'maze' n'est pas directement mesurable, on regarde les attributs de dimension
		print(f"Largeur via _width : {generator._width}")
		print(f"Hauteur via _height : {generator._height}")

	# config_path = sys.argv[1]
	# config_data = load_json(config_path)
	# print("Config load successfully.", config_data) #Pour vérifier si tout fonctionne


def load_json(filepath: str) -> Any:
	try:
		with open(filepath, 'r' ) as file:
			return json.load(file)
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
	try:
		main()
	except Exception as error:
		print("Error usage : python3 pac-man.py config.json")