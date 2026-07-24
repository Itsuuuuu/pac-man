import sys

from src.ui.app import PacManApp


def main() -> None:
	"""Point d'entree unique du jeu : lit le chemin de config et lance l'application pygame."""
	if len(sys.argv) < 2:
		print("Error usage: python3 -m src config.json", file=sys.stderr)
		sys.exit(1)

	config_path = sys.argv[1]

	app = PacManApp(config_path)
	app.run()


if __name__ == "__main__":
	main()
