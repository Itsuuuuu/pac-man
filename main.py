from typing import Any
import json
import sys


def main():
	...

def load_json(filepath: str) -> Any:
	try:
		with open(filepath, 'r' ) as file:
			return json.load(file)
	except FileNotFoundError:
		print(f"Error: {filepath} not found", file=sys.stderr)
		sys.exit(1)
	except json.JSONDecodeError:
		print(
			f"Error: {filepath} invalid JSON",
			file=sys.stderr
		)
		sys.exit(1)

# def load_map(...: ...) -> ??:
# 	...



if __name__ == "__main__":
	try:
		main()
	except Exception as error:
		print("Error usage : python3 pac-man.py config.json")