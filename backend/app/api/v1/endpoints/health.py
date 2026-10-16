from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/health", tags=["Salud del Sistema"])
async def health_check():
    """
    Endpoint para comprobar que el backend está activo y funcionando.
    """
    return {
        "status": "online",
        "app_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "provider": settings.TRANSLATION_PROVIDER,
        "debug": settings.DEBUG
    }
