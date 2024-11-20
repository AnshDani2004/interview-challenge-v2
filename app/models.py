from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

Base = declarative_base()


class Business(Base):
    __tablename__ = "business"

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String(100), nullable=False, unique=True)
    
    symptoms = relationship("Symptom", back_populates="business")

class Symptom(Base):
    __tablename__ = "symptom"

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)

    code = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)
    diagnostic = Column(String(100), nullable=False)
    business_id = Column(Integer, ForeignKey("business.id"))

    business = relationship("Business", back_populates="symptoms")

