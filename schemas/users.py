from  pydantic import  BaseModel
from  typing import Optional , List
from schemas import projects
from uuid import UUID

class UserData(BaseModel):
    email:str
    password : str

class UserOut(BaseModel):
    id : UUID
    emp_id :str
    first_name :str
    last_name :str
    username :str
    email :str
    is_manager : bool 
    is_admin : bool
    is_active : bool
    class Config:
        orm_mode = True

class LoginResponse(BaseModel):
    user: UserOut
    projects: List[projects.ProjectDetailsOut]
    access_token : str
    toke_type:str ="bearer"
    class Config:
        orm_mode = True
