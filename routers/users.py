from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import SessionLocal
from models import users as user_models, projects
from schemas import users as user_schemas
from sqlalchemy.exc import IntegrityError
import hashlib
from  auth.jwthandler  import  create_access_token
from  datetime import timedelta
router = APIRouter(prefix="/users", tags=["Users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login", response_model=user_schemas.LoginResponse)
def login_user(email: str, password: str, db: Session = Depends(get_db)):
    # hashed_password = hashlib.sha256(password.encode()).hexdigest()
    # user_obj = db.query(user_models.User).filter_by(email=email, password=hashed_password).first()
    user_obj = db.query(user_models.User).filter_by(email=email, password=password).first()

    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    access_token = create_access_token(
        data ={"sub": str(user_obj.id)},
        expires_delta=timedelta(minutes=60)
    )
    project_details = db.query(projects.ProjectDetail).filter_by(employee_id=user_obj.id).all()

    return {
        "user": user_obj,
        "projects": project_details,
        "access_token" : access_token,
        "token_type":"bearer"
    }
