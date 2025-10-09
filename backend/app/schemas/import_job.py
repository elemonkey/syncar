from pydantic import BaseModel
from datetime import datetime
from app.models.import_job import JobStatus
from typing import Optional

class ImportJobBase(BaseModel):
    importer_name: str

class ImportJobCreate(ImportJobBase):
    id: str

class ImportJobUpdate(BaseModel):
    status: JobStatus
    log: Optional[str] = None

class ImportJob(ImportJobBase):
    id: str
    status: JobStatus
    log: Optional[str] = None
    created_at: datetime
    finished_at: Optional[datetime] = None

    class Config:
        from_attributes = True