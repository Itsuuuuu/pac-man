import os

import pygame


# Dossier Assets a la racine du projet (src/ui/ -> ../../Assets)
ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Assets"))

# Fichiers des fantomes par couleur (+ etat "frightened" quand pacman est invincible)
GHOST_FILES = {
	"red": "ghosts/blinky.png",
	"pink": "ghosts/pinky.png",
	"blue": "ghosts/inky.png",
	"orange": "ghosts/clyde.png",
	"frightened": "ghosts/blue_ghost.png",
}

# Dossier de sprites de pacman selon sa direction
PACMAN_DIRS = {
	(1, 0): "pacman-right",
	(-1, 0): "pacman-left",
	(0, -1): "pacman-up",
	(0, 1): "pacman-down",
}

# Cache : evite de relire/redimensionner les images a chaque frame
_cache: dict = {}


def _load(path: str, size: int):
	"""Charge et met a l'echelle un sprite (nearest-neighbor pour garder le pixel-art net)."""
	key = (path, size)
	if key not in _cache:
		try:
			img = pygame.image.load(os.path.join(ASSETS_DIR, path)).convert_alpha()
			_cache[key] = pygame.transform.scale(img, (size, size))
		except (pygame.error, FileNotFoundError):
			_cache[key] = None
	return _cache[key]


def get_ghost_sprite(color_value: str, size: int, frightened: bool = False):
	name = "frightened" if frightened else color_value
	return _load(GHOST_FILES.get(name, GHOST_FILES["red"]), size)


def get_pacman_sprite(direction: tuple, frame: int, size: int):
	# Direction (0, 0) au spawn -> on affiche pacman vers la droite par defaut
	folder = PACMAN_DIRS.get(direction, "pacman-right")
	sprite_number = (frame % 3) + 1
	return _load(f"{folder}/{sprite_number}.png", size)
