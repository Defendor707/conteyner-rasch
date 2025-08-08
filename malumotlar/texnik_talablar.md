# Texnik Talablar va Arxitektura

## 1. Telegram Bot Funksionalligi

### Asosiy funksiyalar:
- Test yaratish: O'qituvchi yangi test yaratishi
- Javoblarni kiritish: Talabgorlar javoblarini kiritish
- Rasch tahlili: R dasturi orqali model hisoblash
- Natijalarni ko'rsatish: Rayt xaritasi va baholash natijalari
- Hisobotlar: PDF yoki Excel formatida hisobotlar

### Bot komandalari:
- /start - Botni ishga tushirish
- /new_test - Yangi test yaratish
- /add_questions - Savollarni qo'shish
- /add_students - Talabgorlarni qo'shish
- /analyze - Rasch tahlilini bajarish
- /results - Natijalarni ko'rsatish
- /help - Yordam

## 2. Arxitektura

### Komponentlar:
- Telegram Bot (Python)
- Python API (Flask/FastAPI)
- R Scripts (ltm package)
- Database (SQLite/PostgreSQL)
- File Storage (CSV/JSON)
- Reports (PDF/Excel)

## 3. Ma'lumotlar strukturasi

### Test ma'lumotlari:
- tests: test ma'lumotlari
- questions: savollar va ularning qiyinligi
- students: talabgorlar
- responses: javoblar

## 4. Rasch Modeli Implementatsiyasi

### R skripti (rasch_analysis.R):
- ltm kutubxonasini ishlatish
- 1PL Rasch modelini hisoblash
- Parametrlarni olish
- Rayt xaritasi yaratish

## 5. Python API

### Asosiy endpointlar:
- POST /api/tests - Yangi test yaratish
- POST /api/questions - Savollarni qo'shish
- POST /api/students - Talabgorlarni qo'shish
- POST /api/responses - Javoblarni kiritish
- GET /api/analyze/{test_id} - Rasch tahlilini bajarish
- GET /api/results/{test_id} - Natijalarni olish

## 6. Xavfsizlik

### Kerakli choralar:
- Telegram Bot API tokenini himoyalash
- Ma'lumotlar bazasi parolini himoyalash
- API endpointlarini autentifikatsiya qilish
- Ma'lumotlarni shifrlash

## 7. Deploy va Monitoring

### Docker konteynerlar:
- Python API konteyneri
- R dasturi konteyneri
- Ma'lumotlar bazasi konteyneri
- Nginx reverse proxy

### Monitoring:
- Log fayllarini kuzatish
- API response vaqtlarini o'lchash
- Xatolarni qayd qilish
