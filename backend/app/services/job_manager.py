import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from app.models.translation_job import JobStatus

class JobManager:
    """
    Administrador en memoria de las tareas de traducción activas.
    Permite consultar el estado y emitir eventos en tiempo real.
    """
    def __init__(self):
        self._jobs: Dict[str, Dict[str, Any]] = {}
        self._listeners: Dict[str, list[asyncio.Queue]] = {}

    def create_job(self, task_id: str, filename: str, input_path: Path, output_path: Path) -> dict:
        job = {
            "task_id": task_id,
            "filename": filename,
            "input_path": input_path,
            "output_path": output_path,
            "status": JobStatus.PENDING,
            "progress": 0,
            "total_steps": 0,
            "message": "Archivo recibido, esperando procesamiento...",
            "error": None
        }
        self._jobs[task_id] = job
        self._listeners[task_id] = []
        return job

    def get_job(self, task_id: str) -> Optional[dict]:
        return self._jobs.get(task_id)

    async def update_progress(self, task_id: str, current: int, total: int, message: str):
        if task_id in self._jobs:
            self._jobs[task_id]["progress"] = current
            self._jobs[task_id]["total_steps"] = total
            self._jobs[task_id]["message"] = message
            self._jobs[task_id]["status"] = JobStatus.PROCESSING

            # Notificar a los escuchas conectados por SSE
            event_data = {
                "task_id": task_id,
                "status": JobStatus.PROCESSING.value,
                "progress": current,
                "total_steps": total,
                "message": message
            }
            await self._broadcast(task_id, event_data)

    async def mark_completed(self, task_id: str):
        if task_id in self._jobs:
            self._jobs[task_id]["status"] = JobStatus.COMPLETED
            self._jobs[task_id]["message"] = "Traducción completada con éxito."
            event_data = {
                "task_id": task_id,
                "status": JobStatus.COMPLETED.value,
                "progress": self._jobs[task_id]["total_steps"],
                "total_steps": self._jobs[task_id]["total_steps"],
                "message": "Traducción completada con éxito."
            }
            await self._broadcast(task_id, event_data)

    async def mark_failed(self, task_id: str, error_msg: str):
        if task_id in self._jobs:
            self._jobs[task_id]["status"] = JobStatus.FAILED
            self._jobs[task_id]["error"] = error_msg
            self._jobs[task_id]["message"] = f"Error: {error_msg}"
            event_data = {
                "task_id": task_id,
                "status": JobStatus.FAILED.value,
                "error": error_msg,
                "message": f"Error: {error_msg}"
            }
            await self._broadcast(task_id, event_data)

    def subscribe(self, task_id: str) -> asyncio.Queue:
        queue = asyncio.Queue()
        if task_id not in self._listeners:
            self._listeners[task_id] = []
        self._listeners[task_id].append(queue)
        return queue

    def unsubscribe(self, task_id: str, queue: asyncio.Queue):
        if task_id in self._listeners and queue in self._listeners[task_id]:
            self._listeners[task_id].remove(queue)

    async def _broadcast(self, task_id: str, data: dict):
        if task_id in self._listeners:
            for queue in self._listeners[task_id]:
                await queue.put(data)

job_manager = JobManager()
