import os

import pygame

from src.game_builder import build_game
from src.tile import Pacgum
from src.characters import Color
from .utils import load_highscores, save_highscores
from .draw import draw_menu, draw_highscores, draw_options, draw_cheat, draw_enter_name
from .draw_maze import draw_game_screen


# Chemin absolu vers les polices (robuste, independant du cwd)
FONT_DIR = os.path.join(os.path.dirname(__file__), "font_pacman")

# Duree d'invincibilite apres un super pacgum (ms)
INVINCIBLE_MS = 6000

# Vitesses : delai entre deux deplacements d'une case (ms).
# Plus la valeur est GRANDE, plus le personnage est LENT.
PACMAN_MOVE_MS = 200
GHOST_MOVE_MS = 260
# Les fantomes ralentissent encore quand pacman est invincible (ils fuient)
GHOST_FRIGHTENED_MOVE_MS = 380

# Touches de direction -> vecteur de deplacement
KEY_DIRECTIONS = {
	pygame.K_UP: (0, -1),
	pygame.K_DOWN: (0, 1),
	pygame.K_LEFT: (-1, 0),
	pygame.K_RIGHT: (1, 0),
}

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
		self.options_options = ["Volume", "Dimensions", "Colors", "Back"]
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

	# ------------------------------------------------------------------ #
	# Gestion des entrees
	# ------------------------------------------------------------------ #
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
			if self.options_index == 1:
				self.dimension_index = (self.dimension_index + 1) % len(self.screen_dimensions)
				self.screen = pygame.display.set_mode(self.screen_dimensions[self.dimension_index])
				self.center_ref = self.screen_dimensions[self.dimension_index][0]
			elif self.options_index == 3:
				self.state = "menu"

	def handle_cheat_events(self, event):
		current_cheat = self.cheats[self.cheat_index]

		if event.key == pygame.K_UP:
			if self.cheat_index > 0:
				self.cheat_index -= 1
		elif event.key == pygame.K_DOWN:
			if self.cheat_index != len(self.cheats) - 1:
				self.cheat_index += 1
		elif event.key == pygame.K_RETURN:
			if current_cheat in self.cheat_states:
				self.cheat_states[current_cheat] = not self.cheat_states[current_cheat]

	def update_cheat(self, dt):
		"""Permet de maintenir DROITE/GAUCHE pour faire defiler une valeur en continu."""
		self.cheat_repeat_timer += dt
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
				if self.state == "menu":
					self.running = False
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
			elif self.state == "enter_name":
				self.handle_enter_name_events(event)

	# ------------------------------------------------------------------ #
	# Logique de jeu
	# ------------------------------------------------------------------ #
	def start_game(self):
		self.game = build_game(self.config_path)
		self.direction = (0, 0)
		self.input_buffer.clear()
		self.pacman_timer = 0
		self.ghost_timer = 0
		self.invincible_timer = 0
		self.game_started = False
		if self.cheat_states["Invincibility"]:
			self.game.pacman.invincible = True
			self.invincible_timer = INVINCIBLE_MS
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
			return GHOST_FRIGHTENED_MOVE_MS
		return GHOST_MOVE_MS

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
			pacman.invincible = True
			self.invincible_timer = INVINCIBLE_MS

		# Collisions : pacman a pu entrer dans un fantome
		self.resolve_collisions()

		# Victoire : plus aucun pacgum
		if game.pacgum <= 0:
			self.end_game(won=True)

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
			ghost.x = ghost.spawn_x
			ghost.y = ghost.spawn_y
			ghost.is_dead = False
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

		# Chaque entite avance a son propre rythme
		self.pacman_timer += dt
		while self.pacman_timer >= PACMAN_MOVE_MS and self.state == "game":
			self.pacman_timer -= PACMAN_MOVE_MS
			self.step_pacman()

		self.ghost_timer += dt
		while self.ghost_timer >= self.ghost_interval() and self.state == "game":
			self.ghost_timer -= self.ghost_interval()
			self.step_ghosts()

	# ------------------------------------------------------------------ #
	# Rendu
	# ------------------------------------------------------------------ #
	def render(self):
		self.screen.fill((0, 0, 0))

		if self.state == "menu":
			draw_menu(self.screen, self.font, self.title_font, self.center_ref, self.options, self.menu_index)
		elif self.state == "game":
			draw_game_screen(self.screen, self.game, self.hud_font)
		elif self.state == "highscores":
			draw_highscores(self.screen, self.font, self.title_font, self.center_ref, self.highscores[:10])
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
			)
		elif self.state == "cheat":
			draw_cheat(
				self.screen, self.font, self.title_font, self.center_ref,
				self.cheats, self.cheat_states, self.cheat_value, self.cheat_index,
			)
		elif self.state == "enter_name":
			draw_enter_name(self.screen, self.font, self.title_font, self.center_ref, self.player_name)

		pygame.display.flip()

	# ------------------------------------------------------------------ #
	# Boucle principale
	# ------------------------------------------------------------------ #
	def run(self):
		while self.running:
			dt = self.clock.tick(60)
			self.process_events()
			if self.state == "game" and self.game is not None:
				self.update_game(dt)
			elif self.state == "cheat":
				self.update_cheat(dt)
			self.render()

		pygame.quit()
