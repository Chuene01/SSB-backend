from fastapi import APIRouter

router = APIRouter()

@router.post("/start")
def start_bot():
    return {"status": "started"}

@router.post("/stop")
def stop_bot():
    return {"status": "stopped"}

@router.get("/status")
def bot_status():
    return {"running": False}
