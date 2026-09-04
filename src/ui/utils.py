import json
from typing import Any, TypedDict


Highscore = dict[str, Any]
Rgb = tuple[int, int, int]


class Theme(TypedDict):
    """Palette d'un theme : son nom et les couleurs de chaque element."""

    name: str
    background: Rgb
    text: Rgb
    highlight: Rgb
    title: Rgb
    wall: Rgb


MAX_HIGHSCORES = 10


def load_highscores(filepath: str) -> list[Highscore]:
    """Charge les highscores depuis un fichier JSON.

    Args:
        filepath: Chemin du fichier JSON des highscores.

    Returns:
        La liste des entrees valides, triee par score decroissant et
        limitee a MAX_HIGHSCORES. Liste vide si le fichier est absent
        ou illisible.
    """
    try:
        with open(filepath, 'r') as file:
            data: Any = json.load(file)
    except (OSError, json.JSONDecodeError):
        return []

    if not isinstance(data, list):
        return []

    entries: list[Highscore] = [
        {"pseudo": str(entry["pseudo"]), "score": int(entry["score"])}
        for entry in data
        if isinstance(entry, dict)
        and isinstance(entry.get("pseudo"), str)
        and isinstance(entry.get("score"), int)
        and entry["score"] >= 0
    ]

    entries.sort(key=lambda entry: int(entry["score"]), reverse=True)
    return entries[:MAX_HIGHSCORES]


def ordinal(n: int) -> str:
    if 11 <= n % 100 <= 13:
        suffix = "TH"
    else:
        suffix = {1: "ST", 2: "ND", 3: "RD"}.get(n % 10, "TH")
    return f"{n}{suffix}"


def save_highscores(filepath: str, pseudo: str, score: int) -> None:
    """Insere un score dans le classement et reecrit le fichier JSON.

    Le classement est maintenu trie par score decroissant et plafonne a
    MAX_HIGHSCORES entrees. Si le score ne merite pas sa place, le
    fichier n'est pas reecrit.

    Args:
        filepath: Chemin du fichier JSON des highscores.
        pseudo: Nom du joueur.
        score: Score obtenu (entier positif ou nul).
    """
    data = load_highscores(filepath)

    # Sortie immediate : classement plein et score trop faible.
    # On compare d'abord au pire score, ce qui evite tout parcours.
    if len(data) >= MAX_HIGHSCORES and score <= data[-1]["score"]:
        return

    # Recherche de la position d'insertion en remontant depuis la fin
    # (les moins bons scores en premier) : on s'arrete des qu'on
    # rencontre un score au moins egal au notre.
    index = len(data)
    while index > 0 and data[index - 1]["score"] < score:
        index -= 1

    data.insert(index, {"pseudo": pseudo, "score": score})
    del data[MAX_HIGHSCORES:]

    try:
        with open(filepath, 'w') as file:
            json.dump(data, file, indent=4)
    except OSError as error:
        print(f"Impossible d'enregistrer les highscores : {error}")
