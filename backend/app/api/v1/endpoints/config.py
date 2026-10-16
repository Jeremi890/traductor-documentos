from pathlib import Path
from pydantic import BaseModel
from typing import Optional
from fastapi import APIRouter, HTTPException
from app.core.config import settings, BACKEND_DIR
from app.services.translators.gemini_translator import GeminiTranslator

router = APIRouter(prefix="/config", tags=["Configuración"])

class ConfigUpdateRequest(BaseModel):
    provider: str
    gemini_api_key: Optional[str] = None

class ConfigResponse(BaseModel):
    provider: str
    has_gemini_key: bool
    masked_key: Optional[str] = None

@router.get("", response_model=ConfigResponse)
async def get_config():
    """
    Obtiene la configuración actual del proveedor de traducción.
    """
    key = settings.GEMINI_API_KEY
    masked = f"{key[:4]}...{key[-4:]}" if key and len(key) >= 8 else ("Configurada" if key else None)
    return ConfigResponse(
        provider=settings.TRANSLATION_PROVIDER,
        has_gemini_key=bool(settings.GEMINI_API_KEY),
        masked_key=masked
    )

@router.post("", response_model=ConfigResponse)
async def update_config(data: ConfigUpdateRequest):
    """
    Valida y actualiza el proveedor y la clave de Gemini en memoria y en el archivo .env.
    Opciones válidas: 'free', 'gemini', 'mock'.
    """
    provider = data.provider.lower().strip()
    if provider not in ["free", "gemini", "mock"]:
        raise HTTPException(status_code=400, detail="Proveedor no válido. Usa 'free', 'gemini' o 'mock'.")

    if provider == "gemini":
        new_key = data.gemini_api_key.strip() if data.gemini_api_key else settings.GEMINI_API_KEY
        if not new_key:
            raise HTTPException(
                status_code=400,
                detail="Debes ingresar una clave de API de Gemini."
            )

        # Validación en vivo con Google
        try:
            tester = GeminiTranslator(api_key=new_key)
            await tester.translate_text("Hello", "en", "es", "natural")
        except Exception as e:
            err_text = str(e)
            if "ACCESS_TOKEN_TYPE_UNSUPPORTED" in err_text or "API_KEY_INVALID" in err_text:
                raise HTTPException(
                    status_code=400,
                    detail="Google rechazó esta clave con ACCESS_TOKEN_TYPE_UNSUPPORTED. Esto ocurre cuando el proyecto en Google Cloud no tiene habilitada la API de Gemini. Te sugerimos usar la opción 'Automático Gratuito' o crear la clave en un 'Proyecto Nuevo' en Google AI Studio."
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error al verificar con Google: {err_text}"
                )

        settings.GEMINI_API_KEY = new_key
        settings.TRANSLATION_PROVIDER = "gemini"
        
    elif provider == "free":
        settings.TRANSLATION_PROVIDER = "free"
        
    else:
        settings.TRANSLATION_PROVIDER = "mock"

    # Persistir en backend/.env
    env_path = BACKEND_DIR / ".env"
    try:
        content = (
            f"# Configuración del Servidor\n"
            f"PORT={settings.PORT}\n"
            f"HOST={settings.HOST}\n"
            f"DEBUG={settings.DEBUG}\n\n"
            f"# Proveedor de Traducción: 'free', 'gemini' o 'mock'\n"
            f"TRANSLATION_PROVIDER={settings.TRANSLATION_PROVIDER}\n\n"
            f"# Clave de API de Google Gemini (Gratis en https://aistudio.google.com/)\n"
            f"GEMINI_API_KEY={settings.GEMINI_API_KEY}\n"
        )
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception:
        pass

    key = settings.GEMINI_API_KEY
    masked = f"{key[:4]}...{key[-4:]}" if key and len(key) >= 8 else ("Configurada" if key else None)
    return ConfigResponse(
        provider=settings.TRANSLATION_PROVIDER,
        has_gemini_key=bool(settings.GEMINI_API_KEY),
        masked_key=masked
    )
