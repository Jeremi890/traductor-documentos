from app.core.config import settings
from app.services.translators.base import BaseTranslator
from app.services.translators.mock_translator import MockTranslator
from app.services.translators.gemini_translator import GeminiTranslator
from app.services.translators.free_translator import FreeTranslator

def get_translator() -> BaseTranslator:
    """
    Fábrica (Factory) que devuelve la instancia del proveedor de traducción configurado.
    Opciones: 'free' (Automático gratuito sin clave), 'gemini' (IA Gemini), 'mock' (Pruebas).
    """
    provider = settings.TRANSLATION_PROVIDER.lower().strip()
    
    if provider == "free":
        return FreeTranslator()
        
    elif provider == "gemini":
        if not settings.GEMINI_API_KEY:
            raise ValueError(
                "TRANSLATION_PROVIDER está configurado como 'gemini', pero GEMINI_API_KEY está vacía en backend/.env. "
                "Configura tu clave o cambia el proveedor a 'free'."
            )
        return GeminiTranslator(api_key=settings.GEMINI_API_KEY)
        
    elif provider == "mock":
        return MockTranslator()
        
    else:
        # Por defecto usar traductor gratuito
        return FreeTranslator()
