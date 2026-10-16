import re
import json
import asyncio
import logging
from typing import List, Optional
from google import genai
from google.genai import types
from app.services.translators.base import BaseTranslator

logger = logging.getLogger(__name__)

class GeminiTranslator(BaseTranslator):
    """
    Proveedor de traducción con Google Gemini (utilizando el SDK oficial google-genai).
    Especializado en mantener contexto amplio, tono estilístico y preservar etiquetas estructurales.
    """

    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        clean_key = api_key.strip() if api_key else ""
        if not clean_key:
            raise ValueError("Se requiere una API Key de Gemini válida para usar GeminiTranslator.")
        self.client = genai.Client(api_key=clean_key)
        self.model_name = model_name

    async def translate_text(self, text: str, source_lang: str, target_lang: str, tone: Optional[str] = "natural") -> str:
        if not text or not text.strip():
            return text

        prompt = (
            f"Eres un traductor profesional y maquetador de documentos.\n"
            f"Traduce el siguiente texto de '{source_lang}' a '{target_lang}'.\n"
            f"Tono deseado: {tone}.\n"
            f"REGLA CRÍTICA: Conserva exactamente todas las etiquetas de marcado interno (ejemplo <r0>, <r1>, <tag>, URLs, números).\n"
            f"Devuelve ÚNICAMENTE el texto traducido, sin notas, ni saludos ni comillas adicionales.\n\n"
            f"Texto a traducir:\n{text}"
        )

        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                )
            )
            if not response.text:
                raise ValueError("La respuesta de Gemini vino vacía.")
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error al traducir con Gemini: {e}")
            raise e

    async def translate_batch(self, texts: List[str], source_lang: str, target_lang: str, tone: Optional[str] = "natural") -> List[str]:
        """
        Traduce una lista de párrafos en un solo viaje de ida y vuelta para máxima eficiencia.
        Si la respuesta JSON tiene algún problema de formato, traduce elemento por elemento.
        """
        if not texts:
            return []

        payload = {str(i): t for i, t in enumerate(texts) if t and t.strip()}
        if not payload:
            return texts

        prompt = (
            f"Eres un traductor profesional de documentos y libros.\n"
            f"Traduce los valores del siguiente objeto JSON de '{source_lang}' a '{target_lang}'.\n"
            f"Tono: {tone}.\n"
            f"REGLAS OBLIGATORIAS:\n"
            f"1. Devuelve un objeto JSON con exactamente las mismas claves numéricas.\n"
            f"2. Conserva intactas todas las etiquetas especiales o de marcado interno como <r0>, <r1>.\n"
            f"3. Responde únicamente con JSON puro, sin bloques markdown ni texto adicional.\n\n"
            f"Objeto a traducir:\n{json.dumps(payload, ensure_ascii=False)}"
        )

        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    response_mime_type="application/json"
                )
            )
            
            raw_text = response.text.strip() if response.text else "{}"
            cleaned_json = re.sub(r"^```(?:json)?\s*", "", raw_text)
            cleaned_json = re.sub(r"\s*```$", "", cleaned_json)

            result_dict = json.loads(cleaned_json)
            
            translated_list = []
            for i, original_text in enumerate(texts):
                key = str(i)
                if key in result_dict and result_dict[key]:
                    translated_list.append(result_dict[key])
                else:
                    translated_list.append(original_text)
            return translated_list

        except Exception as e:
            logger.warning(f"Aviso: Batch JSON falló ({e}). Aplicando fallback párrafo por párrafo...")
            # Fallback seguro: traducir elementos uno a uno.
            # IMPORTANTE: NO silenciar excepciones graves de API (clave inválida, cuota, etc.)
            fallback_results = []
            for text in texts:
                if not text or not text.strip():
                    fallback_results.append(text)
                else:
                    translated = await self.translate_text(text, source_lang, target_lang, tone)
                    fallback_results.append(translated)
            return fallback_results
