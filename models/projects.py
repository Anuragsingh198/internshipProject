import uuid
from sqlalchemy import Column, String, Date, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from core.database import Base

class Project(Base):
    __tablename__ = "projects"

    project_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_name = Column(String, index=True)
    project_description = Column(String)
    project_owner = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    project_status = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)

    details = relationship("ProjectDetail", back_populates="project")
    history = relationship("ProjectHistory", back_populates="project")


class ProjectDetail(Base):
    __tablename__ = "project_details"

    details_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.project_id"))
    employee_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.role_id"))
    status = Column(String)
    DA = Column(Boolean, default=False)
    AF = Column(Boolean, default=False)
    EA = Column(Boolean, default=False)
    DI = Column(Boolean, default=False)
    approved = Column(String)

    project = relationship("Project", back_populates="details")
    employee = relationship("User", foreign_keys=[employee_id]) 
    role = relationship("Role")  

class ProjectHistory(Base):
    __tablename__ = "project_history"

    history_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.project_id"))
    employee_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.role_id"))  
    start_date = Column(Date)
    end_date = Column(Date)

    project = relationship("Project", back_populates="history")
    employee = relationship("User", foreign_keys=[employee_id])
    role = relationship("Role")

