from pydantic import BaseModel, Field
from typing import List, Literal
from enum import Enum


class CellType(str, Enum):
    PLAYER = "P"
    ENEMY = "E"
    COIN = "C"
    ASTEROID = "A"
    EMPTY = "_"


class Direction(str, Enum):
    UP = "N"
    DOWN = "S"
    LEFT = "W"
    RIGHT = "E"


class MoveCommand(str, Enum):
    TURN_RIGHT = "R"
    TURN_LEFT = "L"
    MOVE = "M"
    FIRE = "F"


class MoveResponse(BaseModel):
    move: MoveCommand


class FieldCell(BaseModel):
    cell_type: CellType
    direction: Direction | None = None

    @classmethod
    def from_str(cls, cell_str: str):
        print(cell_str)
        if len(cell_str) == 1:
            return cls(cell_type=CellType(cell_str))
        elif len(cell_str) > 1:
            return cls(cell_type=CellType(cell_str[0]), direction=Direction(cell_str[1]))
        else:
            raise ValueError("Invalid cell string")


class GameField(BaseModel):
    field: List[List[str]] = Field(..., min_items=13, max_items=13)
    narrowingIn: int
    gameId: int

    @property
    def parsed_field(self) -> List[List[FieldCell]]:
        return [[FieldCell.from_str(cell) for cell in row] for row in self.field]
