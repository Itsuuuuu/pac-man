import os

import pygame

from src.characters import Color
from src.game_builder import build_game, build_level
from src.tile import Pacgum

from .draw import (
	draw_cheat,
	draw_enter_name,
	draw_highscores,
	draw_menu,
	draw_options,
	draw_pause,
)
from .draw_maze import draw_game_screen
from .utils import load_highscores, save_highscores


# Chemin absolu vers les polices (robuste, independant du cwd)
FONT_DIR = os.path.join(os.path.dirname(__file__), "font_pacman")

# Vitesses (delai entre deux deplacements d'une case, en ms) et duree d'invincibilite :
# desormais definies par niveau dans la config, lues via self.game.params.
# Plus la valeur est GRANDE, plus le personnage est LENT.

# Touches de direction -> vecteur de deplacement
KEY_DIRECTIONS = {
	pygame.K_UP: (0, -1),
	pygame.K_DOWN: (0, 1),
	pygame.K_LEFT: (-1, 0),
	pygame.K_RIGHT: (1, 0),
}

THEMES = [
	{"name": "Classic", "background": (0, 0, 0), "text": (255, 0, 0), "highlight": (0, 255, 0), "title": (255, 255, 0), "wall": (0, 0, 255)},
	{"name": "Ocean", "background": (5, 10, 40), "text": (100, 200, 255), "highlight": (0, 255, 200), "title": (200, 230, 255), "wall": (0, 255, 200)},
	{"name": "Sunset", "background": (40, 10, 20), "text": (255, 140, 60), "highlight": (255, 220, 80), "title": (255, 90, 90), "wall": (255, 140, 60)},
	{"name": "Mono", "background": (15, 15, 15), "text": (220, 220, 220), "highlight": (255, 255, 0), "title": (180, 180, 180), "wall": (150, 150, 150)},
]

# Maximum de charactere pour un pseudo
MAX_NAME_LENGTH = 10


CHEAT_REPEAT_MS = 120


