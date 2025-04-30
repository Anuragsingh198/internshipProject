from sqlalchemy.orm import Session
from core.database import engine, Base
from models.users import User
from models.roles import Role
from models.projects import Project, ProjectDetail, ProjectHistory, ProjectStatusEnum
import uuid
import random
from datetime import date, timedelta, datetime

Base.metadata.create_all(bind=engine)

def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

def seed_data():
    with Session(engine) as session:
        # Create random users
        user_list = []
        for i in range(10):
            user = User(
                id=uuid.uuid4(),
                emp_id=f"EMP{str(i+1).zfill(3)}",
                first_name=f"First{i}",
                last_name=f"Last{i}",
                username=f"user{i}",
                email=f"user{i}@example.com",
                password=f"pass{i}",  # Replace with hashed passwords as needed
                is_manager=bool(random.getrandbits(1)),
                is_admin=bool(random.getrandbits(1)),
                is_active=True
            )
            session.add(user)
            user_list.append(user)
        session.commit()

        # Create roles
        role_list = []
        for i in range(5):
            role = Role(
                role_id=uuid.uuid4(),
                role_name=f"Role{i}"
            )
            session.add(role)
            role_list.append(role)
        session.commit()

        # Create projects with DA, AF, EA, DI
        project_list = []
        for i in range(5):
            project = Project(
                project_id=uuid.uuid4(),
                project_name=f"Project {i}",
                project_description=f"Description {i}",
                project_owner=random.choice(user_list).id,
                project_status=random.choice(list(ProjectStatusEnum)),
                DA=bool(random.getrandbits(1)),
                AF=bool(random.getrandbits(1)),
                EA=bool(random.getrandbits(1)),
                DI=bool(random.getrandbits(1)),
                start_date=random_date(date(2023, 1, 1), date(2023, 6, 1)),
                end_date=random_date(date(2023, 6, 2), date(2023, 12, 31))
            )
            session.add(project)
            project_list.append(project)
        session.commit()

        # Create project details (without DA, AF, EA, DI)
        for project in project_list:
            for user in user_list:
                manager = next((u for u in user_list if u.is_manager), user_list[0])
                editor = random.choice(user_list)
                detail = ProjectDetail(
                    details_id=uuid.uuid4(),
                    project_id=project.project_id,
                    employee_id=user.id,
                    role_id=random.choice(role_list).role_id,
                    status=random.choice(["Active", "Inactive"]),
                    manager_approved=bool(random.getrandbits(1)),
                    approved_manager=manager.id,
                    admin_approved=bool(random.getrandbits(1)),
                    last_edited_on=datetime.utcnow(),
                    last_edited_by=editor.id
                )
                session.add(detail)

        # Create project history
        for project in project_list:
            for user in user_list:
                history = ProjectHistory(
                    history_id=uuid.uuid4(),
                    project_id=project.project_id,
                    employee_id=user.id,
                    role_id=random.choice(role_list).role_id,
                    start_date=random_date(date(2022, 1, 1), date(2022, 6, 1)),
                    end_date=random_date(date(2022, 6, 2), date(2022, 12, 31))
                )
                session.add(history)

        session.commit()
        print("Data seeded successfully!")
