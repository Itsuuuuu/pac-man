from pydantic import BaseModel, Field


class LevelConfig(BaseModel):
    """Reglages d'un niveau : taille du labyrinthe, densite de pacgums et
    difficulte.

    Les durees sont en millisecondes. Pour les vitesses, plus la valeur est
    GRANDE, plus le personnage est LENT (c'est le delai entre deux
    deplacements d'une case).
    """

    width: int = Field(default=10, gt=9)
    height: int = Field(default=10, gt=9)
    pacgum: int = Field(default=10, gt=0)
    level_max_time: int = Field(default=90, gt=1)
    pacman_move_ms: int = Field(default=200, gt=0)
    ghost_move_ms: int = Field(default=260, gt=0)
    ghost_frightened_move_ms: int = Field(default=380, gt=0)
    # 0 = pas de mode fright a ce niveau : le super pacgum ne rapporte que des
    # points
    invincible_ms: int = Field(default=6000, ge=0)


class GameConfig(BaseModel):
    highscore_filename: str = "highscore.json"
    # Table de difficulte, une entree par niveau. La derniere se repete
    # indefiniment.
    level: list[LevelConfig] = Field(min_length=1)
    lives: int = Field(default=1, gt=0)
    points_per_pacgum: int = Field(default=1, gt=0)
    points_per_super_pacgum: int = Field(default=1, gt=0)
    points_per_ghost: int = Field(default=1, gt=0)
    seed: int = Field(default=42)

    def level_params(self, level: int) -> LevelConfig:
        """Reglages du niveau demande (1-based), bornes aux deux bouts de la
        table.
        """
        return self.level[min(max(level, 1), len(self.level)) - 1]
