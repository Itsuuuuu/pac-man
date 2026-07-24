import pygame

from src.tile import Pacgum
from .assets import get_ghost_sprite, get_pacman_sprite


# Zone reservee en haut pour le HUD (score / vies)
HUD_HEIGHT = 50
# Marge autour du labyrinthe
MARGIN = 12
WALL_COLOR = (0, 0, 255)
GUM_COLOR = (255, 255, 200)

GHOST_COLOR_MAP = {
	"red": (255, 0, 0),
	"pink": (255, 182, 193),
	"blue": (0, 255, 255),
	"orange": (255, 165, 0),
}


def compute_layout(screen, game):
	"""Calcule la taille de tuile et le decalage pour centrer le labyrinthe dans la fenetre."""
	avail_w = screen.get_width() - 2 * MARGIN
	avail_h = screen.get_height() - HUD_HEIGHT - 2 * MARGIN

	# Plus grande tuile carree qui rentre dans la zone disponible
	tile = max(8, min(avail_w // game.width, avail_h // game.height))

	maze_w = tile * game.width
	maze_h = tile * game.height
	offset_x = (screen.get_width() - maze_w) // 2
	offset_y = HUD_HEIGHT + (screen.get_height() - HUD_HEIGHT - maze_h) // 2
	return tile, offset_x, offset_y


def draw_maze(screen, game, tile, offset_x, offset_y):
	line_width = max(1, tile // 12)
	for row in game.tile_map:
		for t in row:
			px = offset_x + t.x * tile
			py = offset_y + t.y * tile

			if t.wall_north:
				pygame.draw.line(screen, WALL_COLOR, (px, py), (px + tile, py), line_width)
			if t.wall_south:
				pygame.draw.line(screen, WALL_COLOR, (px, py + tile), (px + tile, py + tile), line_width)
			if t.wall_east:
				pygame.draw.line(screen, WALL_COLOR, (px + tile, py), (px + tile, py + tile), line_width)
			if t.wall_west:
				pygame.draw.line(screen, WALL_COLOR, (px, py), (px, py + tile), line_width)

			center = (px + tile // 2, py + tile // 2)
			if t.content == Pacgum.PACGUM:
				pygame.draw.circle(screen, GUM_COLOR, center, max(2, tile // 9))
			elif t.content == Pacgum.SUPERPACGUM:
				pygame.draw.circle(screen, GUM_COLOR, center, max(4, tile // 4))


def draw_entities(screen, game, tile, offset_x, offset_y):
	# Frame d'animation basee sur le temps (change ~8x/seconde)
	frame = (pygame.time.get_ticks() // 120) % 3

	pacman = game.pacman
	top_x = offset_x + pacman.x * tile
	top_y = offset_y + pacman.y * tile
	sprite = get_pacman_sprite(pacman.direction, frame, tile)
	if sprite is not None:
		screen.blit(sprite, (top_x, top_y))
	else:
		center = (top_x + tile // 2, top_y + tile // 2)
		pygame.draw.circle(screen, (255, 255, 0), center, tile // 2 - 2)

	for ghost in game.ghosts:
		gx = offset_x + ghost.x * tile
		gy = offset_y + ghost.y * tile
		frightened = pacman.invincible and not ghost.is_dead
		sprite = get_ghost_sprite(ghost.color.value, tile, frightened)
		if sprite is not None and not ghost.is_dead:
			screen.blit(sprite, (gx, gy))
		else:
			# Fantome mort (yeux qui rentrent au spawn) ou fallback couleur
			center = (gx + tile // 2, gy + tile // 2)
			color = (120, 120, 120) if ghost.is_dead else GHOST_COLOR_MAP.get(ghost.color.value, (255, 255, 255))
			pygame.draw.circle(screen, color, center, tile // 2 - 2)


def draw_hud(screen, font, game):
	score_text = font.render(f"Score: {game.current_score}", True, (255, 255, 0))
	screen.blit(score_text, (MARGIN, 12))

	lives_text = font.render(f"Lives: {game.current_lives}", True, (255, 0, 0))
	lives_rect = lives_text.get_rect(topright=(screen.get_width() - MARGIN, 12))
	screen.blit(lives_text, lives_rect)


def draw_game_screen(screen, game, hud_font=None):
	tile, offset_x, offset_y = compute_layout(screen, game)
	draw_maze(screen, game, tile, offset_x, offset_y)
	draw_entities(screen, game, tile, offset_x, offset_y)
	if hud_font is not None:
		draw_hud(screen, hud_font, game)
