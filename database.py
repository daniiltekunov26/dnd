from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Character(Base):
    __tablename__ = 'characters'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    name = Column(String)
    race = Column(String)
    subrace = Column(String)
    class_name = Column(String)
    level = Column(Integer, default=1)
    strength = Column(Integer)
    dexterity = Column(Integer)
    constitution = Column(Integer)
    intelligence = Column(Integer)
    wisdom = Column(Integer)
    charisma = Column(Integer)
    skills = Column(JSON)  # Список навыков
    inventory = Column(JSON)  # Список предметов

engine = create_engine('sqlite:///characters.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
