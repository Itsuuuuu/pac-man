from typing import Any
import json
import sys

from mazegenerator import MazeGenerator
from src.config_parser import GameConfig
from src.game_setting import GameSetting


def load_json(filepath: str) -> Any:
    """Charge un fichier JSON en ignorant les lignes vides et les commentaires
    (#).
    """
    try:
        cleaned_lines = []
        with open(filepath, "r") as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                cleaned_lines.append(line)
        return json.loads("\n".join(cleaned_lines))

    except FileNotFoundError:
        print(f"Error: {filepath} not found", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: {filepath} invalid JSON", file=sys.stderr)
        sys.exit(1)


def load_config(config_path: str) -> GameConfig:
    """Lit et valide le fichier de config, et sort proprement si elle est
    invalide.
    """
    try:
        # Les ** servent pour l'unpacking + la validation Pydantic
        return GameConfig(**load_json(config_path))
    except ValueError as error:
        print(f"Error: {config_path} invalid config\n{error}", file=sys.stderr)
        sys.exit(1)


def build_level(
    config: GameConfig,
    level: int,
    score: int,
    lives: int,
) -> GameSetting:
    """Construit un niveau : labyrinthe neuf, score et vies conserves de la
    partie en cours.

    Le niveau est 1-based. Les parametres de difficulte viennent de la table
    de la config (la derniere entree se repete indefiniment), et la graine
    derive du numero de niveau pour que chaque niveau ait son propre
    labyrinthe.
    """
    params = config.level_params(level)
    seed = config.seed + level * 1000

    # Generation du labyrinthe
    maze_gen = MazeGenerator(size=(params.width, params.height), seed=seed)

    return GameSetting(
        config=config,
        params=params,
        seed=seed,
        lives=lives,
        current_score=score,
        maze_grid=maze_gen.maze,
    )


def build_game(config_path: str) -> GameSetting:
    """Demarre une partie neuve au niveau 1 depuis un fichier de config."""
    config = load_config(config_path)
    return build_level(config, level=1, score=0, lives=config.lives)
