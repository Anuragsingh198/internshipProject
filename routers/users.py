from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import SessionLocal
from models import users as user_models, projects 
from models.roles import Role
from schemas import users as user_schemas , projects as project_scjemas
from sqlalchemy.exc import IntegrityError
import hashlib
from auth.jwthandler import create_access_token
from datetime import timedelta
from uuid import UUID
import uuid
from datetime import datetime

from utils.hash import hash_password , verify_password
router = APIRouter(prefix="/users", tags=["Users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@router.post("/signup", response_model=dict)
def signup(user_data: user_schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(user_models.User).filter(
        (user_models.User.email == user_data.email) | (user_models.User.emp_id == user_data.emp_id)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = hash_password(user_data.password)

    new_user = user_models.User(
        id=uuid.uuid4(),
        emp_id=user_data.emp_id,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        username=f"{user_data.first_name[0]}{user_data.last_name[-1]}{user_data.emp_id}",
        email=user_data.email,
        password=hashed_password,
        is_active=True,
        is_manager=False,
        is_admin=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(data={"sub": str(new_user.id)})

    return {
        "detail": "User created successfully",
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_schemas.UserOut.from_orm(new_user)
    }

@router.post("/login", response_model=user_schemas.LoginResponse)
def login_user(email: str, password: str, db: Session = Depends(get_db)):
    user_obj = db.query(user_models.User).filter_by(email=email).first()

    if not user_obj or not verify_password(password, user_obj.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        data={"sub": str(user_obj.id)},
        expires_delta=timedelta(minutes=60)
    )

    project_details = db.query(projects.ProjectDetail).filter_by(employee_id=user_obj.id).all()

    return {
        "status" : "success",
        "user": user_schemas.UserOut.from_orm(user_obj),
        "projects": [user_schemas.ProjectDetailOut.from_orm(p) for p in project_details],
        "access_token": access_token,
        "token_type": "bearer"
    }
@router.get('/getAllUsers', response_model=user_schemas.AllUsers)
def getusers(db: Session = Depends(get_db)):
    allUsers_obj = db.query(user_models.User).filter(
        (user_models.User.is_manager == False) & 
        (user_models.User.is_admin == False)
    ).all()
    
    if not allUsers_obj:
        raise HTTPException(status_code=404, detail="No users found")
    
    return {"allusers": allUsers_obj}



@router.get("/manager", response_model=user_schemas.Managers)
def get_managers(db: Session = Depends(get_db)):
    manage_obj = db.query(user_models.User).filter_by(is_manager=True).all()
    if not manage_obj:
        raise HTTPException(status_code=404, detail="No managers found")

    return {"managers": manage_obj}

@router.put("/update-user/{user_id}", response_model=user_schemas.UserOut)
def update_user(user_id: UUID, user_data: user_schemas.UserOut, db: Session = Depends(get_db)):
    user_obj = db.query(user_models.User).filter_by(id=user_id).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")

    for attr, value in user_data.dict(exclude_unset=True).items():
        setattr(user_obj, attr, value)
    
    db.commit()
    db.refresh(user_obj)
    return user_obj



@router.put("/delete-user/{user_id}")
def deactivate_user(user_id: UUID, db: Session = Depends(get_db)):
    user_obj = db.query(user_models.User).filter_by(id=user_id).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")

    user_obj.is_active = False
    db.commit()
    return {"detail": "User deactivated successfully"}

@router.post("/reset-password")
def reset_user_password(email:str, newpassword:str, db:Session =  Depends(get_db)):
    user_obj = db.query(user_models.User).filter(user_models.User.email == email).first()

    if not  user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    # hashed_password = hashlib.sha256(payload.new_password.encode()).hexdigest()
    # user_obj.password = hashed_password
    user_obj.password = newpassword
    db.commit()
    db.refresh(user_obj)
    return {"detail":"user passweord   has  changed  successfully"}

@router.get("/Approved/new-user-request/{user_id}", response_model=project_scjemas.allProjectOut)
def get_Approved_users(user_id: UUID, db: Session = Depends(get_db)):
    manageroradmin = db.query(user_models.User).filter(user_models.User.id == user_id).first()
    if not manageroradmin:
        raise HTTPException(status_code=404, detail="Current user not found")

    # Base query: only fully approved projects
    approved_projects = db.query(projects.ProjectDetail).filter(
        projects.ProjectDetail.manager_approved == True,
        projects.ProjectDetail.admin_approved == True
    )

    if manageroradmin.is_manager:
        approved_projects = approved_projects.filter(
            projects.ProjectDetail.approved_manager == user_id
        )

    approved_projects = approved_projects.all()

    allProjectsout = []
    for proj in approved_projects:
        one_user = db.query(user_models.User).filter(user_models.User.id == proj.employee_id).first()
        one_role = db.query(Role).filter(Role.role_id == proj.role_id).first()
        approved_manager = db.query(user_models.User).filter(user_models.User.id == proj.approved_manager).first()

        if one_user and one_role and approved_manager:
            outOneProject = {
                "details_id": proj.details_id,
                "project_id": proj.project_id,
                "user_id": one_user.id,
                "employee_id": one_user.emp_id,
                "employee_firstname": one_user.first_name,
                "employee_lastname": one_user.last_name,
                "employee_email": one_user.email,
                "role_id": one_role.role_id,
                "role_name": one_role.role_name,
                "status": proj.status,
                "manager_approved": proj.manager_approved,
                "approved_manager": proj.approved_manager,
                "manager_name": f"{approved_manager.first_name} {approved_manager.last_name}",
                "manager_email": approved_manager.email,
                "admin_approved": proj.admin_approved,
                "remark": proj.remark,
                "last_edited_on": proj.last_edited_on,
                "last_edited_by": proj.last_edited_by
            }
            allProjectsout.append(outOneProject)

    return {"allProjects": allProjectsout}

@router.get("/notApproved/new-user-request/{user_id}", response_model=project_scjemas.allProjectOut)
def get_notApproved_users(user_id: UUID, db: Session = Depends(get_db)):
    manageroradmin = db.query(user_models.User).filter(user_models.User.id == user_id).first()
    if not manageroradmin:
        raise HTTPException(status_code=404, detail="Current user not found")

    notApproved_projects = db.query(projects.ProjectDetail).filter(
        projects.ProjectDetail.manager_approved == True,
        projects.ProjectDetail.admin_approved == False
    )

    if manageroradmin.is_manager:
        notApproved_projects = notApproved_projects.filter(
            projects.ProjectDetail.approved_manager == user_id
        )

    notApproved_projects = notApproved_projects.all()

    allProjectsout = []
    for proj in notApproved_projects:
        one_user = db.query(user_models.User).filter(user_models.User.id == proj.employee_id).first()
        one_role = db.query(Role).filter(Role.role_id == proj.role_id).first()
        approved_manager = db.query(user_models.User).filter(user_models.User.id == proj.approved_manager).first()

        if one_user and one_role and approved_manager:
            outOneProject = {
                "details_id": proj.details_id,
                "project_id": proj.project_id,
                "user_id": one_user.id,
                "employee_id": one_user.emp_id,
                "employee_firstname": one_user.first_name,
                "employee_lastname": one_user.last_name,
                "employee_email": one_user.email,
                "role_id": one_role.role_id,
                "role_name": one_role.role_name,
                "status": proj.status,
                "manager_approved": proj.manager_approved,
                "approved_manager": proj.approved_manager,
                "manager_name": f"{approved_manager.first_name} {approved_manager.last_name}",
                "manager_email": approved_manager.email,
                "admin_approved": proj.admin_approved,
                "remark": proj.remark,
                "last_edited_on": proj.last_edited_on,
                "last_edited_by": proj.last_edited_by
            }
            allProjectsout.append(outOneProject)

    return {"allProjects": allProjectsout}



# @router.post("/manager/approve-user")
# def approve_user_by_manager(
#     payload: user_schemas.ApproveUserRequest,
#     db: Session = Depends(get_db),
# ):
#     current_user = db.query(user_models.User).filter_by(id=payload.user_id).first()

#     if not current_user:
#         raise HTTPException(status_code=404, detail="User not found")

#     if not current_user.is_manager:
#         raise HTTPException(status_code=403, detail="Only managers can perform this action")

#     detail = db.query(projects.ProjectDetail).filter_by(
#         employee_id=payload.employee_id,
#         project_id=payload.project_id
#     ).first()

#     if not detail:
#         raise HTTPException(status_code=404, detail="Project detail not found")

#     detail.manager_approved = True
#     detail.approved_manager = current_user.id
#     detail.last_edited_on = datetime.utcnow()
#     detail.last_edited_by = current_user.id

#     db.commit()
#     return {"detail": "User approved by manager"}


from fastapi import Depends, APIRouter, HTTPException, Path
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID

@router.patch("/admin/approve-user")
def approve_user_by_admin(
    data: user_schemas.AdminApprovalRequest,
    db: Session = Depends(get_db)
):
    admin_user = db.query(user_models.User).filter(user_models.User.id == data.admin_id).first()

    if not admin_user:
        raise HTTPException(status_code=404, detail="Admin user not found")

    if not admin_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can perform this action")

    detail = db.query(projects.ProjectDetail).filter(projects.ProjectDetail.details_id == data.details_id).first()

    if not detail:
        raise HTTPException(status_code=404, detail="Project detail not found")

    if not detail.manager_approved:
        raise HTTPException(status_code=400, detail="Project must be approved by manager first")

    detail.admin_approved = data.admin_approved
    detail.remark = data.remark
    detail.last_edited_on = datetime.utcnow()
    detail.last_edited_by = data.admin_id

    db.commit()

    if data.admin_approved:
        return {"detail": "User has been approved by admin"}
    else:
        return {"detail": "Admin rejected the user/project", "remark": data.remark}
