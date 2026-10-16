from enum import Enum
from typing import Optional
from pydantic import BaseModel

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TranslationJobResponse(BaseModel):
    task_id: str
    filename: str
    status: JobStatus
    progress: int = 0
    total_steps: int = 0
    message: str = "En cola"
    download_url: Optional[str] = None
    error: Optional[str] = None
