from src.tile import TileType, Tile
from enum import Enum
from src.ghost_algo import bfs_next_step, wall_from_tiles
import random

# Correspondance direction (dx, dy) -> bit de mur (N=1, E=2, S=4, W=8)
DIRECTION_FLAGS: dict[tuple[int, int], int] = {
    (0, -1): 1,
    (1, 0): 2,
    (0, 1): 4,
    (-1, 0): 8,
}


class Color(Enum):
    RED = "red"
    PINK = "pink"
    BLUE = "blue"
    ORANGE = "orange"


class Entity:
    """Base commune a tous les personnages qui se deplacent dans le
    labyrinthe.

    Elle porte la position, la case de depart, la case precedente (utilisee
    par l'affichage pour interpoler) et surtout la regle "on ne traverse pas
    les murs", que Pacman et les fantomes appliquent donc a l'identique.
    """

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.spawn_x = x
        self.spawn_y = y
        # Case occupee avant le dernier pas : sert uniquement a
        # l'affichage, qui interpole entre (prev_x, prev_y) et (x, y)
        # pour lisser le deplacement.
        self.prev_x = x
        self.prev_y = y

    def can_move(
        self,
        direc_x: int,
        direc_y: int,
        tile_map: list[list[Tile]],
    ) -> bool:
        """Indique si la case courante laisse passer dans cette direction.

        Args:
            direc_x: Composante horizontale du deplacement (-1, 0 ou 1).
            direc_y: Composante verticale du deplacement (-1, 0 ou 1).
            tile_map: Carte du niveau.

        Returns:
            True si aucun mur ne bloque le pas.
        """
        direction_flag = DIRECTION_FLAGS.get((direc_x, direc_y), 0)
        if direction_flag == 0:
            return False
        return not tile_map[self.y][self.x].has_wall(direction_flag)

    def move_to_next(
        self,
        direc_x: int,
        direc_y: int,
        tile_map: list[list[Tile]],
    ) -> None:
        """Avance d'une case si le mur le permet, sinon ne bouge pas.

        Args:
            direc_x: Composante horizontale du deplacement.
            direc_y: Composante verticale du deplacement.
            tile_map: Carte du niveau.
        """
        # On part toujours de la case courante : si le pas est bloque,
        # prev == courant et l'affichage n'interpole rien.
        self.prev_x, self.prev_y = self.x, self.y

        # Verification mur, si non, deplacement
        if not self.can_move(direc_x, direc_y, tile_map):
            return
        self.x += direc_x
        self.y += direc_y

    def teleport_to_spawn(self) -> None:
        """Repositionne l'entite sur sa case de depart, sans animation."""
        self.x = self.spawn_x
        self.y = self.spawn_y
        # Teleportation : prev suit, sinon l'affichage ferait glisser
        # l'entite a travers le labyrinthe jusqu'au spawn.
        self.prev_x = self.spawn_x
        self.prev_y = self.spawn_y


class Pacman(Entity):
    def __init__(self, x: int, y: int, invincible: bool = False) -> None:
        super().__init__(x, y)
        self.direction: tuple[int, int] = (0, 0)
        self.invincible = invincible

    def move_to_next(
        self,
        direc_x: int,
        direc_y: int,
        tile_map: list[list[Tile]],
    ) -> None:
        """Avance d'une case et memorise la direction effectivement prise.

        La direction ne change que si le pas a eu lieu : un virage bloque
        laisse pacman oriente comme avant.
        """
        super().move_to_next(direc_x, direc_y, tile_map)
        if (self.x, self.y) != (self.prev_x, self.prev_y):
            self.direction = (direc_x, direc_y)

    def fear_ghost(self) -> bool:
        return self.invincible

    # Si le Pacman se fait attraper par un ghost, il retourne au spawn
    def back_to_spawn(self) -> None:
        self.teleport_to_spawn()
        self.direction = (0, 0)

    # Si le Pacman passe sur un super pacgum, on passe is_invinsible
    # en true pour quelques secondes
    def is_invincible(self) -> bool:
        # mettre un timer
        return self.invincible


