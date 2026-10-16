import os
import sys
import uvicorn
from pathlib import Path

# Asegurar que la ruta 'backend' esté en el path de Python
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("   TRANSLATIFY - TRADUCTOR INTELIGENTE DE DOCUMENTOS")
    print("=" * 60)
    print("🌐 Interfaz Web (PWA):        http://127.0.0.1:8000")
    print("📚 Documentación API (Docs):  http://127.0.0.1:8000/docs")
    print("📂 Almacenamiento local:      storage/uploads & storage/processed")
    print("=" * 60)
    print("Presiona Ctrl + C para detener el servidor.\n")

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        app_dir=str(BACKEND_DIR)
    )
