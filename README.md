# Rasch Modeli Telegram Bot

Milliy sertifikat imtihonlari uchun Rasch modeli tahlilini bajaradigan Telegram bot.

## Loyiha haqida

Bu bot O'zbekiston Respublikasi Bilim va malakalarni baholash agentligi (UZBMB) standartlariga mos 1-parametrli (1PL) dixotomik Rasch modelini qo'llaydi.

### Asosiy xususiyatlar

- ✅ 1PL Rasch modeli implementatsiyasi
- ✅ R dasturi va ltm paketi integratsiyasi
- ✅ Telegram bot interfeysi
- ✅ Ma'lumotlar bazasi (PostgreSQL/SQLite)
- ✅ REST API
- ✅ Docker konteynerizatsiya
- ✅ Rayt xaritasi (Wright map) yaratish
- ✅ Sertifikat darajalari hisoblash

## Texnik talablar

- Python 3.11+
- R 4.0+
- PostgreSQL (yoki SQLite)
- Docker (ixtiyoriy)

## O'rnatish

### 1. Loyihani klonlash
```bash
git clone <repository-url>
cd rasch_bot_project
```

### 2. Python dependencies
```bash
pip install -r requirements.txt
```

### 3. R paketlarini o'rnatish
```r
install.packages(c("ltm", "ggplot2", "dplyr"))
```

### 4. Environment variables
```bash
cp .env.example .env
# .env faylini sozlash
```

### 5. Ma'lumotlar bazasini sozlash
```bash
python -c "from src.models.database import create_tables; create_tables()"
```

## Docker bilan ishga tushirish

```bash
docker-compose up -d
```

## Qo'llash

### Telegram Bot

1. BotFather orqali yangi bot yarating
2. TELEGRAM_TOKEN ni .env faylga qo'shing
3. Botni ishga tushiring

### API

```bash
uvicorn src.main:app --reload
```

API dokumentatsiyasi: http://localhost:8000/docs

## Bot komandalari

- `/start` - Botni ishga tushirish
- `/new_test` - Yangi test yaratish
- `/add_questions` - Savollarni qo'shish
- `/add_students` - Talabgorlarni qo'shish
- `/analyze` - Rasch tahlilini bajarish
- `/results` - Natijalarni ko'rsatish
- `/help` - Yordam

## API Endpointlar

- `POST /api/tests` - Yangi test yaratish
- `POST /api/questions` - Savollarni qo'shish
- `POST /api/students` - Talabgorlarni qo'shish
- `POST /api/responses` - Javoblarni kiritish
- `GET /api/analyze/{test_id}` - Rasch tahlilini bajarish
- `GET /api/results/{test_id}` - Natijalarni olish

## Loyiha strukturasi

```
rasch_bot_project/
├── malumotlar/          # Loyiha ma'lumotlari
├── src/                 # Asosiy kod
│   ├── api/            # API routelari
│   ├── bot/            # Telegram bot
│   ├── models/         # Ma'lumotlar bazasi modellari
│   ├── services/       # Biznes logika
│   ├── r_scripts/      # R skriptlari
│   └── utils/          # Yordamchi funksiyalar
├── tests/              # Test fayllari
├── docs/               # Hujjatlar
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker image
└── docker-compose.yml  # Docker compose
```

## Rasch modeli

### Model parametrlari
- **θ (theta)**: Talabgorning yashirin qobiliyati
- **b**: Topshiriqning qiyinligi
- **a**: Diskriminatsiya parametri (1PL da teng)

### Baholash tizimi
- A+ daraja: 70+ ball
- A daraja: 65-69.9 ball
- B+ daraja: 60-64.9 ball
- B daraja: 55-59.9 ball
- C+ daraja: 50-54.9 ball
- C daraja: <50 ball

## Testlash

```bash
pytest tests/
```

## Xavfsizlik

- Telegram Bot API tokenini himoyalash
- Ma'lumotlar bazasi parolini himoyalash
- API endpointlarini autentifikatsiya qilish

## Monitoring

- Log fayllarini kuzatish
- API response vaqtlarini o'lchash
- Xatolarni qayd qilish

## Yordam

Muammolar yoki savollar uchun:
- GitHub Issues oching
- Telegram: @admin

## Litsenziya

MIT License
