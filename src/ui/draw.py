import pygame

from .assets import get_pacman_sprite
from .utils import Highscore, Rgb, Theme, ordinal


def draw_cursor(
    screen: pygame.Surface,
    x: int,
    y: int,
    size: int = 40,
) -> None:
    frame = (pygame.time.get_ticks() // 120) % 3
    sprite = get_pacman_sprite((1, 0), frame, size)
    if sprite is not None:
        rect = sprite.get_rect(center=(x, y))
        screen.blit(sprite, rect)
    else:
        pygame.draw.circle(screen, (255, 255, 0), (x, y), size // 2)


def draw_menu(
    screen: pygame.Surface,
    font: pygame.font.Font,
    title_font: pygame.font.Font,
    height: int,
    options: list[str],
    menu_index: int,
    theme: Theme,
) -> list[pygame.Rect]:
    title_surface = title_font.render("Pac-Man", True, theme["title"])
    title_rect = title_surface.get_rect(center=(height // 2, 100))
    screen.blit(title_surface, title_rect)
    option_rects: list[pygame.Rect] = []
    for i, option in enumerate(options):
        color = theme["highlight"] if i == menu_index else theme["text"]
        text = font.render(option, True, color)
        text_rect = text.get_rect(center=(height // 2, 250 + i * 100))
        screen.blit(text, text_rect)
        option_rects.append(text_rect)
        if i == menu_index:
            x = text_rect.left - 50
            y = text_rect.centery
            draw_cursor(screen, x, y, size=40)

    return option_rects


def draw_options(
    screen: pygame.Surface,
    font: pygame.font.Font,
    title_font: pygame.font.Font,
    height: int,
    options_options: list[str],
    options_index: int,
    screen_dimensions: list[tuple[int, int]],
    dimension_index: int,
    theme_name: str,
    theme: Theme,
) -> None:
    title = title_font.render("Options", True, theme["title"])
    title_rect = title.get_rect(center=(height // 2, 100))
    screen.blit(title, title_rect)

    for i in range(len(options_options)):
        if i == 0:
            largeur, hauteur = screen_dimensions[dimension_index]
            texte = f"Dimensions: {largeur} x {hauteur}"
        elif i == 1:
            texte = f"Colors: {theme_name}"
        else:
            texte = options_options[i]
        color = theme["highlight"] if i == options_index else theme["text"]
        text = font.render(texte, True, color)
        text_rect = text.get_rect(center=(height // 2, 300 + i * 100))
        screen.blit(text, text_rect)
        if i == options_index:
            x = text_rect.left - 50
            y = text_rect.centery
            draw_cursor(screen, x, y, size=40)


def draw_highscores(
    screen: pygame.Surface,
    font: pygame.font.Font,
    title_font: pygame.font.Font,
    height: int,
    highscores: list[Highscore],
    theme: Theme,
) -> None:
    title = title_font.render("High Scores", True, theme["title"])
    title_rect = title.get_rect(center=(height // 2, 100))
    screen.blit(title, title_rect)

    header_y = 220
    rank_header = font.render("Rank", True, theme["title"])
    screen.blit(rank_header,
                rank_header.get_rect(center=(height // 4, header_y)))

    score_header = font.render("Name", True, theme["title"])
    screen.blit(score_header,
                score_header.get_rect(center=(height // 2, header_y)))

    name_header = font.render("Score", True, theme["title"])
    screen.blit(name_header,
                name_header.get_rect(center=(height // 1.3, header_y)))

    for i, entry in enumerate(highscores):
        pseudo = entry["pseudo"]
        score = entry["score"]
        y = 280 + i * 50
        color = theme["highlight"] if i == 0 else theme["text"]

        rank_text = font.render(ordinal(i + 1), True, color)
        rank_rect = rank_text.get_rect(center=(height // 4, y))
        screen.blit(rank_text, rank_rect)

        pseudo_text = font.render(pseudo, True, color)
        pseudo_rect = pseudo_text.get_rect(center=(height // 2, y))
        screen.blit(pseudo_text, pseudo_rect)

        score_text = font.render(str(score), True, color)
        score_rect = score_text.get_rect(center=(height // 1.3, y))
        screen.blit(score_text, score_rect)


def draw_cheat(
    screen: pygame.Surface,
    font: pygame.font.Font,
    title_font: pygame.font.Font,
    height: int,
    cheats: list[str],
    cheat_states: dict[str, bool],
    cheat_value: dict[str, int],
    cheat_index: int,
    editing_cheat: str | None,
    cheat_input_buffer: str,
    theme: Theme,
) -> None:
    title = title_font.render("Cheat", True, theme["title"])
    title_rect = title.get_rect(center=(height // 2, 100))
    screen.blit(title, title_rect)

    for i, cheat in enumerate(cheats):
        color: Rgb
        if cheat in cheat_states:
            status = "ON" if cheat_states[cheat] else "OFF"
            color = (theme["highlight"] if cheat_states[cheat]
                     else theme["text"])
            label = f"{cheat}: {status}"
        elif cheat == editing_cheat:
            color = theme["highlight"]
            label = f"{cheat} : [{cheat_input_buffer}]"
        else:
            color = theme["text"]
            label = f"{cheat} : < {cheat_value[cheat]} >"

        text = font.render(label, True, color)
        text_rect = text.get_rect(center=(height // 2, 250 + i * 100))
        screen.blit(text, text_rect)

        if i == cheat_index:
            x = text_rect.left - 50
            y = text_rect.centery
            draw_cursor(screen, x, y, size=40)


def draw_enter_name(
    screen: pygame.Surface,
    font: pygame.font.Font,
    title_font: pygame.font.Font,
    height: int,
    player_name: str,
    score: int,
) -> None:
    title = title_font.render("Game Over", True, (255, 0, 0))
    title_rect = title.get_rect(center=(height // 2, 150))
    screen.blit(title, title_rect)

    score_label = font.render("Your score is:", True, (255, 255, 255))
    score_value = font.render(str(score), True, (0, 255, 0))

    total_width = score_label.get_width() + 15 + score_value.get_width()
    start_x = (height - total_width) // 2

    scores_label_rect = score_label.get_rect(midleft=(start_x, 350))
    screen.blit(score_label, scores_label_rect)

    score_value_rect = score_value.get_rect(
        midleft=(scores_label_rect.right + 15, 350))
    screen.blit(score_value, score_value_rect)

    prompt = font.render("Enter your name:", True, (255, 255, 0))
    prompt_rect = prompt.get_rect(center=(height // 2, 500))
    screen.blit(prompt, prompt_rect)

    display_name = player_name if player_name else "_"
    name_surface = font.render(display_name, True, (0, 255, 0))
    name_rect = name_surface.get_rect(center=(height // 2, 550))
    screen.blit(name_surface, name_rect)


def draw_pause(
    screen: pygame.Surface,
    font: pygame.font.Font,
    title_font: pygame.font.Font,
    height: int,
    pause_options: list[str],
    pause_index: int,
) -> None:
    title = title_font.render("Pause", True, (255, 255, 0))
    title_rect = title.get_rect(center=(height // 2, 100))
    screen.blit(title, title_rect)

    for i, option in enumerate(pause_options):
        text = font.render(option, True, (255, 255, 255))
        text_rect = text.get_rect(center=(height // 2, 250 + i * 100))
        screen.blit(text, text_rect)
        if i == pause_index:
            x = text_rect.left - 50
            y = text_rect.centery
            draw_cursor(screen, x, y, size=40)
