"""Point d'entree du build autonome.

La version packagee est lancee par un double-clic, sans ligne de commande :
elle doit donc trouver sa configuration toute seule. Ce module cherche un
config.json a cote de l'executable, puis se rabat sur celui embarque dans le
bundle, avant de passer la main au jeu.

Lance directement (python launcher.py config.json), il se comporte comme
`python -m src config.json`.
"""

import os
import sys


def bundle_dir() -> str:
    """Racine des fichiers embarques.

    Returns:
        Le dossier temporaire cree par PyInstaller quand le jeu tourne
        depuis un build autonome, sinon la racine du depot.
    """
    meipass = getattr(sys, "_MEIPASS", None)
    if isinstance(meipass, str):
        return meipass
    return os.path.dirname(os.path.abspath(__file__))


def default_config_path() -> str:
    """Chemin de configuration utilise quand aucun argument n'est donne.

    Un config.json place a cote de l'executable a la priorite : c'est ainsi
    que le joueur regle le jeu sans le reconstruire.

    Returns:
        Le chemin du fichier de configuration a utiliser.
    """
    beside_executable = os.path.join(
        os.path.dirname(os.path.abspath(sys.executable)), "config.json"
    )
    if os.path.isfile(beside_executable):
        return beside_executable
    return os.path.join(bundle_dir(), "config.json")


def main() -> None:
    """Complete les arguments si besoin, puis lance le jeu."""
    if len(sys.argv) < 2:
        sys.argv = [sys.argv[0], default_config_path()]

    from src.__main__ import main as run_game

    run_game()


if __name__ == "__main__":
    main()
