from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import SessionLocal
from models import  roles as role_models
from sqlalchemy.exc import IntegrityError
from schemas import roles as roles_schemas
from uuid import UUID

router = APIRouter(prefix="/roles", tags=["Roles"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=roles_schemas.Allroles)
def get_roles(db: Session = Depends(get_db)):
    role_obj = db.query(role_models.Role).all()
    if not role_obj:
        raise HTTPException(status_code=404, detail="No roles found")

    return {"roles": role_obj}

@router.patch("/{role_id}")
def updateRole(role_id: UUID, rolename: roles_schemas.RoleData, db: Session = Depends(get_db)):
    role = db.query(role_models.Role).filter(role_models.Role.role_id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    role.role_name = rolename.role_name
    db.commit()
    db.refresh(role)
    return role


# @router.delete("/{role_id}")
# def deleteRole(role_id: UUID, db: Session = Depends(get_db)):
#     role = db.query(role_models.Role).filter(role_models.Role.role_id == role_id).first()
#     if not role:
#         raise HTTPException(status_code=404, detail="Role not found")
#     db.delete(role)
#     db.commit()
    
#     return {"detail": "Role deleted successfully"}



