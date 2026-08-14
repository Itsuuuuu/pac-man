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

SIDEBAR_WIDTH = 260
BOX_GAP = 16
BOX_BORDER_COLOR = (255, 255, 255)
HEART_FILLED_COLOR = (255, 0, 0)
HEART_EMPTY_COLOR = (80, 80, 80)
TIMER_WARNING_COLOR = (255, 60, 60)


def compute_layout(screen, game):
    """Calcule la taille de tuile et le decalage pour centrer le labyrinthe
    dans la fenetre.
    """
    avail_w = screen.get_width() - SIDEBAR_WIDTH - 3 * MARGIN
    avail_h = screen.get_height() - 2 * MARGIN

    # Plus grande tuile carree qui rentre dans la zone disponible
    tile = max(8, min(avail_w // game.width, avail_h // game.height))

    maze_w = tile * game.width
    maze_h = tile * game.height
    offset_x = MARGIN + (avail_w - maze_w) // 2
    offset_y = MARGIN + (avail_h - maze_h) // 2
    return tile, offset_x, offset_y


def draw_maze(screen, game, tile, offset_x, offset_y, theme):
    line_width = max(2, tile // 8)
    cap_radius = line_width // 2
    wall_color = theme["wall"]

    for row in game.tile_map:
        for t in row:
            px = offset_x + t.x * tile
            py = offset_y + t.y * tile

            segments = []
            if t.wall_north:
                segments.append(((px, py), (px + tile, py)))
            if t.wall_south:
                segments.append(((px, py + tile), (px + tile, py + tile)))
            if t.wall_east:
                segments.append(((px + tile, py), (px + tile, py + tile)))
            if t.wall_west:
                segments.append(((px, py), (px, py + tile)))

            for start, end in segments:
                pygame.draw.line(screen, wall_color, start, end, line_width)
                pygame.draw.circle(screen, wall_color, start, cap_radius)
                pygame.draw.circle(screen, wall_color, end, cap_radius)

            center = (px + tile // 2, py + tile // 2)
            if t.content == Pacgum.PACGUM:
                pygame.draw.circle(screen, GUM_COLOR, center,
                                   max(2, tile // 9))
            elif t.content == Pacgum.SUPERPACGUM:
                pygame.draw.circle(screen, GUM_COLOR, center,
                                   max(4, tile // 4))


def entity_pixels(entity, tile, offset_x, offset_y, progress):
    """Position a l'ecran d'une entite, interpolee entre sa case precedente et
    la courante.

    La logique du jeu reste sur une grille d'entiers : seule cette fonction
    voit des positions intermediaires. progress va de 0 (vient de quitter
    prev) a 1 (arrive).
    """
    x = entity.prev_x + (entity.x - entity.prev_x) * progress
    y = entity.prev_y + (entity.y - entity.prev_y) * progress
    return round(offset_x + x * tile), round(offset_y + y * tile)


def draw_entities(screen, game, tile, offset_x, offset_y,
                  pacman_progress=1.0, ghost_progress=1.0):
    # Frame d'animation basee sur le temps (change ~8x/seconde)
    frame = (pygame.time.get_ticks() // 120) % 3

    pacman = game.pacman
    top_x, top_y = entity_pixels(pacman, tile, offset_x, offset_y,
                                 pacman_progress)
    sprite = get_pacman_sprite(pacman.direction, frame, tile)
    if sprite is not None:
        screen.blit(sprite, (top_x, top_y))
    else:
        center = (top_x + tile // 2, top_y + tile // 2)
        pygame.draw.circle(screen, (255, 255, 0), center, tile // 2 - 2)

    for ghost in game.ghosts:
        gx, gy = entity_pixels(ghost, tile, offset_x, offset_y, ghost_progress)
        frightened = pacman.invincible and not ghost.is_dead
        sprite = get_ghost_sprite(ghost.color.value, tile, frightened,
                                  ghost.is_dead)
        if sprite is not None:
            screen.blit(sprite, (gx, gy))
        else:
            # Fantome mort (yeux qui rentrent au spawn) ou fallback couleur
            center = (gx + tile // 2, gy + tile // 2)
            color = (120, 120, 120) if ghost.is_dead else \
                GHOST_COLOR_MAP.get(ghost.color.value, (255, 255, 255))
            pygame.draw.circle(screen, color, center, tile // 2 - 2)


def draw_heart(screen, center_x, center_y, size, filled):
    color = HEART_FILLED_COLOR if filled else HEART_EMPTY_COLOR
    radius = size // 4

    pygame.draw.circle(
        screen, color, (center_x - radius, center_y - radius // 2), radius)
    pygame.draw.circle(
        screen, color, (center_x + radius, center_y - radius // 2), radius)

    points = [
        (center_x - size // 2, center_y - radius // 3),
        (center_x + size // 2, center_y - radius // 3),
        (center_x, center_y + size // 2),
    ]
    pygame.draw.polygon(screen, color, points)


def draw_box(screen, font, x, y, width, height, label,
             label_color=(255, 255, 255)):
    """Dessine un cadre avec un label en haut, retourne le point (x, y) ou
    dessiner le contenu.
    """
    pygame.draw.rect(screen, BOX_BORDER_COLOR, (x, y, width, height), 2)
    label_surface = font.render(label, True, label_color)
    screen.blit(label_surface, (x + 15, y + 12))
    return x + 15, y + 50


def draw_sidebar(screen, font, game, level, seconds_remaining):
    x = screen.get_width() - SIDEBAR_WIDTH - MARGIN
    y = MARGIN
    box_width = SIDEBAR_WIDTH

    # --- Score ---
    box_height = 90
    content_x, content_y = draw_box(screen, font, x, y, box_width,
                                    box_height, "SCORE", (255, 255, 0))
    score_surface = font.render(str(game.current_score), True, (255, 255, 255))
    screen.blit(score_surface, (content_x, content_y))
    y += box_height + BOX_GAP

    # --- Lives ---
    box_height = 90
    content_x, content_y = draw_box(screen, font, x, y, box_width,
                                    box_height, "LIVES", (255, 0, 0))
    heart_size = 26
    for i in range(game.lives):
        heart_x = content_x + heart_size // 2 + i * (heart_size + 10)
        heart_y = content_y + heart_size // 2
        draw_heart(screen, heart_x, heart_y, heart_size,
                   filled=i < game.current_lives)
    y += box_height + BOX_GAP

    # --- Level ---
    box_height = 90
    content_x, content_y = draw_box(screen, font, x, y, box_width,
                                    box_height, "LEVEL", (0, 255, 255))
    level_surface = font.render(str(level), True, (255, 255, 255))
    screen.blit(level_surface, (content_x, content_y))
    y += box_height + BOX_GAP

    # --- Timer ---
    box_height = 90
    timer_low = seconds_remaining <= 10
    label_color = TIMER_WARNING_COLOR if timer_low else (255, 165, 0)
    content_x, content_y = draw_box(screen, font, x, y, box_width,
                                    box_height, "TIME", label_color)
    minutes = max(0, seconds_remaining) // 60
    secs = max(0, seconds_remaining) % 60
    timer_text = f"{minutes}:{secs:02d}"
    timer_color = TIMER_WARNING_COLOR if timer_low else (255, 255, 255)
    timer_surface = font.render(timer_text, True, timer_color)
    screen.blit(timer_surface, (content_x, content_y))


def draw_game_screen(screen, game, hud_font, level, seconds_remaining, theme,
                     pacman_progress=1.0, ghost_progress=1.0):
    tile, offset_x, offset_y = compute_layout(screen, game)
    draw_maze(screen, game, tile, offset_x, offset_y, theme)
    draw_entities(screen, game, tile, offset_x, offset_y, pacman_progress,
                  ghost_progress)
    draw_sidebar(screen, hud_font, game, level, seconds_remaining)
