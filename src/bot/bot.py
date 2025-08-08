import asyncio
import os
import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from loguru import logger
from src.services.rasch_service import RaschService
from src.models.database import get_db, Test, Question, Student, Response

class RaschBot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_TOKEN")
        if not self.token:
            raise ValueError("TELEGRAM_TOKEN environment variable topilmadi")
        
        self.application = Application.builder().token(self.token).build()
        self.rasch_service = RaschService()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Bot handlerlarini sozlash"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("analyze", self.analyze_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # Xabar handler
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Callback query handler
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Botni ishga tushirish"""
        welcome_text = """
🎓 Rasch Modeli Botiga xush kelibsiz!

Bu bot milliy sertifikat imtihonlari uchun Rasch modeli tahlilini bajaradi.

📋 Qo'llash:
1. Excel yoki CSV fayl yuboring (talabgorlar va javoblar bilan)
2. Yoki matn formatida ma'lumotlarni yuboring
3. /analyze komandasi bilan tahlilni bajarish

�� Ma'lumotlar formati:
- Birinchi ustun: Talabgor ismi
- Keyingi ustunlar: Har bir savolga javob (0 yoki 1)

📋 Mavjud komandalar:
/analyze - Rasch tahlilini bajarish
/help - Yordam

Boshlash uchun ma'lumotlarni yuboring!
        """
        await update.message.reply_text(welcome_text)
    
    async def analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Rasch tahlilini bajarish"""
        if 'data_matrix' not in context.user_data:
            await update.message.reply_text("❌ Avval ma'lumotlarni yuboring!")
            return
        
        await update.message.reply_text("🔬 Rasch tahlili bajarilmoqda...")
        
        try:
            # Ma'lumotlarni olish
            data_matrix = context.user_data['data_matrix']
            
            # Rasch tahlilini bajarish
            results = self.rasch_service.analyze_matrix(data_matrix)
            
            # Natijalarni ko'rsatish
            await self.show_results(update, results)
            
        except Exception as e:
            logger.error(f"Rasch tahlili xatosi: {str(e)}")
            await update.message.reply_text(f"❌ Xatolik yuz berdi: {str(e)}")
    
    async def show_results(self, update: Update, results: dict):
        """Natijalarni ko'rsatish"""
        # Umumiy statistika
        stats_text = f"""
📊 **Rasch Tahlili Natijalari**

👥 **Talabgorlar:**
- Jami: {results['total_students']} ta
- O'rtacha qobiliyat: {results['avg_ability']:.2f}
- Eng yuqori: {results['max_ability']:.2f}
- Eng past: {results['min_ability']:.2f}

📝 **Savollar:**
- Jami: {results['total_questions']} ta
- O'rtacha qiyinlik: {results['avg_difficulty']:.2f}

📈 **Model ko'rsatkichlari:**
- Ishonchlilik: {results['reliability']:.3f}
- Model mosligi: {results['model_fit']:.3f}

🏆 **Sertifikat darajalari:**
"""
        
        # Sertifikat darajalari
        for grade, count in results['grade_distribution'].items():
            stats_text += f"- {grade}: {count} ta\n"
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')
        
        # Top 5 talabgorlar
        if results['top_students']:
            top_text = "🥇 **Eng yaxshi 5 talabgor:**\n"
            for i, (name, score) in enumerate(results['top_students'], 1):
                top_text += f"{i}. {name}: {score:.2f}\n"
            await update.message.reply_text(top_text, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Xabar qayta ishlash"""
        text = update.message.text
        
        try:
            # CSV formatda ma'lumotlarni parse qilish
            if '\t' in text or ',' in text:
                # CSV format
                lines = text.strip().split('\n')
                data = []
                
                for line in lines:
                    if '\t' in line:
                        row = line.split('\t')
                    else:
                        row = line.split(',')
                    
                    # Birinchi ustun - ism, qolganlari - javoblar
                    student_name = row[0].strip()
                    answers = [int(x.strip()) for x in row[1:] if x.strip() in ['0', '1']]
                    
                    if answers:  # Faqat javoblari bor qatorlarni qo'shish
                        data.append([student_name] + answers)
                
                if data:
                    # DataFrame yaratish
                    df = pd.DataFrame(data)
                    df.columns = ['student_name'] + [f'q{i+1}' for i in range(len(df.columns)-1)]
                    
                    context.user_data['data_matrix'] = df
                    
                    await update.message.reply_text(
                        f"✅ Ma'lumotlar qabul qilindi!\n\n"
                        f"👥 Talabgorlar: {len(df)} ta\n"
                        f"📝 Savollar: {len(df.columns)-1} ta\n\n"
                        f"Endi /analyze komandasi bilan tahlilni bajaring."
                    )
                else:
                    await update.message.reply_text("❌ Ma'lumotlarni to'g'ri formatda yuboring!")
            
            else:
                await update.message.reply_text(
                    "📋 Ma'lumotlarni quyidagi formatda yuboring:\n\n"
                    "Ism\t0\t1\t0\t1\t0\n"
                    "Yoki\n"
                    "Ism,0,1,0,1,0\n\n"
                    "Bu yerda 0 - noto'g'ri, 1 - to'g'ri javob"
                )
                
        except Exception as e:
            logger.error(f"Ma'lumotlarni parse qilish xatosi: {str(e)}")
            await update.message.reply_text("❌ Ma'lumotlarni to'g'ri formatda yuboring!")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Yordam"""
        help_text = """
❓ **Yordam**

Bu bot milliy sertifikat imtihonlari uchun Rasch modeli tahlilini bajaradi.

📋 **Qo'llash:**
1. Talabgorlar va ularning javoblarini yuboring
2. /analyze komandasi bilan tahlilni bajaring
3. Natijalarni ko'ring

📊 **Ma'lumotlar formati:**
```
Ism Familya    0    1    0    1    0
Azizov Aziz    1    1    0    1    1
Karimova Malika    0    1    1    0    1
```

📈 **Natijalar:**
- Talabgorlar qobiliyati (θ)
- Savollar qiyinligi (b)
- Sertifikat darajalari
- Model ishonchliligi

📞 Qo'llab-quvvatlash: @admin
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Button callback"""
        query = update.callback_query
        await query.answer()
        
        # Bu yerda button callback logikasi
        await query.edit_message_text("✅ Tanlandi!")
    
    def run(self):
        """Botni ishga tushirish"""
        logger.info("Rasch Bot ishga tushmoqda...")
        self.application.run_polling()

def start_bot():
    """Botni ishga tushirish funksiyasi"""
    bot = RaschBot()
    bot.run()
