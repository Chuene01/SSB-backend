from fastapi import FastAPI
from app.api import signal, bot

app = FastAPI(title="Bot backend")

app.include_router(signal.router, prefix="/signal")
app.include_router(bot.router, prefix="/bot")

@app.get("/")
def health():
    return {"status": "running"}
