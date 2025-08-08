from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./rasch_bot.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Test(Base):
    __tablename__ = "tests"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    teacher_id = Column(Integer)
    
    questions = relationship("Question", back_populates="test")
    students = relationship("Student", back_populates="test")

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"))
    question_text = Column(Text, nullable=False)
    correct_answer = Column(Integer)  # 0 yoki 1
    difficulty_b = Column(Float)  # Rasch qiyinlik parametri
    
    test = relationship("Test", back_populates="questions")
    responses = relationship("Response", back_populates="question")

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    test_id = Column(Integer, ForeignKey("tests.id"))
    
    test = relationship("Test", back_populates="students")
    responses = relationship("Response", back_populates="student")

class Response(Base):
    __tablename__ = "responses"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    answer = Column(Integer)  # 0 yoki 1
    
    student = relationship("Student", back_populates="responses")
    question = relationship("Question", back_populates="responses")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Ma'lumotlar bazasini yaratish
def create_tables():
    Base.metadata.create_all(bind=engine)
