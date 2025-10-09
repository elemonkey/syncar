from sqlalchemy.orm import Session
from typing import Optional
from app.models.import_job import ImportJob, JobStatus
from app.schemas.import_job import ImportJobCreate, ImportJobUpdate

def get_import_job(db: Session, job_id: str) -> Optional[ImportJob]:
    return db.query(ImportJob).filter(ImportJob.id == job_id).first()

def create_import_job(db: Session, job: ImportJobCreate) -> ImportJob:
    db_job = ImportJob(**job.model_dump(), status=JobStatus.PENDING)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def update_import_job(db: Session, job_id: str, job_update: ImportJobUpdate) -> Optional[ImportJob]:
    db_job = get_import_job(db, job_id)
    if db_job:
        update_data = job_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_job, key, value)
        db.commit()
        db.refresh(db_job)
    return db_job