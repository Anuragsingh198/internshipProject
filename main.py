from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import Base, engine
from models.users import User
from models.projects import Project, ProjectDetail, ProjectHistory
from models.roles import Role 
from routers import users 
# from utils  import  data

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Project Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
# data.seed_data()
@app.get("/")
def read_root():
    return {"message": "FastAPI server is running 🎉"}
   