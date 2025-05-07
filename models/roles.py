from  sqlalchemy import  Column , Integer , String
from  core.database  import   Base
import  uuid
from sqlalchemy.dialects.postgresql import UUID
class Role(Base):
    __tablename__ = "roles"
    role_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_descrition= Column(String ,default="")
    role_name = Column(String, unique=True, index=True)