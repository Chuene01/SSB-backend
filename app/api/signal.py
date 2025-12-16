from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_signal():
    return {"status": "ok"}