class Ghost(Entity):
    def __init__(
        self,
        x: int,
        y: int,
        current_zone: TileType = TileType.SPAWN,
        color: Color = Color.RED,
    ) -> None:
        super().__init__(x, y)
        self.current_zone = current_zone
        self.color = color
        self.is_dead = False
        self.frightened_target: tuple[int, int] | None = None

    # Doit devenir des petits yeux, et bfs vers la case de son spawn
    def back_to_spawn(self) -> None:
        self.is_dead = True

    # Remise au spawn seche (perte de vie) : contrairement a back_to_spawn, le
    # fantome ne rentre pas en marchant, il est repositionne d'un coup.
    def respawn(self) -> None:
        self.teleport_to_spawn()
        self.is_dead = False

    def run_to_spawn(self, width: int, height: int) -> tuple[int, int]:
        if self.color == Color.RED:
            return (width - 2, 1)
        elif self.color == Color.PINK:
            return (1, 1)
        elif self.color == Color.BLUE:
            return (width - 2, height - 2)
        else:
            return (1, height - 2)

    # Empeche qu'une coordonnée sorte de la map
    def block(self, val: int, min_val: int, max_val: int) -> int:
        return max(min_val, min(val, max_val))

    def random_frightened_target(
        self, width: int, height: int
    ) -> tuple[int, int]:
        return (random.randint(1, width - 2), random.randint(1, height - 2))

    def get_frightened_target(
        self, width: int, height: int
    ) -> tuple[int, int]:
        if (self.frightened_target is None
                or (self.x, self.y) == self.frightened_target):
            self.frightened_target = self.random_frightened_target(
                width, height)
            while (self.frightened_target == (self.x, self.y)
                    and width > 2 and height > 2):
                self.frightened_target = self.random_frightened_target(
                    width, height)
        return self.frightened_target

    def get_target(
        self,
        pacman: Pacman,
        blinky: 'Ghost | None',
        width: int,
        height: int,
    ) -> tuple[int, int]:
        if self.is_dead:
            return (self.spawn_x, self.spawn_y)

        # Si pacman est invinsible, les ghosts fuient dans leurs coin
        if pacman.invincible:
            return self.get_frightened_target(width, height)

        self.frightened_target = None

        # Cible pacman
        if self.color == Color.RED:
            return (pacman.x, pacman.y)

        # Vise 4 cases devant pacman
        elif self.color == Color.PINK:
            pac_direc_x, pac_direc_y = pacman.direction
            target_x = self.block(pacman.x + 4 * pac_direc_x, 0, width - 1)
            target_y = self.block(pacman.y + 4 * pac_direc_y, 0, height - 1)
            return (target_x, target_y)

        # Truc chiant entre blinky et pacman, il prend les cases entre
        # pacman et rouge et il double la distance, et cette case sera
        # la cible
        elif self.color == Color.BLUE:
            if blinky is None:
                return (pacman.x, pacman.y)
            pacman_direc_x, pac_direc_y = pacman.direction
            pac_direc_x = pacman.x + 2 * pacman_direc_x
            pac_direc_y = pacman.y + 2 * pac_direc_y

            target_x = self.block(2 * pac_direc_x - blinky.x, 0, width - 1)
            target_y = self.block(2 * pac_direc_y - blinky.y, 0, height - 1)
            return (target_x, target_y)

        # Mouvement Aléatoire (Color.ORANGE)
        else:
            target_x = random.randint(1, width - 2)
            target_y = random.randint(1, height - 2)
            return (target_x, target_y)

    # On met en paramètre Blinky car Inky à besoin de connaître
    # sa position pour bouger
    def move(
        self,
        tile_map: list[list[Tile]],
        width: int,
        height: int,
        pacman: Pacman,
        blinky: 'Ghost | None',
    ) -> None:
        target = self.get_target(pacman, blinky, width, height)
        has_wall = wall_from_tiles(tile_map)
        next_step = bfs_next_step(
            has_wall, width, height, (self.x, self.y), target)

        if next_step is None:
            self.prev_x, self.prev_y = self.x, self.y
        else:
            # Le pas choisi par le BFS est applique via move_to_next, donc
            # soumis a la meme verification de mur que pacman.
            self.move_to_next(
                next_step[0] - self.x, next_step[1] - self.y, tile_map)

        if self.is_dead and (self.x, self.y) == (self.spawn_x, self.spawn_y):
            self.is_dead = False
