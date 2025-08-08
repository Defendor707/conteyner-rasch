from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel

from src.models.database import get_db, Test, Question, Student, Response
from src.services.rasch_service import RaschService

router = APIRouter()
rasch_service = RaschService()

# Pydantic modellar
class TestCreate(BaseModel):
    name: str
    subject: str
    teacher_id: int

class QuestionCreate(BaseModel):
    test_id: int
    question_text: str
    correct_answer: int

class StudentCreate(BaseModel):
    test_id: int
    name: str

class ResponseCreate(BaseModel):
    student_id: int
    question_id: int
    answer: int

# Test routelari
@router.post("/tests", response_model=Dict[str, Any])
def create_test(test: TestCreate, db: Session = Depends(get_db)):
    """Yangi test yaratish"""
    try:
        db_test = Test(
            name=test.name,
            subject=test.subject,
            teacher_id=test.teacher_id
        )
        db.add(db_test)
        db.commit()
        db.refresh(db_test)
        
        return {
            "success": True,
            "test_id": db_test.id,
            "message": "Test muvaffaqiyatli yaratildi"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tests", response_model=List[Dict[str, Any]])
def get_tests(db: Session = Depends(get_db)):
    """Barcha testlarni olish"""
    tests = db.query(Test).all()
    return [
        {
            "id": test.id,
            "name": test.name,
            "subject": test.subject,
            "created_at": test.created_at
        }
        for test in tests
    ]

# Savol routelari
@router.post("/questions", response_model=Dict[str, Any])
def create_question(question: QuestionCreate, db: Session = Depends(get_db)):
    """Yangi savol qo'shish"""
    try:
        db_question = Question(
            test_id=question.test_id,
            question_text=question.question_text,
            correct_answer=question.correct_answer
        )
        db.add(db_question)
        db.commit()
        db.refresh(db_question)
        
        return {
            "success": True,
            "question_id": db_question.id,
            "message": "Savol muvaffaqiyatli qo'shildi"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tests/{test_id}/questions", response_model=List[Dict[str, Any]])
def get_test_questions(test_id: int, db: Session = Depends(get_db)):
    """Test savollarini olish"""
    questions = db.query(Question).filter(Question.test_id == test_id).all()
    return [
        {
            "id": question.id,
            "question_text": question.question_text,
            "correct_answer": question.correct_answer,
            "difficulty_b": question.difficulty_b
        }
        for question in questions
    ]

# Talabgor routelari
@router.post("/students", response_model=Dict[str, Any])
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    """Yangi talabgor qo'shish"""
    try:
        db_student = Student(
            test_id=student.test_id,
            name=student.name
        )
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
        
        return {
            "success": True,
            "student_id": db_student.id,
            "message": "Talabgor muvaffaqiyatli qo'shildi"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tests/{test_id}/students", response_model=List[Dict[str, Any]])
def get_test_students(test_id: int, db: Session = Depends(get_db)):
    """Test talabgorlarini olish"""
    students = db.query(Student).filter(Student.test_id == test_id).all()
    return [
        {
            "id": student.id,
            "name": student.name
        }
        for student in students
    ]

# Javob routelari
@router.post("/responses", response_model=Dict[str, Any])
def create_response(response: ResponseCreate, db: Session = Depends(get_db)):
    """Yangi javob qo'shish"""
    try:
        db_response = Response(
            student_id=response.student_id,
            question_id=response.question_id,
            answer=response.answer
        )
        db.add(db_response)
        db.commit()
        db.refresh(db_response)
        
        return {
            "success": True,
            "response_id": db_response.id,
            "message": "Javob muvaffaqiyatli qo'shildi"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Rasch tahlili routelari
@router.post("/analyze/{test_id}", response_model=Dict[str, Any])
def analyze_test(test_id: int, db: Session = Depends(get_db)):
    """Test uchun Rasch tahlilini bajarish"""
    try:
        # Test ma'lumotlarini olish
        responses = db.query(Response).join(Question).filter(Question.test_id == test_id).all()
        
        if not responses:
            raise HTTPException(status_code=404, detail="Test uchun javoblar topilmadi")
        
        # Javoblarni formatga o'tkazish
        response_data = [
            {
                "student_id": r.student_id,
                "question_id": r.question_id,
                "answer": r.answer
            }
            for r in responses
        ]
        
        # Rasch tahlilini bajarish
        results = rasch_service.run_rasch_analysis(
            rasch_service.prepare_data(response_data)
        )
        
        return {
            "success": True,
            "test_id": test_id,
            "results": results,
            "message": "Rasch tahlili muvaffaqiyatli bajarildi"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results/{test_id}", response_model=Dict[str, Any])
def get_test_results(test_id: int, db: Session = Depends(get_db)):
    """Test natijalarini olish"""
    try:
        # Bu yerda natijalarni olish logikasi
        # Hozircha oddiy struktura qaytaraman
        
        return {
            "success": True,
            "test_id": test_id,
            "results": {
                "total_students": 25,
                "average_score": 65.4,
                "grade_distribution": {
                    "A+": 3,
                    "A": 8,
                    "B+": 7,
                    "B": 4,
                    "C+": 2,
                    "C": 1
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
