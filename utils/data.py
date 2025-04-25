from sqlalchemy.orm import Session
from core.database import engine, Base
from models.users import User
from models.roles import Role
from models.projects import Project, ProjectDetail, ProjectHistory
import uuid
import random
from datetime import date, timedelta
import bcrypt

Base.metadata.create_all(bind=engine)

# def hash_password(plain_text):
    # return bcrypt.hashpw(plain_text.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

def seed_data():
    with Session(engine) as session:
        # Create users
        user_list = []
        for i in range(10):
            user = User(
                id=uuid.uuid4(),
                emp_id=f"EMP00{i}",
                first_name=f"First{i}",
                last_name=f"Last{i}",
                username=f"user{i}",
                email=f"user{i}@example.com",
                # password=hash_password(f"pass{i}"), 
                password=f"pass{i}", 
                is_manager=i % 2 == 0,
                is_admin=i % 3 == 0,
                is_active=True
            )
            user_list.append(user)
            session.add(user)

        # Create roles
        role_list = []
        for i in range(10):
            role = Role(
                role_id=uuid.uuid4(),
                role_name=f"Role{i}"
            )
            role_list.append(role)
            session.add(role)

        session.commit()

        # Create projects
        project_list = []
        for i in range(10):
            project = Project(
                project_id=uuid.uuid4(),
                project_name=f"Project {i}",
                project_description=f"Description {i}",
                project_owner=random.choice(user_list).id,
                project_status=random.choice(["Planned", "Ongoing", "Completed"]),
                start_date=random_date(date(2023, 1, 1), date(2023, 6, 1)),
                end_date=random_date(date(2023, 6, 2), date(2023, 12, 31))
            )
            project_list.append(project)
            session.add(project)

        session.commit()

        # Create project details
        for i in range(10):
            detail = ProjectDetail(
                details_id=uuid.uuid4(),
                project_id=random.choice(project_list).project_id,
                employee_id=random.choice(user_list).id,
                role_id=random.choice(role_list).role_id,
                status=random.choice(["Active", "Inactive"]),
                DA=bool(random.getrandbits(1)),
                AF=bool(random.getrandbits(1)),
                EA=bool(random.getrandbits(1)),
                DI=bool(random.getrandbits(1)),
                approved=random.choice(["Yes", "No"])
            )
            session.add(detail)

        # Create project history
        for i in range(10):
            history = ProjectHistory(
                history_id=uuid.uuid4(),
                project_id=random.choice(project_list).project_id,
                employee_id=random.choice(user_list).id,
                role_id=random.choice(role_list).role_id,
                start_date=random_date(date(2022, 1, 1), date(2022, 6, 1)),
                end_date=random_date(date(2022, 6, 2), date(2022, 12, 31))
            )
            session.add(history)

        session.commit()
        print("Data seeded successfully!")

