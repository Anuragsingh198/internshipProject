from fastapi import APIRouter, Depends, HTTPException, status , Query
from sqlalchemy.orm import Session
from core.database import SessionLocal
from models import projects as project_models , users as users_model , roles as role_model
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

@router.post("/addNewProjectToUser", response_model=dict)
def add_new_user_to_project(payload: projects_schemas.AddNewUserToProjects, db: Session = Depends(get_db)):

    user = db.query(users_model.User).filter(users_model.User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    manager = db.query(users_model.User).filter(
        users_model.User.is_manager == True,
        users_model.User.id == payload.approved_manager
    ).first()
    if not manager:
        raise HTTPException(status_code=404, detail="Approved manager not found or not a manager.")

    role = db.query(role_model.Role).filter(role_model.Role.role_id == payload.role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found.")

    project = db.query(project_models.Project).filter(project_models.Project.project_id == payload.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    new_detail = project_models.ProjectDetail(
        project_id=payload.project_id,
        employee_id=user.id,
        role_id=payload.role_id,
        status=payload.status,
        manager_approved=payload.manager_approved,
        approved_manager=payload.approved_manager,
        admin_approved=payload.admin_approved,
        last_edited_on=datetime.utcnow(),
        last_edited_by=payload.approved_manager,
    )

    db.add(new_detail)
    db.commit()
    db.refresh(new_detail)

    response = {
        "message": "User successfully added to project.",
        "project_details": {
            "details_id": new_detail.details_id,
            "project_id": new_detail.project_id,
            "user_id": user.id,
            "employee_id": user.emp_id,
            "employee_firstname": user.first_name,
            "employee_lastname": user.last_name,
            "employee_email": user.email,
            "role_id": role.role_id,
            "role_name": role.role_name,
            "status": new_detail.status,
            "manager_approved": new_detail.manager_approved,
            "approved_manager": manager.id,
            "manager_name": f"{manager.first_name} {manager.last_name}",
            "manager_email": manager.email,
            "admin_approved": new_detail.admin_approved,
            "remark": new_detail.remark,
            "last_edited_on": new_detail.last_edited_on,
            "last_edited_by": new_detail.last_edited_by,
        }
    }

    return response



    
    




@router.put("/delete-project/{project_id}")
def delete_project(project_id: UUID, db: Session = Depends(get_db)):
    project_details = db.query(project_models.ProjectDetail).filter_by(project_id=project_id).all()
    if not project_details:
        raise HTTPException(status_code=404, detail="No project details found for this project")

    for detail in project_details:
        detail.status = "Dropped"
        detail.last_edited_on = datetime.utcnow()
    db.commit()
    return {"detail": "All related project details marked as Dropped"}


