# Pac-Man — documentation technique

Clone de Pac-Man en Python / pygame, avec labyrinthe généré procéduralement,
4 fantômes aux comportements distincts, niveaux à difficulté croissante,
thèmes de couleurs et menu de triche.

```bash
make install    # uv sync
make run        # uv run python -m src config.json
make lint       # flake8 + mypy
make lint-strict # flake8 + mypy --strict
```

## Sommaire

- [Structure du projet](#structure-du-projet)
- [L'algorithme des fantômes](#lalgorithme-des-fantômes)
- [La partie GUI](#la-partie-gui)
- [Configuration](#configuration)
- [Points connus et pistes d'amélioration](#points-connus-et-pistes-damélioration)

---

## Structure du projet

```
src/
├── __main__.py       point d'entrée (python -m src config.json)
├── config_parser.py  schéma Pydantic de config.json
├── game_builder.py   chargement config + construction d'un niveau
├── game_setting.py   état d'un niveau (map, pacgums, spawns)
├── tile.py           une case du labyrinthe (murs, contenu)
├── characters.py     Pacman, Ghost et les cibles de chaque fantôme
├── ghost_algo.py     BFS de pathfinding (le seul algo de déplacement)
└── ui/
    ├── app.py        machine à états, boucle principale, entrées
    ├── draw.py       écrans de menu (texte)
    ├── draw_maze.py  écran de jeu (labyrinthe, entités, sidebar)
    ├── assets.py     chargement et cache des sprites
    └── utils.py      types partagés (Theme, Rgb) + highscores JSON
```

Le sens des dépendances est strict : `ui/` connaît le moteur, jamais l'inverse.
`ghost_algo.py` ne dépend que de `tile.py`, ce qui le rend testable isolément.

---

## L'algorithme des fantômes

### Représentation du labyrinthe

Les murs sont encodés en **bitmask** par case : `N=1, E=2, S=4, W=8`. `DELTAS`
associe chaque bit à un vecteur `(dx, dy)`. Une case avec `walls_value = 15` est
totalement fermée (case réservée, hors du labyrinthe jouable).

Deux adaptateurs produisent la fonction `has_wall(x, y, direction)` que
l'algorithme consomme — c'est ce qui le rend indépendant du reste du jeu :

| Fonction | Source |
|---|---|
| `wall_from_grid(maze_grid)` | grille brute du `MazeGenerator` |
| `wall_from_tiles(tile_map)` | objets `Tile` du jeu (celui utilisé en pratique) |

### Le parcours en largeur

Il n'y a **qu'un seul algorithme de pathfinding**, un BFS
([ghost_algo.py:18](src/ghost_algo.py#L18)) :

1. File `deque` initialisée avec `start`, dict `came_from` qui sert à la fois de
   marqueur « visité » et de chaîne de parents.
2. Pour chaque case dépilée, on teste les 4 directions ; on ignore celles
   bloquées par un mur, hors bornes, ou déjà visitées.
3. Dès que `goal` est atteint on **s'arrête immédiatement** (pas d'exploration
   complète) et on remonte la chaîne de parents.

Le BFS garantit le plus court chemin en nombre de cases, le graphe n'étant pas
pondéré. Complexité `O(W×H)` au pire, exécuté **une fois par fantôme et par pas
de déplacement**.

Deux variantes partagent le même corps :

- `bfs_next_step` → `_first_step` remonte les parents jusqu'au nœud dont le
  parent est `start` : retourne **une seule case**, celle où avancer. C'est
  celle utilisée en jeu.
- `bfs_path` → `_rebuild_path` retourne la **liste complète** des cases. Utile
  pour du debug ou une visualisation, actuellement non appelée.

Cas limites : `start == goal` renvoie `start` / `[start]` ; une cible
inatteignable renvoie `None`, et le fantôme ne bouge pas ce tour-ci.

### Les personnalités

Le point clé du design : **l'algorithme est unique, seule la cible change**.
Toute l'IA se joue dans `Ghost.get_target()`
([characters.py:152](src/characters.py#L152)).

| Fantôme | Couleur | Cible | Comportement |
|---|---|---|---|
| Blinky | `RED` | `(pacman.x, pacman.y)` | poursuite directe |
| Pinky | `PINK` | pacman + `4 × direction`, clampé | embuscade devant |
| Inky | `BLUE` | `2 × (pacman + 2×dir) − blinky` | vecteur doublé depuis Blinky |
| Clyde | `ORANGE` | case aléatoire | erratique |

Deux surcouches sont prioritaires sur la personnalité :

- **Mort** (`is_dead`) → la cible devient son spawn. Le fantôme traverse le
  labyrinthe sous forme d'yeux, et `move()` remet `is_dead = False` à l'arrivée
  ([characters.py:201](src/characters.py#L201)).
- **Frightened** (pacman invincible) → `get_frightened_target()` tire une case
  au hasard et **la mémorise** dans `self.frightened_target` jusqu'à ce qu'elle
  soit atteinte. C'est ce qui évite que le fantôme tremble sur place. Le champ
  est remis à `None` dès que la peur cesse.

`block()` clampe les coordonnées dans la grille : une cible hors map rendrait
le BFS infructueux.

`move()` sauvegarde `prev_x` / `prev_y` **avant** le pas — cette paire ne sert
qu'à l'interpolation d'affichage.

---

## La partie GUI

Quatre modules, tous pilotés par **pygame**.

### `app.py` — la classe `PacManApp`

#### Machine à états

`self.state` ∈ `menu | options | highscores | cheat | game | pause | enter_name`.
Chaque état a son handler d'événements et sa branche de rendu. `ESCAPE` remonte
d'un cran : jeu → pause, sous-écran → menu, menu → quitter.

#### Boucle principale

[app.py:669](src/ui/app.py#L669) :

```
dt = clock.tick(60) → process_events() → update_game(dt) → render()
```

Un `prev_state` détecte la sortie de l'état `game` pour couper le son de
lancement.

#### Découplage logique / affichage

La logique du jeu est **strictement sur grille entière**, mais la boucle tourne
à 60 FPS. Deux mécanismes réconcilient les deux.

**Timers à accumulateur** ([app.py:581](src/ui/app.py#L581)) — pacman et
fantômes ont chacun leur horloge :

```python
self.pacman_timer += dt
while self.pacman_timer >= pacman_interval and self.state == "game":
    self.pacman_timer -= pacman_interval
    self.step_pacman()
```

Le `while` (et non `if`) rattrape les frames perdues ; le `-=` (et non `= 0`)
évite la dérive. Les intervalles viennent de la config par niveau
(`pacman_move_ms`, `ghost_move_ms`, `ghost_frightened_move_ms`) — **plus la
valeur est grande, plus le personnage est lent**. `ghost_interval()` bascule sur
l'intervalle « frightened » quand pacman est invincible, ce qui ralentit les
fantômes en fuite.

**Interpolation** — `move_progress()` retourne un ratio 0→1
(`timer / intervalle`), transmis au rendu. `entity_pixels()`
([draw_maze.py:93](src/ui/draw_maze.py#L93)) fait un lerp entre
`(prev_x, prev_y)` et `(x, y)`. C'est pourquoi `back_to_spawn()` et `respawn()`
recopient aussi `prev_*` : sinon le sprite glisserait à travers tout le
labyrinthe jusqu'au spawn.

#### Buffer d'entrées

[app.py:316](src/ui/app.py#L316) — comportement du Pac-Man original : à l'appui
d'une touche, si le virage est possible **immédiatement**, il est appliqué et le
buffer vidé. Sinon la commande est stockée (**1 seule au maximum**) et retentée
à chaque `step_pacman()` — pacman continue tout droit en attendant que le
passage s'ouvre.

#### Progression et scoring

- `step_pacman()` : applique le buffer → déplace → ramasse le pacgum →
  décrémente `game.pacgum` → collisions → si `pacgum <= 0`, `next_level()`.
- Un super pacgum ne déclenche l'invincibilité que si `invincible_ms > 0`.
  À 0, il ne rapporte que des points : c'est un réglage de difficulté par niveau.
- `next_level()` reconstruit un labyrinthe neuf via `build_level()` en
  **conservant score et vies** ; la graine dérive du numéro de niveau, donc
  chaque niveau a son propre labyrinthe reproductible.
- `resolve_collisions()` est appelée **deux fois par tour** (après le pas de
  pacman *et* après celui des fantômes) : sans ça, un croisement pourrait passer
  inaperçu.
- Timer de niveau : `level_max_time` est décompté ; à zéro, `lose_life()`.
- `lose_life()` remet pacman et tous les fantômes au spawn et **remet les timers
  à zéro**, pour ne pas se faire retoucher instantanément.

#### L'invariant « une partie est en cours »

`self._game` vaut `None` tant que `start_game()` n'a pas été appelé. L'accès
passe par une propriété qui porte l'invariant une fois pour toutes
([app.py:173](src/ui/app.py#L173)) :

```python
@property
def game(self) -> GameSetting:
    assert self._game is not None, "aucune partie en cours"
    return self._game
```

Tout le code de jeu écrit `self.game.pacman` sans se poser la question.
`has_game()` sert au seul endroit qui doit vraiment tester l'absence de partie :
le garde-fou de la boucle principale.

#### Cheats

Cinq entrées : trois booléens (`Invincibility`, `Infinite lives`,
`Edible ghosts`) et deux valeurs numériques. `update_cheat()` gère la
**répétition de touche** (maintenir ←/→ fait défiler toutes les 120 ms) et
`handle_cheat_input_event()` une saisie numérique au clavier, avec limite de
chiffres.

#### Thèmes et résolutions

Quatre thèmes (`Classic`, `Ocean`, `Sunset`, `Mono`) définis comme des
`Theme` (`TypedDict`), cyclés depuis le menu Options. Quatre résolutions de
1024×768 à 1920×1080 ; le labyrinthe s'adapte tout seul, voir `compute_layout`.

#### Souris

`draw_menu()` **retourne les rects** de ses options, stockés dans
`self.menu_item_rects`. `MOUSEMOTION` met à jour `menu_index` au survol,
`MOUSEBUTTONDOWN` rejoue l'action clavier correspondante. Uniquement sur le
menu principal : les autres écrans restent au clavier.

#### Son

`start.wav` est chargé au démarrage dans un `try / except` — le jeu ne plante
pas si le fichier manque. Il est joué dans `start_game()` et stoppé à la sortie
de l'état `game`.

### `draw_maze.py` — l'écran de jeu

**`compute_layout()`** calcule la plus grande tuile carrée qui rentre dans
`fenêtre − sidebar − marges`, avec un plancher à 8 px, puis centre le
labyrinthe. C'est le cœur de l'adaptation à la résolution.

**`draw_maze()`** dessine les murs **segment par segment** en lisant les 4
booléens de chaque `Tile`, avec des cercles aux extrémités pour combler les
jointures (`cap_radius`). L'épaisseur est proportionnelle à la tuile
(`tile // 8`). Les pacgums sont des cercles centrés : `tile // 9` pour un
normal, `tile // 4` pour un super.

**`draw_entities()`** dérive sa frame d'animation de l'horloge globale
(`get_ticks() // 120 % 3`), donc indépendamment du FPS. Pour chaque entité :
position interpolée, puis sprite. Les fantômes ont trois apparences
(normal / frightened / yeux) et **chaque branche a un repli en cercle coloré**
si le sprite manque.

**Sidebar** : quatre cadres empilés (SCORE / LIVES / LEVEL / TIME) dessinés par
le helper `draw_box()`, qui retourne le point d'ancrage du contenu. Les vies
sont des cœurs vectoriels (2 cercles + 1 triangle), rouges si restantes, gris
sinon. Le timer passe en rouge sous 10 secondes.

### `draw.py` — les écrans texte

Six fonctions (`draw_menu`, `draw_options`, `draw_highscores`, `draw_cheat`,
`draw_enter_name`, `draw_pause`) bâties sur le même patron : titre en
`title_font` centré à y=100, puis items espacés de 100 px, l'item sélectionné
dans la couleur `highlight`.

Le curseur (`draw_cursor`) est un **sprite de pacman animé** placé 50 px à
gauche de l'item, pas un simple triangle.

### `assets.py` — les sprites

Cache `dict` indexé par `(chemin, taille)` : chaque image n'est lue et
redimensionnée **qu'une fois par taille**. `_load` retourne `None` en cas
d'échec plutôt que de lever, d'où les replis côté dessin. Pacman a un dossier
par direction × 3 frames ; la direction `(0, 0)` au spawn affiche par défaut le
sprite orienté à droite.

### `utils.py` — types partagés et highscores

Définit `Rgb`, le `TypedDict` `Theme` et `Highscore`, utilisés par les trois
autres modules d'UI. `load_highscores` lit le JSON et le trie par score
décroissant (liste vide si le fichier est absent) ; `save_highscores`
relit-ajoute-réécrit.

### Flux complet d'une frame

```
clock.tick(60) → dt
  ↓
process_events()          clavier / souris → state, direction, buffer
  ↓
update_game(dt)           timer d'invincibilité, timer de niveau
  ├─ while pacman_timer   → step_pacman()  : buffer, move, pacgum, collisions
  └─ while ghost_timer    → step_ghosts()  : get_target() → BFS → 1 case
  ↓
render()                  layout → murs → entités interpolées → sidebar → flip
```

---

## Configuration

`config.json` est validé par Pydantic ([config_parser.py](src/config_parser.py)).
`level` est une **table de difficulté, une entrée par niveau** ; la dernière
entrée se répète indéfiniment au-delà.

| Champ | Effet |
|---|---|
| `width`, `height` | taille du labyrinthe (> 9) |
| `pacgum` | nombre de pacgums à semer |
| `level_max_time` | secondes avant de perdre une vie |
| `pacman_move_ms` | délai entre deux pas de pacman (plus grand = plus lent) |
| `ghost_move_ms` | idem pour les fantômes |
| `ghost_frightened_move_ms` | idem quand ils fuient |
| `invincible_ms` | durée du mode fright ; `0` = désactivé à ce niveau |

Le fichier tolère les lignes vides et les commentaires `#`, retirés avant le
parsing par `load_json`.

---

## Points connus et pistes d'amélioration

**Clyde ne mémorise pas sa cible**, contrairement au mode frightened : il tire
une case aléatoire à chaque pas, donc il oscille au lieu d'errer proprement. Le
Clyde original vise pacman au-delà de 8 cases de distance (Manhattan) et son
coin de scatter en deçà.

**`Ghost.run_to_spawn()` est du code mort** : les coins de scatter sont
calculés mais la fonction n'est jamais appelée.

**Le mode frightened vise des cases aléatoires**, pas les coins, malgré ce que
suggère le commentaire dans `get_target`.

**`draw_pause` et `draw_enter_name` n'acceptent pas le thème** et utilisent des
couleurs codées en dur : ces deux écrans ne suivent pas le changement de
palette.

**Le paramètre `height` des fonctions de `draw.py`** reçoit en réalité la
*largeur* (`center_ref`). L'usage est cohérent (`height // 2` donne bien le
centre horizontal) mais le nom induit en erreur.

**Dans `get_target`, la branche `BLUE`** réutilise les variables
`pacman_direc_x` / `pac_direc_x` pour stocker des coordonnées : le calcul est
juste, mais le nommage brouille la lecture.
