import json
import uuid
import asyncio
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, StreamingResponse

from app.core.config import settings
from app.models.translation_job import TranslationJobResponse, JobStatus
from app.services.job_manager import job_manager
from app.services.translators.factory import get_translator
from app.services.parsers.docx_parser import DocxDocumentParser

router = APIRouter(prefix="/translate", tags=["Traducción de Documentos"])

async def run_translation_background(
    task_id: str,
    input_path: Path,
    output_path: Path,
    source_lang: str,
    target_lang: str,
    tone: str
):
    """
    Tarea en segundo plano que coordina el parser y la traducción sin bloquear la API.
    """
    try:
        # Obtener el traductor configurado (Gemini o Mock)
        translator = get_translator()
        
        # Seleccionar el parser adecuado según la extensión
        suffix = input_path.suffix.lower()
        if suffix == ".docx":
            parser = DocxDocumentParser(translator=translator)
        else:
            raise ValueError(f"Extensión no soportada aún: {suffix}")

        async def on_progress(current: int, total: int, msg: str):
            await job_manager.update_progress(task_id, current, total, msg)

        await parser.translate_document(
            input_path=input_path,
            output_path=output_path,
            source_lang=source_lang,
            target_lang=target_lang,
            tone=tone,
            progress_callback=on_progress
        )

        await job_manager.mark_completed(task_id)

    except Exception as e:
        error_text = str(e)
        if "API_KEY_INVALID" in error_text or "400" in error_text:
            error_text = "La clave de Gemini no es válida. Revisa la configuración en ⚙️ Ajustes."
        await job_manager.mark_failed(task_id, error_text)


@router.post("/upload", response_model=TranslationJobResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    source_lang: str = Form("en"),
    target_lang: str = Form("es"),
    tone: str = Form("natural")
):
    """
    Recibe un documento, lo guarda de forma segura e inicia la traducción en segundo plano.
    """
    suffix = Path(file.filename).suffix.lower()
    if suffix not in [".docx"]:
        raise HTTPException(
            status_code=400,
            detail=f"Por ahora se admiten archivos .docx (Word). Archivo recibido: '{file.filename}'"
        )

    task_id = str(uuid.uuid4())
    safe_filename = f"{task_id}_{file.filename}"
    input_path = settings.STORAGE_UPLOADS_DIR / safe_filename
    output_path = settings.STORAGE_PROCESSED_DIR / f"traducido_{safe_filename}"

    # Guardar archivo cargado en disco
    content = await file.read()
    with open(input_path, "wb") as f:
        f.write(content)

    # Registrar tarea
    job = job_manager.create_job(
        task_id=task_id,
        filename=file.filename,
        input_path=input_path,
        output_path=output_path
    )

    # Lanzar procesamiento asíncrono en segundo plano pasando el tono
    background_tasks.add_task(
        run_translation_background,
        task_id=task_id,
        input_path=input_path,
        output_path=output_path,
        source_lang=source_lang,
        target_lang=target_lang,
        tone=tone
    )

    return TranslationJobResponse(
        task_id=task_id,
        filename=file.filename,
        status=job["status"],
        progress=0,
        total_steps=0,
        message="Documento en cola de procesamiento",
        download_url=f"/api/v1/translate/download/{task_id}"
    )


@router.get("/status/{task_id}", response_model=TranslationJobResponse)
async def get_status(task_id: str):
    """
    Consulta el estado y progreso actual de una tarea de traducción.
    """
    job = job_manager.get_job(task_id)
    if not job:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")

    return TranslationJobResponse(
        task_id=task_id,
        filename=job["filename"],
        status=job["status"],
        progress=job["progress"],
        total_steps=job["total_steps"],
        message=job["message"],
        download_url=f"/api/v1/translate/download/{task_id}" if job["status"] == JobStatus.COMPLETED else None,
        error=job["error"]
    )


@router.get("/download/{task_id}")
async def download_translated_file(task_id: str):
    """
    Permite descargar el archivo final traducido cuando el estado es 'completed'.
    """
    job = job_manager.get_job(task_id)
    if not job:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")

    if job["status"] != JobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="El archivo aún no ha terminado de traducirse")

    output_path: Path = job["output_path"]
    if not output_path.exists():
        raise HTTPException(status_code=404, detail="El archivo traducido no se encuentra en el servidor")

    original_name = job["filename"]
    download_filename = f"traducido_{original_name}"

    return FileResponse(
        path=str(output_path),
        filename=download_filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


@router.get("/stream/{task_id}")
async def stream_progress(task_id: str):
    """
    Emite el progreso en tiempo real usando Server-Sent Events (SSE) para la PWA.
    """
    job = job_manager.get_job(task_id)
    if not job:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")

    async def event_generator():
        queue = job_manager.subscribe(task_id)
        try:
            initial_data = {
                "task_id": task_id,
                "status": job["status"].value,
                "progress": job["progress"],
                "total_steps": job["total_steps"],
                "message": job["message"]
            }
            yield f"data: {json.dumps(initial_data)}\n\n"

            while True:
                data = await queue.get()
                yield f"data: {json.dumps(data)}\n\n"
                if data.get("status") in [JobStatus.COMPLETED.value, JobStatus.FAILED.value]:
                    break
        finally:
            job_manager.unsubscribe(task_id, queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
