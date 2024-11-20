from fastapi import FastAPI
from models import *

app = FastAPI()

@app.get('/healthz')
async def status_dict():
    return {"status": "OK"}


@app.get('/healthz-model')
async def status_model():
    response = HealthCheckResponse(status="OK")
    return response


@app.post('/message')
async def create_message(message: MessageModel):
    message.created = True
    return message

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
