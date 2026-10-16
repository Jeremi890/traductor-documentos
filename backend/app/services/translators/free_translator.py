import re
import asyncio
import logging
from typing import List, Optional
from deep_translator import MyMemoryTranslator
from app.services.translators.base import BaseTranslator

logger = logging.getLogger(__name__)

LANG_MAP = {
    "en": "english",
    "es": "spanish",
    "fr": "french",
    "de": "german",
    "it": "italian",
    "pt": "portuguese"
}

class FreeTranslator(BaseTranslator):
    """
    Proveedor de traducción gratuito y automático (sin necesidad de API Key).
    Utiliza el motor de MyMemory para traducciones inmediatas a costo cero.
    """

    async def translate_text(self, text: str, source_lang: str, target_lang: str, tone: Optional[str] = "natural") -> str:
        if not text or not text.strip():
            return text

        src = LANG_MAP.get(source_lang.lower(), source_lang)
        tgt = LANG_MAP.get(target_lang.lower(), target_lang)

        # Si el texto contiene etiquetas de runs <r0>...</r0>, traducimos cada parte preservando los tags
        tag_pattern = re.compile(r"(<r\d+>)(.*?)(</r\d+>)", re.DOTALL)
        
        def translate_match(match):
            open_tag = match.group(1)
            inner_text = match.group(2)
            close_tag = match.group(3)
            if not inner_text.strip():
                return f"{open_tag}{inner_text}{close_tag}"
            try:
                translated_inner = MyMemoryTranslator(source=src, target=tgt).translate(inner_text)
                return f"{open_tag}{translated_inner}{close_tag}"
            except Exception:
                return f"{open_tag}{inner_text}{close_tag}"

        if tag_pattern.search(text):
            return tag_pattern.sub(translate_match, text)

        # Texto normal sin tags internos
        try:
            return await asyncio.to_thread(
                MyMemoryTranslator(source=src, target=tgt).translate,
                text
            )
        except Exception as e:
            logger.error(f"Error en traducción gratuita: {e}")
            return text

    async def translate_batch(self, texts: List[str], source_lang: str, target_lang: str, tone: Optional[str] = "natural") -> List[str]:
        results = []
        for text in texts:
            res = await self.translate_text(text, source_lang, target_lang, tone)
            results.append(res)
        return results
