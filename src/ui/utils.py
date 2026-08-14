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


def load_highscores(filepath: str) -> list[Highscore]:
    try:
        with open(filepath, 'r') as file:
            data: list[Highscore] = json.load(file)
    except FileNotFoundError:
        return []

    return sorted(data, key=lambda entry: entry["score"], reverse=True)


def ordinal(n: int) -> str:
    if 11 <= n % 100 <= 13:
        suffix = "TH"
    else:
        suffix = {1: "ST", 2: "ND", 3: "RD"}.get(n % 10, "TH")
    return f"{n}{suffix}"


def save_highscores(filepath: str, pseudo: str, score: int) -> None:
    try:
        with open(filepath, 'r') as file:
            data: list[Highscore] = json.load(file)
    except FileNotFoundError:
        data = []

    data.append({"pseudo": pseudo, "score": score})

    with open(filepath, 'w') as file:
        json.dump(data, file, indent=4)
