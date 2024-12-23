from fastapi import FastAPI
from models import *
import heapq
from typing import List, Tuple
from copy import deepcopy

app = FastAPI()


@app.get('/healthz')
async def status_dict():
    return {"status": "OK"}

turn_left = MoveResponse(move=MoveCommand.TURN_LEFT)
turn_right = MoveResponse(move=MoveCommand.TURN_RIGHT)
move = MoveResponse(move=MoveCommand.MOVE)
fire = MoveResponse(move=MoveCommand.FIRE)

previous_field = None
next_step = None

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


def find_nearest_asteroid(game_field: GameField, player: Tuple[int, int, Direction]) -> Tuple[int, int, Direction]:
    shortest_distance = float('inf')
    nearest_asteroid = None
    for y, row in enumerate(game_field.parsed_field):
        for x, cell in enumerate(row):
            if cell.cell_type == CellType.ASTEROID:
                distance = abs(x - player[0]) + abs(y - player[1])
                if distance < shortest_distance:
                    shortest_distance = distance
                    nearest_asteroid = (x, y, player[2])
    return nearest_asteroid


def has_asteroid_ahead(game_field: GameField, player: Tuple[int, int, Direction]) -> bool:
    if player[2] == Direction.UP:
        print(player, check_asteroid(game_field, (player[0], player[1] - 1)))
        return check_asteroid(game_field, (player[0], player[1] - 1))
    elif player[2] == Direction.RIGHT:
        print(player, check_asteroid(game_field, (player[0] + 1, player[1])))
        return check_asteroid(game_field, (player[0] + 1, player[1]))
    elif player[2] == Direction.LEFT:
        print(player, check_asteroid(game_field, (player[0] - 1, player[1])))
        return check_asteroid(game_field, (player[0] - 1, player[1]))
    else:
        print(player, check_asteroid(game_field, (player[0], player[1] + 1)))
        return check_asteroid(game_field, (player[0], player[1] + 1))


def has_asteroid_to_left(game_field: GameField, player: Tuple[int, int, Direction]) -> bool:
    if player[2] == Direction.UP:
        return check_asteroid(game_field, (player[0] - 1, player[1]))
    elif player[2] == Direction.RIGHT:
        return check_asteroid(game_field, (player[0], player[1] - 1))
    elif player[2] == Direction.LEFT:
        return check_asteroid(game_field, (player[0], player[1] + 1))
    else:
        return check_asteroid(game_field, (player[0] + 1, player[1]))


def has_asteroid_to_right(game_field: GameField, player: Tuple[int, int, Direction]) -> bool:
    if player[2] == Direction.UP:
        return check_asteroid(game_field, (player[0] + 1, player[1]))
    elif player[2] == Direction.RIGHT:
        return check_asteroid(game_field, (player[0], player[1] + 1))
    elif player[2] == Direction.LEFT:
        return check_asteroid(game_field, (player[0], player[1] - 1))
    else:
        return check_asteroid(game_field, (player[0] - 1, player[1]))

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


def turn_from_asteroids(game_field: GameField, player: Tuple[int, int, Direction]) -> MoveResponse:
    if has_asteroid_to_right(game_field, player):
        print("Turning left")
        return turn_left
    elif has_asteroid_to_left(game_field, player):
        print("Turning right")
        return turn_right
    else:
        print("Turning right")
        return turn_right


def move_to_target(game_field: GameField, player: Tuple[int, int, Direction], target: Tuple[int, int]) -> (MoveResponse, bool):
    global next_step
    if has_asteroid_ahead(game_field, player):
        next_step = move
        return turn_from_asteroids(game_field, player), (player[0] == target[0] and player[1] == target[1])

    if player[0] == target[0]:
        if player[1] < target[1]:
            if player[2] == Direction.DOWN:
                print("Moving")
                return move, (player[0] == target[0] and player[1] == target[1])
            elif player[2] == Direction.UP:
                return turn_from_asteroids(game_field, player), (player[0] == target[0] and player[1] == target[1])
            elif player[2] == Direction.LEFT:
                print("Turning left")
                return turn_left, (player[0] == target[0] and player[1] == target[1])
            else:
                print("Turning right")
                return turn_right, (player[0] == target[0] and player[1] == target[1])
        else:
            if player[2] == Direction.UP:
                print("Moving")
                return move, (player[0] == target[0] and player[1] == target[1])
            elif player[2] == Direction.DOWN:
                return turn_from_asteroids(game_field, player), (player[0] == target[0] and player[1] == target[1])
            elif player[2] == Direction.RIGHT:
                print("Turning left")
                return turn_left, (player[0] == target[0] and player[1] == target[1])
            else:
                return turn_right, (player[0] == target[0] and player[1] == target[1])
    elif player[1] == target[1]:
        if player[0] < target[0]:
            if player[2] == Direction.RIGHT:
                return move, (player[0] == target[0] and player[1] == target[1])
            elif player[2] == Direction.UP:
                print("Turning right")
                return turn_right, (player[0] == target[0] and player[1] == target[1])
            elif player[2] == Direction.DOWN:
                print("Turning left")
                return turn_left, (player[0] == target[0] and player[1] == target[1])
            else:
                return turn_from_asteroids(game_field, player), (player[0] == target[0] and player[1] == target[1])
        else:
            if player[2] == Direction.LEFT:
                return move, (player[0] == target[0] and player[1] == target[1])
            elif player[2] == Direction.DOWN:
                print("Turning right")
                return turn_right, (player[0] == target[0] and player[1] == target[1])
            elif player[2] == Direction.UP:
                print("Turning left")
                return turn_left, (player[0] == target[0] and player[1] == target[1])
            else:
                return turn_from_asteroids(game_field, player), (player[0] == target[0] and player[1] == target[1])
    return move, (player[0] == target[0] and player[1] == target[1])


def move_to_center(game_field: GameField, player: Tuple[int, int, Direction]) -> (MoveResponse, bool):
    if not check_asteroid(game_field, (6, 6)):
        return move_to_target(game_field, player, (6, 6))
    else:
        for x in (5, 6, 7):
            for y in (5, 6, 7):
                if not check_asteroid(game_field, (x, y)):
                    return move_to_target(game_field, player, (x, y))


def check_asteroid(game_field: GameField, point: Tuple[int, int]) -> bool:
    return game_field.parsed_field[point[1]][point[0]].cell_type == CellType.ASTEROID

@app.post('/move')
async def make_move(game_field: GameField) -> MoveResponse:
    global next_step, previous_field
    print("narrowingIn", game_field.narrowingIn)

    # print(game_field)
    # print(enemies)
    # print(player)
    enemies = get_enemies(game_field)
    player = get_player(game_field)
    coins = get_coins(game_field)
    nearest_coin = find_nearest_coin(coins, player)
    if next_step:
        step = deepcopy(next_step)
        next_step = None
        print("step=", step, "next_step=", next_step)
        return step

    current_move, in_center = move_to_center(game_field, player)

    if in_center:
        print("Moving to coin")
        next_step = turn_right
        return fire
    return current_move
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