class PacManApp:
	"""Application principale : gere le menu, les options, les scores et la boucle de jeu."""

	def __init__(self, config_path):
		self.config_path = config_path

		pygame.init()
		pygame.display.set_caption("Pac-Man")

		# Menus
		self.cheats = [
			"Invincibility", "Infinite lives", "Edible ghosts",
			"Level skips", "Point additions",
		]
		self.cheat_states = {
			"Invincibility": False,
			"Infinite lives": False,
			"Edible ghosts": False,
		}
		self.cheat_value = {"Level skips": 0, "Point additions": 0}
		self.cheat_max = {"Level skips": 42, "Point additions": 9999}

		self.options = ["Start Game", "Options", "High Scores", "Cheat", "Exit"]
		self.options_options = ["Dimensions", "Colors", "Back"]
		self.pause_options = ["Resume", "Restart", "Quit to Menu"]
		# 4 resolutions standards (le labyrinthe s'adapte automatiquement a la fenetre)
		self.screen_dimensions = [
			(1024, 768),    # XGA (4:3)
			(1280, 800),    # WXGA (16:10)
			(1600, 900),    # HD+ (16:9)
			(1920, 1080),   # Full HD (16:9)
		]

		self.dimension_index = 0
		self.menu_index = 0
		self.options_index = 0
		self.cheat_index = 0
		self.pause_index = 0


		self.screen = pygame.display.set_mode(self.screen_dimensions[self.dimension_index])
		# Reference de centrage horizontal des menus = largeur de la fenetre
		self.center_ref = self.screen_dimensions[self.dimension_index][0]

		self.title_font = pygame.font.Font(os.path.join(FONT_DIR, "Pacfont-ZEBZ.ttf"), 90)
		self.font = pygame.font.SysFont("Rockwell Nova", 50, bold=True)
		self.hud_font = pygame.font.SysFont("Rockwell Nova", 28, bold=True)

		self.highscores = load_highscores("highscore.json")
		self.clock = pygame.time.Clock()

		self.state = "menu"
		self.running = True

		# Etat de la partie en cours
		self.game = None
		self.direction = (0, 0)
		# Buffer de touches : stocke la prochaine commande (1 maximum)
		self.input_buffer = []
		# Timers de deplacement separes : pacman et fantomes avancent a leur propre rythme
		self.pacman_timer = 0
		self.ghost_timer = 0
		self.invincible_timer = 0
		self.cheat_repeat_timer = 0
		self.game_started = False

		self.player_name = ""

		self.editing_cheat = None
		self.cheat_input_buffer = 0

		self.current_level = 1
		self.level_timer_ms = 0

		self.theme_index = 0

	# ------------------------------------------------------------------ #
	# Gestion des entrees
	# ------------------------------------------------------------------ #

	def handle_pause_events(self, event):
		if event.key == pygame.K_UP:
			if self.pause_index > 0:
				self.pause_index -= 1
		elif event.key == pygame.K_DOWN:
			if self.pause_index != len(self.pause_options) - 1:
				self.pause_index += 1
		elif event.key == pygame.K_RETURN:
			if self.pause_index == 0:
				self.state = "game"
			if self.pause_index == 1:
				self.start_game()
			elif self.pause_index == 2:
				self.state = "menu"

	def handle_menu_events(self, event):
		if event.key == pygame.K_UP:
			if self.menu_index > 0:
				self.menu_index -= 1
		elif event.key == pygame.K_DOWN:
			if self.menu_index != len(self.options) - 1:
				self.menu_index += 1
		elif event.key == pygame.K_RETURN:
			if self.menu_index == 0:
				self.start_game()
			elif self.menu_index == 1:
				self.state = "options"
			elif self.menu_index == 2:
				self.state = "highscores"
			elif self.menu_index == 3:
				self.state = "cheat"
			elif self.menu_index == 4:
				self.running = False

	def handle_options_events(self, event):
		if event.key == pygame.K_UP:
			if self.options_index > 0:
				self.options_index -= 1
		elif event.key == pygame.K_DOWN:
			if self.options_index != len(self.options_options) - 1:
				self.options_index += 1
		elif event.key == pygame.K_RETURN:
			if self.options_index == 0:
				self.dimension_index = (self.dimension_index + 1) % len(self.screen_dimensions)
				self.screen = pygame.display.set_mode(self.screen_dimensions[self.dimension_index])
				self.center_ref = self.screen_dimensions[self.dimension_index][0]
			elif self.options_index == 1:
				self.theme_index = (self.theme_index + 1) % len(THEMES)
			elif self.options_index == 2:
				self.state = "menu"

	def handle_cheat_events(self, event):
		current_cheat = self.cheats[self.cheat_index]

		if self.editing_cheat is not None:
			self.handle_cheat_input_event(event)
			return

		if event.key == pygame.K_UP:
			if self.cheat_index > 0:
				self.cheat_index -= 1
		elif event.key == pygame.K_DOWN:
			if self.cheat_index != len(self.cheats) - 1:
				self.cheat_index += 1
		elif event.key == pygame.K_RETURN:
			if current_cheat in self.cheat_states:
				self.cheat_states[current_cheat] = not self.cheat_states[current_cheat]
			elif current_cheat == "Point additions":
				self.editing_cheat = current_cheat
				self.cheat_input_buffer = str(self.cheat_value[current_cheat])

	def handle_cheat_input_event(self, event):
		if event.key == pygame.K_RETURN:
			value = int(self.cheat_input_buffer) if self.cheat_input_buffer else 0
			value = min(value, self.cheat_max[self.editing_cheat])
			self.cheat_value[self.editing_cheat] = value
			self.editing_cheat = None
			self.cheat_input_buffer = ""
		elif event.key == pygame.K_ESCAPE:
			self.editing_cheat = None
			self.cheat_input_buffer = ""
		elif event.key == pygame.K_BACKSPACE:
			self.cheat_input_buffer = self.cheat_input_buffer[:-1]
		elif event.unicode.isdigit():
			max_digits = len(str(self.cheat_max[self.editing_cheat]))
			if len(self.cheat_input_buffer) < max_digits:
				self.cheat_input_buffer += event.unicode

	def update_cheat(self, dt):
		"""Permet de maintenir DROITE/GAUCHE pour faire defiler une valeur en continu."""
		self.cheat_repeat_timer += dt

		if self.editing_cheat is not None:
			return

		if self.cheat_repeat_timer < CHEAT_REPEAT_MS:
			return
		self.cheat_repeat_timer = 0

		current_cheat = self.cheats[self.cheat_index]
		if current_cheat not in self.cheat_value:
			return

		keys = pygame.key.get_pressed()
		if keys[pygame.K_RIGHT]:
			if self.cheat_value[current_cheat] < self.cheat_max[current_cheat]:
				self.cheat_value[current_cheat] += 1
		elif keys[pygame.K_LEFT]:
			if self.cheat_value[current_cheat] > 0:
				self.cheat_value[current_cheat] -= 1

	def handle_game_events(self, event):
		key_dir = KEY_DIRECTIONS.get(event.key)
		if key_dir is None:
			return

		self.game_started = True

		pacman = self.game.pacman
		if pacman.can_move(key_dir[0], key_dir[1], self.game.tile_map):
			# Virage possible tout de suite -> on l'applique sans attendre (pacman part / avance)
			self.direction = key_dir
			self.input_buffer.clear()
		else:
			# Sinon pacman continue tout droit et on garde la commande en buffer (1 max),
			# elle s'appliquera au prochain pas ou le passage s'ouvre.
			self.input_buffer.clear()
			self.input_buffer.append(key_dir)

	def handle_enter_name_events(self, event):
		if event.key == pygame.K_RETURN:
			pseudo = self.player_name.strip() or "PLAYER"
			save_highscores("highscore.json", pseudo, self.game.current_score)
			self.highscores = load_highscores("highscore.json")
			self.player_name = ""
			self.state = "menu"
		elif event.key == pygame.K_BACKSPACE:
			self.player_name = self.player_name[:-1]
		elif event.unicode.isalnum() and len(self.player_name) < MAX_NAME_LENGTH:
			self.player_name += event.unicode


	def process_events(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False
				continue

			if event.type != pygame.KEYDOWN:
				continue

			if event.key == pygame.K_ESCAPE:
				if self.state == "cheat" and self.editing_cheat is not None:
					self.editing_cheat = None
					self.cheat_input_buffer = ""
					continue
				if self.state == "menu":
					self.running = False
				elif self.state == "game":
					self.state = "pause"
				elif self.state == "pause":
					self.state = "game"
				else:
					self.state = "menu"
				continue

			if self.state == "menu":
				self.handle_menu_events(event)
			elif self.state == "options":
				self.handle_options_events(event)
			elif self.state == "cheat":
				self.handle_cheat_events(event)
			elif self.state == "game":
				self.handle_game_events(event)
			elif self.state == "pause":
				self.handle_pause_events(event)
			elif self.state == "enter_name":
				self.handle_enter_name_events(event)

	# ------------------------------------------------------------------ #
	# Logique de jeu
	# ------------------------------------------------------------------ #
	def reset_level_state(self):
		"""Remet a zero le pilotage d'un niveau : direction, buffer, timers, chrono."""
		self.direction = (0, 0)
		self.input_buffer.clear()
		self.pacman_timer = 0
		self.ghost_timer = 0
		self.invincible_timer = 0
		self.game_started = False
		self.level_timer_ms = self.game.params.level_max_time * 1000

	def start_game(self):
		self.current_level = 1
		self.game = build_game(self.config_path)
		self.reset_level_state()
		if self.cheat_states["Invincibility"]:
			self.game.pacman.invincible = True
			self.invincible_timer = self.game.params.invincible_ms
		if self.cheat_value["Point additions"]:
			self.game.current_score += self.cheat_value["Point additions"]
		self.state = "game"

	def find_blinky(self):
		for ghost in self.game.ghosts:
			if ghost.color == Color.RED:
				return ghost
		return None

	def ghost_interval(self):
		"""Delai courant entre deux deplacements de fantome (plus lent s'ils fuient)."""
		if self.game.pacman.invincible:
			return self.game.params.ghost_frightened_move_ms
		return self.game.params.ghost_move_ms

	def move_progress(self):
		"""Avancement (0..1) de pacman et des fantomes entre leur case precedente et
		la courante. Sert uniquement a l'affichage, qui interpole pour rester fluide
		alors que la logique n'avance que d'une case toutes les quelques dizaines de frames.
		"""
		pacman = min(1.0, self.pacman_timer / self.game.params.pacman_move_ms)
		ghosts = min(1.0, self.ghost_timer / self.ghost_interval())
		return pacman, ghosts

	def step_pacman(self):
		"""Fait avancer pacman d'une case : direction, deplacement, ramassage, collisions."""
		game = self.game
		pacman = game.pacman

		# Buffer de touches : on tente d'appliquer la commande en attente.
		# Si le virage est possible, elle devient la direction courante et est retiree ;
		# sinon pacman continue tout droit et la commande reste en attente.
		if self.input_buffer:
			next_dir = self.input_buffer[0]
			if pacman.can_move(next_dir[0], next_dir[1], game.tile_map):
				self.direction = next_dir
				self.input_buffer.pop(0)

		pacman.move_to_next(self.direction[0], self.direction[1], game.tile_map)

		# Ramassage des pacgums
		tile = game.tile_map[pacman.y][pacman.x]
		if tile.content == Pacgum.PACGUM:
			game.current_score += game.config.points_per_pacgum
			tile.content = Pacgum.NOTHING
			game.pacgum -= 1
		elif tile.content == Pacgum.SUPERPACGUM:
			game.current_score += game.config.points_per_super_pacgum
			tile.content = Pacgum.NOTHING
			# invincible_ms a 0 : plus de mode fright a ce niveau, les points seulement
			if game.params.invincible_ms > 0:
				pacman.invincible = True
				self.invincible_timer = game.params.invincible_ms

		# Collisions : pacman a pu entrer dans un fantome
		self.resolve_collisions()

		# Niveau termine : plus aucun pacgum
		if game.pacgum <= 0:
			self.next_level()

	def next_level(self):
		"""Passe au niveau suivant en conservant score et vies."""
		self.current_level += 1
		self.game = build_level(
			self.game.config,
			self.current_level,
			self.game.current_score,
			self.game.current_lives,
		)
		self.reset_level_state()

	def step_ghosts(self):
		"""Fait avancer tous les fantomes d'une case, puis verifie les collisions."""
		if not self.game_started:
			return
		game = self.game
		blinky = self.find_blinky()
		for ghost in game.ghosts:
			ghost.move(game.tile_map, game.width, game.height, game.pacman, blinky)

		# Collisions : un fantome a pu entrer dans pacman
		self.resolve_collisions()

	def resolve_collisions(self):
		game = self.game
		pacman = game.pacman
		for ghost in game.ghosts:
			if ghost.x != pacman.x or ghost.y != pacman.y or ghost.is_dead:
				continue
			if pacman.invincible or self.cheat_states["Edible ghosts"]:
				ghost.back_to_spawn()
				game.current_score += game.config.points_per_ghost
			else:
				self.lose_life()
				return

	def lose_life(self):
		game = self.game
		if not self.cheat_states["Infinite lives"]:
			game.current_lives -= 1
		game.pacman.back_to_spawn()
		for ghost in game.ghosts:
			ghost.respawn()
		self.direction = (0, 0)
		self.input_buffer.clear()
		# Repart d'un rythme propre pour ne pas se refaire toucher instantanement
		self.pacman_timer = 0
		self.ghost_timer = 0
		if game.current_lives <= 0:
			self.end_game(won=False)


	def end_game(self, won):
		self.game.is_finished = True
		if not won:
			self.state = "enter_name"
		else:
			self.state = "menu"
		self.menu_index = 0

	def update_game(self, dt):
		if self.invincible_timer > 0:
			self.invincible_timer -= dt
			if self.invincible_timer <= 0 and not self.cheat_states["Invincibility"]:
				self.game.pacman.invincible = False

		if self.game_started:
			self.level_timer_ms -= dt
			if self.level_timer_ms <= 0:
				self.level_timer_ms = self.game.params.level_max_time * 1000
				self.lose_life()
				return

		# Chaque entite avance a son propre rythme
		pacman_interval = self.game.params.pacman_move_ms
		self.pacman_timer += dt
		while self.pacman_timer >= pacman_interval and self.state == "game":
			self.pacman_timer -= pacman_interval
			self.step_pacman()

		self.ghost_timer += dt
		while self.ghost_timer >= self.ghost_interval() and self.state == "game":
			self.ghost_timer -= self.ghost_interval()
			self.step_ghosts()

	# ------------------------------------------------------------------ #
	# Rendu
	# ------------------------------------------------------------------ #
	def render(self):
		theme = THEMES[self.theme_index]
		self.screen.fill(theme["background"])

		if self.state == "menu":
			draw_menu(self.screen, self.font, self.title_font, self.center_ref, self.options, self.menu_index, theme)
		elif self.state == "game":
			seconds_remaining = max(0, self.level_timer_ms) // 1000
			pacman_progress, ghost_progress = self.move_progress()
			draw_game_screen(
				self.screen, self.game, self.hud_font, self.current_level, seconds_remaining, theme,
				pacman_progress, ghost_progress,
			)
		elif self.state == "highscores":
			draw_highscores(self.screen, self.font, self.title_font, self.center_ref, self.highscores[:10], theme)
		elif self.state == "options":
			draw_options(
				screen=self.screen,
				font=self.font,
				title_font=self.title_font,
				height=self.center_ref,
				options_options=self.options_options,
				options_index=self.options_index,
				screen_dimensions=self.screen_dimensions,
				dimension_index=self.dimension_index,
				theme_name=theme["name"],
				theme=theme
			)
		elif self.state == "pause":
			draw_pause(
				self.screen, self.font, self.title_font, self.center_ref,
				self.pause_options, self.pause_index
			)
		elif self.state == "cheat":
			draw_cheat(
				self.screen, self.font, self.title_font, self.center_ref,
				self.cheats, self.cheat_states, self.cheat_value, self.cheat_index,
				self.editing_cheat, self.cheat_input_buffer, theme
			)
		elif self.state == "enter_name":
			draw_enter_name(
				self.screen, self.font, self.title_font, self.center_ref, self.player_name, self.game.current_score
			)

		pygame.display.flip()

	# ------------------------------------------------------------------ #
	# Boucle principale
	# ------------------------------------------------------------------ #
	def run(self):
		pygame.mixer.music.load("./Assets/sound/start.wav")
		pygame.mixer.music.play()
		while self.running:
			dt = self.clock.tick(60)
			self.process_events()
			if self.state == "game" and self.game is not None:
				self.update_game(dt)
			elif self.state == "cheat":
				self.update_cheat(dt)
			self.render()

		pygame.quit()
