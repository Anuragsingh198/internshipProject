from fastapi import APIRouter, Depends, HTTPException, status , Query , Request
from sqlalchemy.orm import Session
from core.database import SessionLocal
from models import projects as project_models , users as users_model , roles as role_model
from sqlalchemy.exc import IntegrityError
from schemas import projects as projects_schemas
from SendEmail import send_email
from uuid import UUID
import uuid
from math import ceil
from  typing import  Optional 
from datetime import datetime
from auth.getCurrUser import get_current_user
from   sqlalchemy  import  asc
router = APIRouter(prefix="/projects", tags=["Projects"])
from utils.email_templates import  user_account_created_template , manager_request_user_assignment_template
# from models.projects import ProjectDetailsStatusEnum , ProjectStatusEnum

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/addNewProject" , response_model=projects_schemas.AddProjectResponse)
def create_new_project( request: Request, payload: projects_schemas.AddNewProjects, db: Session = Depends(get_db)):
     
    admin_id = request.state.user_id
    user = db.query(users_model.User).filter_by(id=admin_id).first()
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Only admin can add   the  project.")
    

    users =  db.query(users_model.User).filter_by(users_model.User.id == payload.project_owner).first()
    if not users:
        raise HTTPException(status_code=404 , detail="assigned  manager  not  exists")
    
    new_project = project_models.Project(
        project_id=uuid.uuid4(),
        project_name=payload.project_name,
        project_description=payload.project_description,
        project_owner=payload.project_owner,
        project_status=payload.project_status,
        start_date=payload.start_date,
        end_date=payload.end_date,
        edited_by = f"{user.first_name} {user.last_name}",
        edited_on=datetime.utcnow(),
        DA=payload.DA,
        AF=payload.AF,
        EA=payload.EA,
        DI=payload.DI,
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    # send_email(
    #     recipient_email=users.email,
    #     description=f"\n You have been  Assigned new proejct \n Project Name: {payload.project_name} \n you will be  handeling  this  project\n Project  Duration  is  from {payload.start_date} to {payload.end_date}\nThank you!\nTeam Ielektron"
    # )
    return {
        "message": "Project created successfully!",
    }

@router.get("/", response_model=projects_schemas.AllProjectsOut)
def get_all_projects(
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db),
    current_user: users_model.User = Depends(get_current_user)
):
    if not  current_user:
        raise HTTPException(status_code=403, detail="login  please")
    limit = 10
    offset = (page - 1) * limit

    total_count = db.query(project_models.Project).count()
    total_page_count = ceil(total_count / limit)

    all_projects = db.query(
    project_models.Project,
    users_model.User.first_name,
    users_model.User.last_name
).join(
    users_model.User, project_models.Project.project_owner == users_model.User.id
).order_by(
    asc(project_models.Project.project_name)
).offset(offset).limit(limit).all()


    if not all_projects:
        raise HTTPException(status_code=404, detail="Projects not found")

    projects_out = []
    for project, first_name, last_name in all_projects:
        projects_out.append({
            "project_id": project.project_id,
            "project_name": project.project_name,
            "project_description": project.project_description,
            "project_owner": project.project_owner,
            "manager_firstname": first_name,
            "manager_lastname": last_name,
            "project_status": project.project_status,
            "DA": project.DA,
            "AF": project.AF,
            "EA": project.EA,
            "DI": project.DI,
            "edited_by":project.edited_by,
            "edited_on":project.edited_on,
            "start_date": project.start_date,
            "end_date": project.end_date
        })
    return {
        "projects": projects_out,
        "pagination": {
            "total_count": total_count,
            "total_pages": total_page_count,
            "current_page": page,
            "per_page": limit
        }
    }

@router.patch("/update/{detail_id}", response_model=projects_schemas.ProjectDetailsOut)
def update_project_detail(
    detail_id: UUID,
    payload: projects_schemas.ProjectDetailUpdate,
    db: Session = Depends(get_db),
   current_user: users_model.User = Depends(get_current_user)
):
    detail_obj = db.query(project_models.ProjectDetail).filter_by(details_id=detail_id).first()
    
    if not current_user:
        raise HTTPException(status_code=403 , detail="No  Login  User  Found")
    if not  current_user.is_admin or current_user.is_manager:
        raise HTTPException(status_code=403 , detail="Only   Admin or manager Can  Perform  this action")

    if not detail_obj:
        raise HTTPException(status_code=404, detail="Project detail not found")

    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(detail_obj, attr, value)

    detail_obj.last_edited_on = datetime.utcnow()
    detail_obj.last_edited_by = payload.approved_manager

    db.commit()
    db.refresh(detail_obj)
    return detail_obj


