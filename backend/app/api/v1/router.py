from fastapi import APIRouter
from app.api.v1.endpoints import health, translation, config

api_router = APIRouter()
api_router.include_router(health.router, prefix="", tags=["Salud del Sistema"])
api_router.include_router(translation.router, prefix="", tags=["Traducción de Documentos"])
api_router.include_router(config.router, prefix="", tags=["Configuración"])
