print("Initializing database...")
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from datetime import datetime

engine=create_engine("sqlite:///thebot.db")

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    tg_id = Column(Integer, primary_key=True)
    name = Column(String)
    money = Column(Integer, default=200)
    farm_time = Column(DateTime, nullable=False)


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True)
    tg_id = Column(String, unique=True)

class UserFactory(Base):
    __tablename__ = "user_factories"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.tg_id"))
    factory_name = Column(String, nullable=False)
    last_used = Column(DateTime, nullable=False)

Base.metadata.create_all(engine)

with Session(engine) as session:
    admin=Admin(
        tg_id="1975572565"
    )
    user_factory = UserFactory(
        user_id=1975572565,
        factory_name="coal_mine",
        last_used=datetime.utcnow()
    )
    session.add(admin)
    session.add(user_factory)
    session.commit()
    
