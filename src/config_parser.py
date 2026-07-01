from pydantic import BaseModel, Field, model_validator


class LevelConfig(BaseModel):
	width: int = Field(default= 1, ge= 1)
	height: int = Field(default= 1, ge= 1)

class GameConfig(BaseModel):
	highscore_filename: str = "jsp"
	level: list[tuple[int, int]]
	lives: int = Field(default= 1, gt= 0)
	pacgum: int = Field(default= 1, gt= 0)
	points_per_pacgum: int = Field(default= 1, gt= 0)
	points_per_super_pacgum: int = Field(default= 1, gt= 0)
	points_per_ghost: int = Field(default= 1, gt= 0)
	seed: int = Field(default= 42)
	level_max_time: int = Field(default= 90, gt= 1)


# du coup faire un truc qui teste la map choisi, si elle passe
# par ce BaseModel, on peut donc la mettre dans des 
# structures / objets



