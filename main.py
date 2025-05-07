from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from core.database import Base, engine
from models.users import User
from models.projects import Project, ProjectDetail, ProjectHistory
from models.roles import Role 
from routers import users, project, roles 
from routers import otp
# from utils import data
from models.otp import OTP

Base.metadata.create_all(bind=engine)

# data.seed_data()

app = FastAPI(title="Project Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(project.router)
app.include_router(roles.router)
app.include_router(otp.router)

@app.get("/")
def read_root():
    return {"message": "FastAPI server is running"}
