from fastapi import FastAPI
from models import *
import random
from typing import List, Tuple

app = FastAPI()


@app.get('/healthz')
async def status_dict():
    return {"status": "OK"}

turn_left = MoveResponse(move=MoveCommand.TURN_LEFT)
turn_right = MoveResponse(move=MoveCommand.TURN_RIGHT)
move = MoveResponse(move=MoveCommand.MOVE)
fire = MoveResponse(move=MoveCommand.FIRE)

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
                return x, y, cell.direction


@app.post('/move')
async def make_move(game_field: GameField) -> MoveResponse:
    print(game_field)
    enemies = get_enemies(game_field)
    player = get_player(game_field)
    print(enemies)
    print(player)
    if enemies[0][2] == Direction.LEFT:
        print("Turning left")
        return turn_left
    elif enemies[0][2] == Direction.RIGHT:
        print("Turning right")
        return turn_right
    else:
        print("moving forward")
        return move


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


# 1. Если меньше 5 ходов до сужение, то начинать уходить
# 2. elif: если смотрит противник -- убегать
# 3. elif: если ты смотришь на противника -- стреляй
# 4. найти кратчайший путь к монете и сделать шаг
