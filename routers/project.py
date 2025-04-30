from fastapi import APIRouter, Depends, HTTPException, status , Query
from sqlalchemy.orm import Session
from core.database import SessionLocal
from models import projects as project_models
from sqlalchemy.exc import IntegrityError
from schemas import projects as projects_schemas
from uuid import UUID
from  typing import  Optional 
from datetime import datetime
router = APIRouter(prefix="/projects", tags=["Projects"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=projects_schemas.AllProjectsOut)
def get_all_projects(db: Session = Depends(get_db)):
    all_projects = db.query(project_models.Project).all()
    if not all_projects:
        raise HTTPException(status_code=404, detail="Projects not found")
    return {"projects": all_projects}


@router.patch("/update/{detail_id}", response_model=projects_schemas.ProjectDetailsOut)
def update_project_detail(
    detail_id: UUID,
    payload: projects_schemas.ProjectDetailUpdate,
    db: Session = Depends(get_db),
    editor_id: Optional[UUID] = Query(None, description="UUID of the user editing the record")
):
    detail_obj = db.query(project_models.ProjectDetail).filter_by(details_id=detail_id).first()

    if not detail_obj:
        raise HTTPException(status_code=404, detail="Project detail not found")

    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(detail_obj, attr, value)

    detail_obj.last_edited_on = datetime.utcnow()
    
    if editor_id:
        detail_obj.last_edited_by = editor_id

    db.commit()
    db.refresh(detail_obj)
    return detail_obj

@router.put("/delete-project/{project_id}")
def delete_project(project_id: UUID, db: Session = Depends(get_db)):
    # Fetch all related project detail rows
    project_details = db.query(project_models.ProjectDetail).filter_by(project_id=project_id).all()

    if not project_details:
        raise HTTPException(status_code=404, detail="No project details found for this project")

    for detail in project_details:
        detail.status = "Dropped"
        detail.last_edited_on = datetime.utcnow()

    db.commit()
    return {"detail": "All related project details marked as Dropped"}

