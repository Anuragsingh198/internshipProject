from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import SessionLocal
from models import  roles as role_models
from schemas import  roles as roles_schemas
from sqlalchemy.exc import IntegrityError
from schemas import roles as roles_schemas
from uuid import UUID ,uuid4

router = APIRouter(prefix="/roles", tags=["Roles"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=roles_schemas.AllRoles)
def get_roles(db: Session = Depends(get_db)):
    roles = db.query(role_models.Role).all()
    if not roles:
        raise HTTPException(status_code=404, detail="No roles found")
    return {"roles": roles}

@router.patch("/{role_id}", response_model=roles_schemas.RoleOut)
def update_role(
    role_id: UUID,
    role_data: roles_schemas.RoleData,
    db: Session = Depends(get_db)
):
    role = db.query(role_models.Role).filter(role_models.Role.role_id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    # Update fields
    if role_data.role_name:
        role.role_name = role_data.role_name
    if role_data.role_description is not None:
        role.role_description = role_data.role_description

    db.commit()
    db.refresh(role)
    return role


@router.post('/addRole', response_model=roles_schemas.RoleOut)
def add_new_role(
    payload: roles_schemas.CreateRole,
    db: Session = Depends(get_db)
):
    existing = db.query(role_models.Role).filter(role_models.Role.role_name == payload.role_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Role with this name already exists")

    new_role = role_models.Role(
        role_id=uuid4(),
        role_name=payload.role_name,
        role_description=payload.role_description or ""
    )

    db.add(new_role)
    db.commit()
    db.refresh(new_role)

    return new_role
    


# @router.delete("/{role_id}")
# def deleteRole(role_id: UUID, db: Session = Depends(get_db)):
#     role = db.query(role_models.Role).filter(role_models.Role.role_id == role_id).first()
#     if not role:
#         raise HTTPException(status_code=404, detail="Role not found")
#     db.delete(role)
#     db.commit()
    
#     return {"detail": "Role deleted successfully"}



