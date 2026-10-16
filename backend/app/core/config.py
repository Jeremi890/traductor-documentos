from pydantic_settings import BaseSettings
from pathlib import Path

# Directorio raíz del backend y proyecto
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
ROOT_DIR = BACKEND_DIR.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "Translatify - Traductor de Documentos"
    VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # Proveedor: "free" (automático sin clave), "gemini" o "mock"
    TRANSLATION_PROVIDER: str = "free"
    GEMINI_API_KEY: str = ""
    
    # Rutas de almacenamiento siempre absolutas
    STORAGE_UPLOADS_DIR: Path = ROOT_DIR / "storage" / "uploads"
    STORAGE_PROCESSED_DIR: Path = ROOT_DIR / "storage" / "processed"

    class Config:
        env_file = str(BACKEND_DIR / ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()

# Garantizar que las rutas apunten siempre a la carpeta del proyecto
settings.STORAGE_UPLOADS_DIR = ROOT_DIR / "storage" / "uploads"
settings.STORAGE_PROCESSED_DIR = ROOT_DIR / "storage" / "processed"
settings.STORAGE_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
settings.STORAGE_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
