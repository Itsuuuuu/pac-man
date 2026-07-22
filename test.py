import pygame
import math
import json

pygame.init()

pygame.display.set_caption("Pac-Man")
screen_dimensions = [(2000, 1000), (2500, 1400), (1000, 1000)]
dimension_index = 0
height, width = screen_dimensions[dimension_index]
screen = pygame.display.set_mode(screen_dimensions[dimension_index])

title_font = pygame.font.Font("font_pacman/Pacfont-ZEBZ.ttf", 90)
# start = pygame.font.SysFont("Rockwell Nova", 50, bold=True)
font = pygame.font.SysFont("Rockwell Nova", 50, bold=True)

options = ["Start Game", "Options", "High Scores", "Cheat", "Exit"]
options_options = ["Volume", "Dimensions", "Colors", "Back"]
cheats = ["Invincibility", "Level skips", "Infinite lives", "Edible ghosts", "Point additions"]
cheat_states = {
    "Invincibility": False,
    "Infinite lives": False,
    "Edible ghosts": False,
    }

cheat_value = {
    "Level skips": 0,
    "Point additions": 0,
}

cheat_max = {
    "Level skips": 42,
    "Point additions": 9999,
}

menu_index = 0
options_index = 0
cheat_index = 0

running = True
state = "menu"

def load_highscores(filepath):
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        return []
    
    return sorted(data, key=lambda entry: entry["score"], reverse=True)

def ordinal(n):
    if 11 <= n % 100 <= 13:
        suffix = "TH"
    else:
        suffix = {1: "ST", 2: "ND", 3: "RD"}.get(n % 10, "TH")
    return f"{n}{suffix}"

highscores = load_highscores("hightscore.json")


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


def draw_menu(screen, menu_index):
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


def draw_game(screen):
    title = title_font.render("Game", True, (255, 255, 0))
    title_rect = title.get_rect(center=(height // 2, 100))  #
    screen.blit(title, title_rect)


def draw_options(screen, options_index):
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
        text = font.render(texte, True, (255, 0, 0))
        text_rect = text.get_rect(center=(height // 2, 300 + i * 100))
        screen.blit(text, text_rect)
        if i == options_index:
            circle = 15
            x = text_rect.left - 50
            y = text_rect.centery
            draw_pacman(screen, x, y, circle, mouth_angle=20)


def draw_highscores(screen):
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




def draw_cheat(screen, cheat_index):
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


def handle_cheat_events(event):
    global cheat_index, state, running

    current_cheat = cheats[cheat_index]


    if event.key == pygame.K_UP:
        if cheat_index > 0:
            cheat_index -= 1
    elif event.key == pygame.K_DOWN:
        if cheat_index != len(cheats) - 1:
            cheat_index += 1
    elif event.key == pygame.K_RETURN:
        if current_cheat in cheat_states:
            cheat_states[current_cheat] = not cheat_states[current_cheat]
    elif event.key == pygame.K_RIGHT:
        if current_cheat in cheat_value:
            if cheat_value[current_cheat] < cheat_max[current_cheat]:
                cheat_value[current_cheat] += 1
    elif event.key == pygame.K_LEFT:
        if current_cheat in cheat_value:
            if cheat_value[current_cheat] > 0:
                cheat_value[current_cheat] -= 1


        

def handle_menu_events(event):
    global menu_index, state, running

    if event.key == pygame.K_UP:
        if menu_index > 0:
            menu_index -= 1
    elif event.key == pygame.K_DOWN:
        if menu_index != len(options) - 1:
            menu_index += 1
    elif event.key == pygame.K_RETURN:
        if menu_index == 0:
            state = "game"
        elif menu_index == 1:
            state = "options"
        elif menu_index == 2:
            state = "highscores"
        elif menu_index == 3:
            state = "cheat"
        elif menu_index == 4:
            running = False
    elif event.key == pygame.K_ESCAPE:
        running = False

def handle_options_events(event):  ##
    global options_index, state, running, dimension_index, height, width, screen

    if event.key == pygame.K_UP:
        if options_index > 0:
            options_index -= 1
    elif event.key == pygame.K_DOWN:
        if options_index != len(options_options) - 1:
            options_index += 1
    elif event.key == pygame.K_RETURN:
        if options_index == 0:
            print("Volume option selected")
        elif options_index == 1:
            dimension_index = (dimension_index + 1) % len(screen_dimensions)
            height, width = screen_dimensions[dimension_index]
            screen = pygame.display.set_mode(screen_dimensions[dimension_index])
        elif options_index == 2:
            print("Colors option selected")
        elif options_index == 3:
            state = "menu"
    elif event.key == pygame.K_ESCAPE:
        running = False


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if state == "menu":
                    running = False
                else:
                    state = "menu"
            elif state == "menu":
                handle_menu_events(event)
            elif state == "cheat":
                handle_cheat_events(event)
            elif state == "options":
                handle_options_events(event)

    screen.fill((0, 0, 0))

    if state == "menu":
        draw_menu(screen, menu_index)
    elif state == "highscores":
        draw_highscores(screen)
    elif state == "options":
        draw_options(screen, options_index)
    elif state == "cheat":
        draw_cheat(screen, cheat_index)
    elif state == "game":
        draw_game(screen)

    pygame.display.flip()


pygame.quit()
quit()
