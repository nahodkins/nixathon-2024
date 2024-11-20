from fastapi import FastAPI
from models import *
import heapq
from typing import List, Tuple

app = FastAPI()


@app.get('/healthz')
async def status_dict():
    return {"status": "OK"}

turn_left = MoveResponse(move=MoveCommand.TURN_LEFT)
turn_right = MoveResponse(move=MoveCommand.TURN_RIGHT)
move = MoveResponse(move=MoveCommand.MOVE)
fire = MoveResponse(move=MoveCommand.FIRE)

previous_field = None

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

def get_coins(game_field: GameField) -> List[Tuple[int, int]]:
    coins = []
    for y, row in enumerate(game_field.parsed_field):
        for x, cell in enumerate(row):
            if cell.cell_type == CellType.COIN:
                coins.append((x, y))
    return coins


def find_enemies_in_line(enemies: List[Tuple[int, int, Direction]], player: Tuple[int, int, Direction]):
    for enemy in enemies:
        if enemy[0] == player[0] or enemy[1] == player[1]:
            print("Found an enemy in line")

def find_nearest_enemy(enemies: List[Tuple[int, int, Direction]], player: Tuple[int, int, Direction]) -> Tuple[int, int, Direction]:
    shortest_distance = float('inf')
    nearest_enemy = None
    for enemy in enemies:
        distance = abs(enemy[0] - player[0]) + abs(enemy[1] - player[1])
        if distance < shortest_distance:
            shortest_distance = distance
            nearest_enemy = enemy
    return nearest_enemy

def find_nearest_coin(coins: List[Tuple[int, int]], player: Tuple[int, int, Direction]) -> Tuple[int, int]:
    min_moves = float('inf')
    nearest_coin = None
    for coin in coins:
        dx = abs(coin[0] - player[0])
        dy = abs(coin[1] - player[1])
        turns = 0
        if (dx > 0 and dy > 0) or (player[2] in [Direction.UP, Direction.DOWN] and dx > 0) or (player[2] in [Direction.LEFT, Direction.RIGHT] and dy > 0):
            turns = 1
        moves = dx + dy + turns
        if moves < min_moves:
            min_moves = moves
            nearest_coin = coin
    return nearest_coin


def move_to_coin(game_field: GameField, player: Tuple[int, int, Direction], coin: Tuple[int, int]) -> MoveResponse:
    if player[0] == coin[0]:
        if player[1] < coin[1]:
            if player[2] == Direction.DOWN:
                return move
            elif player[2] == Direction.UP:
                return turn_right
            elif player[2] == Direction.LEFT:
                return turn_left
            else:
                return turn_right
        else:
            if player[2] == Direction.UP:
                return move
            elif player[2] == Direction.DOWN:
                return turn_right
            elif player[2] == Direction.RIGHT:
                return turn_left
            else:
                return turn_right
    elif player[1] == coin[1]:
        if player[0] < coin[0]:
            if player[2] == Direction.RIGHT:
                return move
            elif player[2] == Direction.UP:
                return turn_right
            elif player[2] == Direction.DOWN:
                return turn_left
            else:
                return turn_right
        else:
            if player[2] == Direction.LEFT:
                return move
            elif player[2] == Direction.DOWN:
                return turn_right
            elif player[2] == Direction.UP:
                return turn_left
            else:
                return turn_right
    return move


@app.post('/move')
async def make_move(game_field: GameField) -> MoveResponse:
    # print(game_field)
    # print(enemies)
    # print(player)
    enemies = get_enemies(game_field)
    player = get_player(game_field)
    coins = get_coins(game_field)
    nearest_coin = find_nearest_coin(coins, player)

    return move_to_coin(game_field, player, nearest_coin)
    # if enemies[0][2] == Direction.LEFT:
    #     print("Turning left")
    #     return turn_left
    # elif enemies[0][2] == Direction.RIGHT:
    #     print("Turning right")
    #     return turn_right
    # else:
    #     print("moving forward")
    #     return move


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


# 1. Если меньше 5 ходов до сужение, то начинать уходить
# 2. elif: если смотрит противник -- убегать
# 3. elif: если ты смотришь на противника -- стреляй
# 4. найти кратчайший путь к монете и сделать шаг
