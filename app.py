from fastapi import FastAPI
from models import *
import random
from typing import List, Tuple


app = FastAPI()


@app.get('/healthz')
async def status_dict():
    return {"status": "OK"}


def get_enemies(game_field: GameField) -> List[Tuple[int, int, Direction]]:
    enemies = []
    for y, row in enumerate(game_field.parsed_field):
        for x, cell in enumerate(row):
            if cell.cell_type == CellType.ENEMY and cell.direction:
                enemies.append((x, y, cell.direction))
    return enemies


def get_player(game_field: GameField) -> Tuple[int, int, Direction]:
    for y, row in enumerate(game_field.parsed_field):
        for x, cell in enumerate(row):
            if cell.cell_type == CellType.PLAYER and cell.direction:
                return (x, y, cell.direction)

@app.post('/move')
async def make_move(game_field: GameField) -> MoveResponse:
    enemies = get_enemies(game_field)
    player = get_player(game_field)
    print(enemies)
    print(player)
    if enemies[0][2] == Direction.LEFT:
        return MoveResponse(moove = MoveCommand.TURN_LEFT)
    elif enemies[0][2] == Direction.RIGHT:
        return MoveResponse(moove = MoveCommand.TURN_RIGHT)
    else:
        return MoveResponse(moove = MoveCommand.MOVE)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
