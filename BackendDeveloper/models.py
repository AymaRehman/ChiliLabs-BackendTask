from sqlalchemy import Column, Integer, String
from BackendDeveloper.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    identifier = Column(String, unique=True, index=True)
    password_hash = Column(String)
    avatar_url = Column(String, nullable=True)
