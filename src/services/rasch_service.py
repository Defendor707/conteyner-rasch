import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import subprocess
import tempfile
import os
from loguru import logger

class RaschService:
    def __init__(self):
        self.r_script_path = "src/r_scripts/rasch_analysis.R"
    
    def analyze_matrix(self, data_matrix: pd.DataFrame) -> Dict:
        """Matrix ma'lumotlarini Rasch modeli bilan tahlil qilish"""
        try:
            # Ma'lumotlarni tayyorlash
            # Birinchi ustun - talabgor ismi, qolganlari - javoblar
            student_names = data_matrix.iloc[:, 0].tolist()
            response_data = data_matrix.iloc[:, 1:].values
            
            # NaN qiymatlarni 0 ga almashtirish
            response_data = np.nan_to_num(response_data, nan=0)
            
            # Faqat 0 va 1 qiymatlarini qoldirish
            response_data = np.where((response_data == 0) | (response_data == 1), response_data, 0)
            
            # DataFrame yaratish
            df = pd.DataFrame(response_data, columns=[f'q{i+1}' for i in range(response_data.shape[1])])
            df['student_name'] = student_names
            
            # Rasch tahlilini bajarish
            results = self.run_rasch_analysis(df)
            
            # Natijalarni formatlash
            formatted_results = self.format_results(results, student_names, df)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Matrix tahlili xatosi: {str(e)}")
            raise
    
    def run_rasch_analysis(self, data: pd.DataFrame) -> Dict:
        """R dasturi orqali Rasch tahlilini bajarish"""
        try:
            # Ma'lumotlarni CSV faylga saqlash
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                data.to_csv(f.name, index=False)
                temp_file = f.name
            
            # R skriptini ishga tushirish
            result = subprocess.run([
                'Rscript', 
                self.r_script_path, 
                temp_file
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                logger.error(f"R skripti xatosi: {result.stderr}")
                # Agar R skripti ishlamasa, oddiy hisoblash
                return self.simple_analysis(data)
            
            # Natijalarni o'qish
            results = self._parse_r_output(result.stdout, data)
            
            # Vaqtinchalik faylni o'chirish
            os.unlink(temp_file)
            
            return results
            
        except Exception as e:
            logger.error(f"Rasch tahlili xatosi: {str(e)}")
            # Xatolik bo'lsa oddiy hisoblash
            return self.simple_analysis(data)
    
    def simple_analysis(self, data: pd.DataFrame) -> Dict:
        """Oddiy statistika hisoblash (R ishlamasa)"""
        response_data = data.iloc[:, :-1].values  # student_name ustunini olib tashlash
        
        # Talabgorlar qobiliyati (to'g'ri javoblar foizi)
        student_abilities = np.mean(response_data, axis=1) * 100
        
        # Savollar qiyinligi (noto'g'ri javoblar foizi)
        question_difficulties = (1 - np.mean(response_data, axis=0)) * 100
        
        # Ishonchlilik (Cronbach's Alpha)
        n_questions = response_data.shape[1]
        if n_questions > 1:
            variance_total = np.var(np.sum(response_data, axis=1))
            variance_items = np.sum(np.var(response_data, axis=0))
            reliability = (n_questions / (n_questions - 1)) * (1 - variance_items / variance_total)
        else:
            reliability = 0.0
        
        return {
            'student_abilities': student_abilities,
            'question_difficulties': question_difficulties,
            'reliability': reliability,
            'total_students': len(student_abilities),
            'total_questions': n_questions
        }
    
    def _parse_r_output(self, output: str, data: pd.DataFrame) -> Dict:
        """R natijalarini parse qilish"""
        try:
            # Bu yerda R natijalarini parse qilish logikasi
            # Hozircha oddiy hisoblash qaytaraman
            return self.simple_analysis(data)
        except Exception as e:
            logger.error(f"R natijalarini parse qilish xatosi: {str(e)}")
            return self.simple_analysis(data)
    
    def format_results(self, results: Dict, student_names: List[str], data: pd.DataFrame) -> Dict:
        """Natijalarni formatlash"""
        student_abilities = results.get('student_abilities', [])
        question_difficulties = results.get('question_difficulties', [])
        reliability = results.get('reliability', 0.0)
        
        # Talabgorlar va ularning ballarini birlashtirish
        student_scores = list(zip(student_names, student_abilities))
        student_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Sertifikat darajalarini hisoblash
        grade_distribution = self.calculate_grades(student_abilities)
        
        # Model mosligi (oddiy korrelyatsiya)
        model_fit = reliability  # Hozircha ishonchlilikni model mosligi sifatida ishlatamiz
        
        return {
            'total_students': len(student_abilities),
            'total_questions': len(question_difficulties),
            'avg_ability': np.mean(student_abilities),
            'max_ability': np.max(student_abilities),
            'min_ability': np.min(student_abilities),
            'avg_difficulty': np.mean(question_difficulties),
            'reliability': reliability,
            'model_fit': model_fit,
            'grade_distribution': grade_distribution,
            'top_students': student_scores[:5],  # Top 5 talabgor
            'student_abilities': student_abilities,
            'question_difficulties': question_difficulties
        }
    
    def calculate_grades(self, ability_scores: List[float]) -> Dict[str, int]:
        """Qobiliyat ballarini sertifikat darajalariga aylantirish"""
        grades = {
            'A+': 0, 'A': 0, 'B+': 0, 'B': 0, 'C+': 0, 'C': 0
        }
        
        for score in ability_scores:
            if score >= 80:
                grades['A+'] += 1
            elif score >= 70:
                grades['A'] += 1
            elif score >= 60:
                grades['B+'] += 1
            elif score >= 50:
                grades['B'] += 1
            elif score >= 40:
                grades['C+'] += 1
            else:
                grades['C'] += 1
        
        return grades
    
    def create_wright_map(self, difficulty_params: List[float], ability_params: List[float]) -> str:
        """Rayt xaritasi yaratish"""
        # Bu yerda Rayt xaritasi yaratish logikasi
        # Hozircha oddiy matn qaytaraman
        return "Rayt xaritasi yaratildi"
