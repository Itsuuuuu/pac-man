import pygame
import math
from .utils import ordinal


def draw_pacman(screen, x, y, circle, mouth_angle=20):
    pygame.draw.circle(screen, (255, 255, 0), (x, y), circle)
    mouth_angle = 20
    point_top = (
        x + circle * math.cos(math.radians(-mouth_angle)) * 5,
        y + circle * math.sin(math.radians(-mouth_angle)) * 5,
    )
    point_bottom = (
        x + circle * math.cos(math.radians(mouth_angle)),
        y + circle * math.sin(math.radians(mouth_angle)),
    )
    pygame.draw.polygon(screen, (0, 0, 0), [(x, y), point_top, point_bottom])


def draw_menu(screen, font, title_font, height, options, menu_index):
    title_surface = title_font.render("Pac-Man", True, (255, 255, 0))
    title_rect = title_surface.get_rect(center=(height // 2, 100))  #
    screen.blit(title_surface, title_rect)

    for i, option in enumerate(options):
        text = font.render(option, True, (255, 0, 0))
        text_rect = text.get_rect(center=(height // 2, 300 + i * 100))  #
        screen.blit(text, text_rect)
        if i == menu_index:
            circle = 15
            x = text_rect.left - 50
            y = text_rect.centery
            draw_pacman(screen, x, y, circle, mouth_angle=20)


def draw_game(screen, title_font, height):
    title = title_font.render("Game", True, (255, 255, 0))
    title_rect = title.get_rect(center=(height // 2, 100))  #
    screen.blit(title, title_rect)


def draw_options(
        screen,
        font,
        title_font,
        height,
        options_options,
        options_index,
        screen_dimensions,
        dimension_index
                 ):
    global text
    title = title_font.render("Options", True, (255, 255, 0))
    title_rect = title.get_rect(center=(height // 2, 100))  
    screen.blit(title, title_rect)

    for i in range(len(options_options)):
        if i == 1:
            largeur, hauteur = screen_dimensions[dimension_index]
            texte = f"Dimensions : {largeur} x {hauteur}"
        else:
            texte = options_options[i]
        text = font.render(texte, True, (255, 255, 255))
        text_rect = text.get_rect(center=(height // 2, 300 + i * 100))
        screen.blit(text, text_rect)
        if i == options_index:
            circle = 15
            x = text_rect.left - 50
            y = text_rect.centery
            draw_pacman(screen, x, y, circle, mouth_angle=20)


def draw_highscores(screen, font, title_font, height, highscores):
    title = title_font.render("High Scores", True, (255, 255, 0))
    title_rect = title.get_rect(center=(height // 2, 100))
    screen.blit(title, title_rect)

    header_y = 220
    rank_header = font.render("Rank", True, (250, 7, 7))
    screen.blit(rank_header, rank_header.get_rect(center=(height // 4, header_y)))

    score_header = font.render("Name", True, (250, 7, 7))
    screen.blit(score_header, score_header.get_rect(center=(height // 2, header_y)))

    name_header = font.render("Score", True, (250, 7, 7))
    screen.blit(name_header, name_header.get_rect(center=(height // 1.3, header_y)))

    row_colors = [
        (255, 111, 97), (0, 119, 182), (129, 217, 178), (147, 112, 219),
        (230, 179, 41), (255, 0, 122), (25, 42, 86), (204, 85, 0),
        (112, 128, 144), (64, 224, 208),
	]
    
    for i, entry in enumerate(highscores):
        pseudo = entry["pseudo"]
        score = entry["score"]
        y = 280 + i * 50
        color = row_colors[i % len(row_colors)]


        rank_text = font.render(ordinal(i + 1), True, color)
        rank_rect = rank_text.get_rect(center=(height // 4, y))
        screen.blit(rank_text, rank_rect)

        pseudo_text = font.render(pseudo, True, color)
        pseudo_rect = pseudo_text.get_rect(center=(height // 2, y))
        screen.blit(pseudo_text, pseudo_rect)

        score_text = font.render(str(score), True, color)
        score_rect = score_text.get_rect(center=(height // 1.3, y))
        screen.blit(score_text, score_rect)




def draw_cheat(screen, font, title_font, height, cheats, cheat_states, cheat_value, cheat_index):
    title = title_font.render("Cheat", True, (255, 255, 0))
    title_rect = title.get_rect(center=(height // 2, 100))
    screen.blit(title, title_rect)

    for i, cheat in enumerate(cheats):
        if cheat in cheat_states:
            status = "ON" if cheat_states[cheat] else "OFF"
            color = (0, 255, 0) if cheat_states[cheat] else (255, 255, 255)
            label = f"{cheat}: {status}"
        else:
            color = (255, 255, 255)
            label = f"{cheat} : < {cheat_value[cheat]} >"
        
        text = font.render(label, True, color)
        text_rect = text.get_rect(center=(height // 2, 400 + i * 100))
        screen.blit(text, text_rect)

        if i == cheat_index:
            circle = 15
            x = text_rect.left - 50
            y = text_rect.centery
            draw_pacman(screen, x, y, circle, mouth_angle=20)