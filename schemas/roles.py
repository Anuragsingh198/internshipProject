from typing import Optional
from uuid import UUID
from datetime import date
from  typing import  List
from pydantic import BaseModel

class RoleOut(BaseModel):
    role_id: UUID
    role_name: str

    class Config:
        orm_mode = True

class  Allroles(BaseModel):
    roles:List[RoleOut]
    class Config:
          orm_mode = True

class RoleData(BaseModel):
     role_name : str
     class Config:
          orm_mode = True
