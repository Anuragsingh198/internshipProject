from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import date, datetime

# ProjectOut schema
class ProjectOut(BaseModel):
    project_id: UUID
    project_name: str
    project_description: Optional[str]
    project_owner: UUID
    project_status: Optional[str]
    DA: bool
    AF: bool
    EA: bool
    DI: bool
    start_date: Optional[date]
    end_date: Optional[date]

    class Config:
        orm_mode = True

# ProjectDetailOut schema
class ProjectDetailsOut(BaseModel):
    details_id: UUID
    project_id: UUID
    employee_id: UUID
    role_id: UUID
    status: str
    manager_approved: bool
    approved_manager: UUID
    admin_approved: bool
    last_edited_on: datetime
    last_edited_by: UUID

    class Config:
        orm_mode = True


# AllprojectsOut schema
class AllProjectsOut(BaseModel):
    projects: List[ProjectOut]

    class Config:
        orm_mode = True

# ProjectUpdate schema
class ProjectDetailUpdate(BaseModel):
    status: Optional[str]
    manager_approved: Optional[bool]
    approved_manager: Optional[UUID]
    admin_approved: Optional[bool]
    role_id: Optional[UUID]
    employee_id: Optional[UUID]
    class Config:
        orm_mode = True
