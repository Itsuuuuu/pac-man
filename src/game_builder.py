from typing import Any
import json
import sys

from mazegenerator import MazeGenerator
from pydantic import BaseModel, ValidationError

from src.config_parser import GameConfig, LevelConfig
from src.game_setting import GameSetting


# Borne du nombre de passes de correction de la config : une passe corrige au
# moins un champ, donc ce plafond ne peut pas etre atteint en pratique.
MAX_SANITIZE_PASSES = 50


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


def field_default(location: tuple[Any, ...]) -> Any:
    """Valeur de repli pour le champ designe par une localisation d'erreur
    Pydantic.

    Une localisation est le chemin du champ fautif, par exemple ("lives",)
    pour un champ de GameConfig ou ("level", 0, "width") pour un champ du
    premier niveau.

    Args:
        location: Chemin du champ, tel que fourni par ValidationError.

    Returns:
        La valeur par defaut declaree dans le modele, ou None si le champ est
        inconnu ou n'a pas de defaut.
    """
    if not location:
        return None

    # ("level", <index>, "<champ>") designe un champ de niveau ; tout le reste
    # est un champ de premier niveau.
    model: type[BaseModel]
    if location[0] == "level" and len(location) == 3:
        model, name = LevelConfig, location[2]
    else:
        model, name = GameConfig, location[0]

    field = model.model_fields.get(str(name))
    if field is None or field.is_required():
        return None
    return field.get_default()


def clamp_value(data: Any, location: tuple[Any, ...], value: Any) -> bool:
    """Remplace en place la valeur fautive designee par location.

    Args:
        data: Structure issue du JSON, modifiee en place.
        location: Chemin du champ fautif.
        value: Valeur de remplacement.

    Returns:
        True si le remplacement a pu etre fait.
    """
    target: Any = data
    for key in location[:-1]:
        try:
            target = target[key]
        except (KeyError, IndexError, TypeError):
            return False

    try:
        target[location[-1]] = value
    except (KeyError, IndexError, TypeError):
        return False
    return True


def sanitize_config(data: Any) -> GameConfig:
    """Valide la config en ramenant chaque valeur invalide a son defaut.

    Le sujet demande de ne jamais s'arreter sur une config douteuse : chaque
    champ hors bornes, mal type ou manquant est remplace par la valeur par
    defaut du modele, un message explicite est affiche, et la partie continue.
    Les cles inconnues sont ignorees par Pydantic.

    Args:
        data: Structure issue du fichier JSON.

    Returns:
        Une config valide, au besoin corrigee.

    Raises:
        ValueError: Si la config reste invalide apres correction, ce qui ne
            peut arriver que sur une structure irrecuperable.
    """
    if not isinstance(data, dict):
        print("Warning: config is not a JSON object, using defaults",
              file=sys.stderr)
        data = {}

    # La table de niveaux n'a pas de defaut utilisable : sans elle, on repart
    # sur un niveau unique entierement par defaut.
    if not isinstance(data.get("level"), list) or not data["level"]:
        print("Warning: 'level' missing or empty, falling back to one "
              "default level", file=sys.stderr)
        data["level"] = [{}]

    # Chaque passe corrige les champs signales par Pydantic. Le nombre de
    # passes est borne par le nombre de champs, donc la boucle termine.
    for _ in range(MAX_SANITIZE_PASSES):
        try:
            return GameConfig(**data)
        except ValidationError as error:
            if not repair_errors(data, error):
                raise ValueError(str(error)) from error

    raise ValueError("configuration could not be repaired")


def repair_errors(data: Any, error: ValidationError) -> bool:
    """Corrige les champs signales par une erreur de validation.

    Args:
        data: Structure issue du JSON, modifiee en place.
        error: Erreur levee par Pydantic.

    Returns:
        True si au moins un champ a ete corrige.
    """
    repaired = False
    for detail in error.errors():
        location = tuple(detail["loc"])
        default = field_default(location)
        if default is None:
            continue
        if clamp_value(data, location, default):
            field = ".".join(str(key) for key in location)
            print(f"Warning: config field '{field}' is invalid "
                  f"({detail['msg']}), using default {default!r}",
                  file=sys.stderr)
            repaired = True
    return repaired


def load_config(config_path: str) -> GameConfig:
    """Lit le fichier de config et en tire une config valide.

    Les valeurs invalides sont ramenees a leurs defauts plutot que de faire
    echouer le lancement ; seule une structure irrecuperable arrete le
    programme, avec un message clair et sans traceback.
    """
    try:
        return sanitize_config(load_json(config_path))
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
