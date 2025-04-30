import uuid
import enum
from datetime import datetime
from sqlalchemy import (
    Column, String, Date, Boolean, ForeignKey, Enum, DateTime
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from core.database import Base


class ProjectStatusEnum(enum.Enum):
    ongoing = "ongoing"
    completed = "completed"
    hold = "hold"
    dropped = "dropped"


class Project(Base):
    __tablename__ = "projects"

    project_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_name = Column(String, index=True, nullable=False)
    project_description = Column(String)
    project_owner = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_status = Column(Enum(ProjectStatusEnum), nullable=False)

    DA = Column(Boolean, default=False)
    AF = Column(Boolean, default=False)
    EA = Column(Boolean, default=False)
    DI = Column(Boolean, default=False)

    start_date = Column(Date)
    end_date = Column(Date)

    details = relationship("ProjectDetail", back_populates="project")
    history = relationship("ProjectHistory", back_populates="project")


class ProjectDetail(Base):
    __tablename__ = "project_details"

    details_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.project_id"), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.role_id"), nullable=False)

    status = Column(String)
    manager_approved = Column(Boolean, default=False)
    approved_manager = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    admin_approved = Column(Boolean, default=False)

    last_edited_on = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_edited_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    project = relationship("Project", back_populates="details")
    employee = relationship("User", foreign_keys=[employee_id])
    role = relationship("Role")
    manager = relationship("User", foreign_keys=[approved_manager])
    editor = relationship("User", foreign_keys=[last_edited_by])


class ProjectHistory(Base):
    __tablename__ = "project_history"

    history_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.project_id"), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.role_id"), nullable=False)

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    project = relationship("Project", back_populates="history")
    employee = relationship("User", foreign_keys=[employee_id])
    role = relationship("Role")