@router.post("/addNewProjectToUser", response_model=dict)
def add_new_user_to_project(payload: projects_schemas.AddNewUserToProjects,current_user: users_model.User = Depends(get_current_user), db: Session = Depends(get_db)):

    if not current_user:
        raise HTTPException(status_code=403 , detail="No  Login  User  Found")
    if  not  current_user.is_admin or current_user.is_manager:
        raise HTTPException(status_code=403 , detail="Only   Admin or manager Can  Perform  this action")

    user = db.query(users_model.User).filter(users_model.User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    admin_obj = db.query(users_model.User).filter_by(is_admin=True).first()
    if not admin_obj:
        raise HTTPException(status_code=404, detail="No admin is there for  approval not found.")
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
    
   
    email_html = manager_request_user_assignment_template(
        admin= f"{admin_obj.first_name} {admin_obj.last_name}",
        manager=f"{manager.first_name} {manager.last_name}",
        user=f"{user.first_name} {user.last_name}",
        role=role.role_name,
        users=user,
        project=project.project_name
    )

    send_email(
        # recipient_email=admin_obj.email,
        recipient_email="anuragsingh.bisen@ielektron.com",
        description=email_html
    )

    response = {
        "message": "User successfully added to project.",
        "project_details": {
            "details_id": new_detail.details_id,
            "project_id": new_detail.project_id,
            "project_name":project.project_name,
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


@router.patch("/update-project/{project_id}")
def update_project(project_id: UUID, payload: projects_schemas.ProjectUpdate,current_user: users_model.User = Depends(get_current_user),  db: Session = Depends(get_db)):
    if not current_user:
        raise HTTPException(status_code=403 , detail="No  Login  User  Found")
    if  not current_user.is_admin  :
        raise HTTPException(status_code=403 , detail="Only   Admin or manager Can  Perform  this action")
    
    project = db.query(project_models.Project).filter(project_models.Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    old_owner = project.project_owner
    owner_changed = False

    if payload.project_owner and payload.project_owner != old_owner:
        owner_changed = True
        project.project_owner = payload.project_owner

    if payload.project_name:
        project.project_name = payload.project_name
    if payload.project_description:
        project.project_description = payload.project_description
    if payload.project_status:
        project.project_status = payload.project_status
    if payload.start_date:
        project.start_date = payload.start_date
    if payload.end_date:
        project.end_date = payload.end_date

    if owner_changed:
        project_details = db.query(project_models.ProjectDetail).filter(project_models.ProjectDetail.project_id == project_id).all()
        for detail in project_details:
            detail.approved_manager = payload.project_owner
    history = project_models.ProjectHistory(
                project_id=project.project_id,
                employee_id=old_owner.id,
                # role_id=detail.role_id,
                start_date=project.start_date,
                end_date=datetime.utcnow()
            )
    project.edited_by = f"{current_user.first_name} {current_user.last_name}"
    project.edited_on= datetime.utcnow()
    db.add(history)       
    db.commit()
    db.refresh(project)
    return {"message": "Project updated successfully"}

@router.get("/delete-project/{project_id}")
def delete_project(project_id: UUID,current_user: users_model.User = Depends(get_current_user), db: Session = Depends(get_db)):

    if not current_user:
        raise HTTPException(status_code=403 , detail="No  Login  User  Found")
    if  not current_user.is_admin:
        raise HTTPException(status_code=403 , detail="Only   Admin or manager Can  Perform  this action")

    project = db.query(project_models.Project).filter(project_models.Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    manager = db.query(users_model.User).filter(users_model.User.id == project.project_owner).first()
    if not manager:
        raise HTTPException(status_code=404, detail="No project owner found for this project")

    project.project_status = "dropped"
    project_details = db.query(project_models.ProjectDetail).filter(project_models.ProjectDetail.project_id == project_id).all()
    if  project_details:
        for detail in project_details:
            detail.status = "Dropped"
            detail.last_edited_on = datetime.utcnow()
    history = project_models.ProjectHistory(
            project_id=project_id,
            employee_id=manager.id,
            # role_id=detail.role_id,
            start_date=project.start_date,
            end_date=datetime.utcnow()
        )
    db.add(history)   

    db.commit()
    send_email(
        recipient_email=manager.email,
        description=f"\nCurrent project {project.project_name} has been dropped by admin.\n\nThank you!\nTeam Ielektron"
    )
    return {"detail": "Project marked as dropped, all related details updated, and history recorded"}



