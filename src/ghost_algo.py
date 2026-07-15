from collections import deque
from typing import Callable, Optional

N, E, S, W = 1, 2, 4, 8
DELTAS = {
	N: (0, -1),
	E: (1, 0),
	S: (0, 1),
	W: (-1, 0),
}

Coord = tuple[int, int]
HasWall = callable[[int, int, int], bool]

def bfs_next_step(
	has_wall: HasWall,
	width: int,
	height: int,
	start: Coord,
	goal: Coord,
) -> Optional[Coord]:
	if start == goal:
		return start

	queue: deque[Coord] = deque([start])
	came_from: dict[Coord, Optional[Coord]] = {start: None}

	while queue:
		x, y = queue.popleft()
		for direction, (dx, dy) in DELTAS.items():
			if has_wall(x, y, direction):
				continue
			nxt = (x + dx, y + dy)
			if not (0 <= nxt[0] < width and 0 <= nxt[1] < height):
				continue
			if nxt in came_from:
				continue
			came_from[nxt] = (x, y)
			if nxt == goal:
				return _first_step(came_from, start, goal)
			queue.append(nxt)
	return None


def bfs_path(
	has_wall: HasWall,
	width: int,
	height: int,
	start: Coord,
	goal: Coord,
) -> Optional[list[Coord]]:

	if start == goal:
		return [start]

	queue: deque[Coord] = deque([start])
	came_from: dict[Coord, Optional[Coord]] = {start: None}

	while queue:
		x, y = queue.popleft()
		for direction, (dx, dy) in DELTAS.items():
			if has_wall(x, y, direction):
				continue
			nxt = (x + dx, y + dy)
			if not (0 <= nxt[0] < width and 0 <= nxt[1] < height):
				continue
			if nxt in came_from:
				continue
			came_from[nxt] = (x, y)
			if nxt == goal:
				return _rebuild_path(came_from, start, goal)
			queue.append(nxt)
	return None


def _rebuild_path(
	came_from: dict[Coord, Optional[Coord]],
	start: Coord,
	goal: Coord,
) -> list[Coord]:
	path: list[Coord] = [goal]
	node: Optional[Coord] = goal
	while node != start:
		node = came_from[node]
		assert node is not None
		path.append(node)
	path.reverse()
	return path


def _first_step(
	came_from: dict[Coord, Optional[Coord]],
	start: Coord,
	goal: Coord,
) -> Coord:
	step: Coord = goal
	while came_from[step] != start:
		parent = came_from[step]
		assert parent is not None
		step = parent
	return step


def wall_from_grid(maze_grid: list[list[int]]) -> HasWall:
	return lambda x, y, d: bool(maze_grid[y][x] & d)


def wall_from_tiles(tile_map: list) -> HasWall:
	return lambda x, y, d: tile_map[y][x].has_wall(d)


#if __name__ == "__main__":
#	from mazegenerator import MazeGenerator
#
#	width, height = 20, 20
#	mg = MazeGenerator(size=(width, height), seed=42)
#	has_wall = wall_from_grid(mg.maze)
#
#	ghost: Coord = (0, 0)
#	pacman: Coord = (width - 1, height - 1)
#	step = bfs_next_step(has_wall, width, height, ghost, pacman)
#	path = bfs_path(has_wall, width, height, ghost, pacman)
#
#	print(f"Fantome  : {ghost}")
#	print(f"Pacman   : {pacman}")
#	print(f"Prochaine case du fantome : {step}")
#	if path is None:
#		print("Chemin   : aucun (pacman inatteignable)")
#	else:
#		print(f"Chemin   : {len(path)} cases -> {path}")
