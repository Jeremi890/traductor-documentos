from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, Awaitable, Optional
from app.services.translators.base import BaseTranslator

class BaseDocumentParser(ABC):
    """
    Clase base para procesar diferentes tipos de documentos (.docx, .pdf, .epub).
    Extrae el texto, coordina la traducción y reconstruye el archivo final.
    """

    def __init__(self, translator: BaseTranslator):
        self.translator = translator

    @abstractmethod
    async def translate_document(
        self,
        input_path: Path,
        output_path: Path,
        source_lang: str,
        target_lang: str,
        tone: Optional[str] = "natural",
        progress_callback: Optional[Callable[[int, int, str], Awaitable[None]]] = None
    ) -> Path:
        """
        Lee el archivo de entrada, traduce su contenido preservando diseño y guarda en output_path.
        progress_callback(current_step, total_steps, message) emite progreso para la PWA.
        """
        pass
