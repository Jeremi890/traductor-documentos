from abc import ABC, abstractmethod
from typing import List, Optional

class BaseTranslator(ABC):
    """
    Clase base abstracta que define la interfaz común para cualquier proveedor de traducción
    (Patrón Estrategia).
    """

    @abstractmethod
    async def translate_text(self, text: str, source_lang: str, target_lang: str, tone: Optional[str] = "natural") -> str:
        """
        Traduce un único bloque de texto preservando etiquetas de formato interno.
        """
        pass

    @abstractmethod
    async def translate_batch(self, texts: List[str], source_lang: str, target_lang: str, tone: Optional[str] = "natural") -> List[str]:
        """
        Traduce una lista de bloques o párrafos para optimizar las peticiones a la API.
        """
        pass
