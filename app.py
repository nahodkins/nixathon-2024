from fastapi import FastAPI
from models import *
import random


app = FastAPI()

@app.get('/healthz')
async def status_dict():
    return {"status": "OK"}


@app.post('/move')
async def make_move(game_field: GameField) -> MoveResponse:
    move = random.choice(list(MoveCommand))
    return MoveResponse(move=move)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
