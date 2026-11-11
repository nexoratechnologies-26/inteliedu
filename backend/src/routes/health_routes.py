from fastapi import APIRouter
from src.controllers.health_controller import get_health

router = APIRouter(prefix="/api/v1", tags=["Health"])


@router.get("/health")
def health():
    return get_health()
