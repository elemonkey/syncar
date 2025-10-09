
import enum
from sqlalchemy import Column, Integer, String, DateTime, func, Enum, Text
from .base import Base

class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"

class ImportJob(Base):
    __tablename__ = "import_jobs"

    id = Column(String, primary_key=True, index=True)
    importer_name = Column(String, index=True, nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False)
    log = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)
