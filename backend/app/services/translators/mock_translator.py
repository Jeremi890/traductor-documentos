import asyncio
from typing import List, Optional
from app.services.translators.base import BaseTranslator

class MockTranslator(BaseTranslator):
    """
    Traductor simulado para desarrollo local y pruebas sin gastar cuota de API.
    Añade un prefijo con el idioma destino y simula una latencia realista.
    """

    async def translate_text(self, text: str, source_lang: str, target_lang: str, tone: Optional[str] = "natural") -> str:
        if not text or not text.strip():
            return text
        # Simula un pequeño retraso de red
        await asyncio.sleep(0.05)
        return f"[{target_lang.upper()}] {text}"

    async def translate_batch(self, texts: List[str], source_lang: str, target_lang: str, tone: Optional[str] = "natural") -> List[str]:
        if not texts:
            return []
        # Simular procesamiento por lotes
        await asyncio.sleep(0.2)
        translated = []
        for text in texts:
            if not text or not text.strip():
                translated.append(text)
            else:
                translated.append(f"[{target_lang.upper()}] {text}")
        return translated
