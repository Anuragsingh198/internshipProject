from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import SessionLocal
from models import users as user_models, projects
from schemas import users as user_schemas
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
        "user": user_schemas.UserOut.from_orm(user_obj),
        "projects": [user_schemas.ProjectDetailOut.from_orm(p) for p in project_details],
        "access_token": access_token,
        "token_type": "bearer"
    }


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

from schemas import users as user_schemas
@router.get("/manager/new-user-request/{user_id}", response_model=list[ user_schemas.ProjectDetailResponse])
def get_pending_users_for_manager(user_id: UUID, db: Session = Depends(get_db)):
    pending = db.query(projects.ProjectDetail).filter(
        projects.ProjectDetail.manager_approved == False,
        projects.ProjectDetail.approved_manager == user_id
    ).all()
    return pending

@router.get("/admin/new-user-request/{user_id}", response_model=list[ user_schemas.ProjectDetailResponse])
def get_pending_users_for_admin(user_id: UUID, db: Session = Depends(get_db)):
    pending = db.query(projects.ProjectDetail).filter(
        projects.ProjectDetail.manager_approved == True,
        projects.ProjectDetail.admin_approved == False
    ).all()
    return pending


@router.post("/manager/approve-user")
def approve_user_by_manager(
    payload: user_schemas.ApproveUserRequest,
    db: Session = Depends(get_db),
):
    current_user = db.query(user_models.User).filter_by(id=payload.user_id).first()

    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not current_user.is_manager:
        raise HTTPException(status_code=403, detail="Only managers can perform this action")

    detail = db.query(projects.ProjectDetail).filter_by(
        employee_id=payload.employee_id,
        project_id=payload.project_id
    ).first()

    if not detail:
        raise HTTPException(status_code=404, detail="Project detail not found")

    detail.manager_approved = True
    detail.approved_manager = current_user.id
    detail.last_edited_on = datetime.utcnow()
    detail.last_edited_by = current_user.id

    db.commit()
    return {"detail": "User approved by manager"}


@router.post("/admin/approve-user")
def approve_user_by_admin(
    payload: user_schemas.ApproveUserRequest,
    db: Session = Depends(get_db),
):
    current_user = db.query(user_models.User).filter_by(id=payload.user_id).first()

    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can perform this action")

    detail = db.query(projects.ProjectDetail).filter_by(
        employee_id=payload.employee_id,
        project_id=payload.project_id,
        manager_approved=True
    ).first()

    if not detail:
        raise HTTPException(status_code=404, detail="Approval not found or not yet approved by manager")

    detail.admin_approved = True
    detail.last_edited_on = datetime.utcnow()
    detail.last_edited_by = current_user.id

    db.commit()
    return {"detail": "User approved by admin"}
