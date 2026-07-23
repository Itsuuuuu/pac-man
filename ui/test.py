import pygame
import json
import sys

from .utils import load_highscores
from .draw import draw_menu, draw_highscores, draw_options, draw_cheat, draw_game
from .draw_maze import draw_game_screen, build_game



pygame.init()

pygame.display.set_caption("Pac-Man")
cheats = ["Invincibility", "Infinite lives", "Edible ghosts", "Level skips", "Point additions"]
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

dimension_index = 0
menu_index = 0
options_index = 0
cheat_index = 0

options = ["Start Game", "Options", "High Scores", "Cheat", "Exit"]
options_options = ["Volume", "Dimensions", "Colors", "Back"]
screen_dimensions = [(2000, 1000), (2500, 1400), (1000, 1000)]


highscores = load_highscores("hightscore.json")

height, width = screen_dimensions[dimension_index]
screen = pygame.display.set_mode(screen_dimensions[dimension_index])

title_font = pygame.font.Font("ui/font_pacman/Pacfont-ZEBZ.ttf", 90)
# start = pygame.font.SysFont("Rockwell Nova", 50, bold=True)
font = pygame.font.SysFont("Rockwell Nova", 50, bold=True)


running = True
state = "menu"




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

if len(sys.argv) < 2:
    print("Error usage: python3 test.py config.json", file=sys.stderr)
    sys.exit(1)

game = build_game(sys.argv[1])


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
        draw_menu(screen, font, title_font, height, options, menu_index)
    elif state == "game":
        draw_game_screen(screen, game)
    elif state == "highscores":
        draw_highscores(screen, font, title_font, height, highscores)
    elif state == "options":
        draw_options(
        screen=screen,
        font=font,
        title_font=title_font,
        height=height,
        options_options=options_options,
        options_index=options_index,
        screen_dimensions=screen_dimensions,
        dimension_index=dimension_index
                 )
    elif state == "cheat":
        draw_cheat(screen, font, title_font, height, cheats, cheat_states, cheat_value, cheat_index)

    pygame.display.flip()


pygame.quit()
quit()
