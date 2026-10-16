import sys
from pathlib import Path

# Añadir backend al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from fastapi.testclient import TestClient
from app.main import app

def test_full_api_flow():
    client = TestClient(app)
    
    # 1. Comprobar salud del backend
    print("--- 1. Probando GET /api/v1/health ---")
    resp_health = client.get("/api/v1/health")
    assert resp_health.status_code == 200, f"Error en health check: {resp_health.text}"
    print("Respuesta Health:", resp_health.json())

    # 2. Subir documento de prueba
    print("\n--- 2. Probando POST /api/v1/translate/upload ---")
    test_file_path = Path("storage/uploads/documento_prueba.docx")
    assert test_file_path.exists(), "El archivo de prueba no existe, ejecuta test_docx.py primero"

    with open(test_file_path, "rb") as f:
        resp_upload = client.post(
            "/api/v1/translate/upload",
            files={"file": ("manual_test.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
            data={"source_lang": "es", "target_lang": "en", "tone": "natural"}
        )

    assert resp_upload.status_code == 200, f"Error en upload: {resp_upload.text}"
    data_upload = resp_upload.json()
    task_id = data_upload["task_id"]
    print(f"Documento subido con éxito. Task ID: {task_id}")
    print("Respuesta Upload:", data_upload)

    # 3. Consultar estado de la tarea
    print(f"\n--- 3. Probando GET /api/v1/translate/status/{task_id} ---")
    resp_status = client.get(f"/api/v1/translate/status/{task_id}")
    assert resp_status.status_code == 200
    data_status = resp_status.json()
    print("Estado actual:", data_status)

    # 4. Probar descarga si ya completó
    if data_status["status"] == "completed":
        print(f"\n--- 4. Probando GET /api/v1/translate/download/{task_id} ---")
        resp_download = client.get(f"/api/v1/translate/download/{task_id}")
        assert resp_download.status_code == 200
        print(f"Descarga exitosa, tamaño recibido: {len(resp_download.content)} bytes")

    print("\n¡Flujo completo de la API probado con ÉXITO rotundo!")

if __name__ == "__main__":
    test_full_api_flow()
