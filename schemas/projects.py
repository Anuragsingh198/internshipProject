from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date

class ProjectOut(BaseModel):
    project_id: UUID
    project_name: str
    project_description: Optional[str]
    project_status: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]

    class Config:
        orm_mode = True

class ProjectDetailsOut(BaseModel):
    details_id: UUID
    project_id: UUID
    employee_id: UUID 
    role_id: UUID
    status: str
    DA: bool
    AF: bool
    EA: bool 
    DI: bool 
    approved: str

    project: Optional[ProjectOut]  

    class Config:
        orm_mode = True
