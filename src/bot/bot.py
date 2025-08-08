import os
import pandas as pd
from loguru import logger
from typing import Dict

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from src.services.rasch_service import RaschService


class RaschBot:
    def __init__(self) -> None:
        self.token = os.getenv("TELEGRAM_TOKEN")
        if not self.token:
            raise ValueError("TELEGRAM_TOKEN environment variable topilmadi")

        self.application = Application.builder().token(self.token).build()
        self.rasch_service = RaschService()
        self._register_handlers()

    def _register_handlers(self) -> None:
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("analyze", self.analyze_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        text = (
            "🎓 Rasch Modeli Botiga xush kelibsiz!\n\n"
            "Bu bot 0/1 matritsa asosida 1-bosqichda ball hisoblab beradi.\n\n"
            "📋 Ma'lumotlar formati:\n"
            "Ism,0,1,0,1,0 yoki\nIsm\t0\t1\t0\t1\t0\n\n"
            "1) Matritsani yuboring\n2) /analyze ni bosing\n"
        )
        await update.message.reply_text(text)

    async def analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if "data_matrix" not in context.user_data:
            await update.message.reply_text("❌ Avval matritsani yuboring!")
            return

        await update.message.reply_text("🔬 Tahlil bajarilmoqda...")
        try:
            df: pd.DataFrame = context.user_data["data_matrix"]
            results: Dict = self.rasch_service.analyze_matrix(df)
            await self._send_results(update, results)
        except Exception as exc:
            logger.exception("Analyze failed")
            await update.message.reply_text(f"❌ Xatolik: {exc}")

    async def _send_results(self, update: Update, results: Dict) -> None:
        lines = [
            "📊 Natijalar",
            f"👥 Jami talabgor: {results['total_students']}",
            f"📝 Jami savol: {results['total_questions']}",
            f"📈 O'rtacha ball: {results['avg_ability']:.2f}",
            f"⬆️ Eng yuqori: {results['max_ability']:.2f}",
            f"⬇️ Eng past: {results['min_ability']:.2f}",
            f"🧪 Ishonchlilik (alpha): {results['reliability']:.3f}",
        ]
        lines.append("\n🏆 Sertifikat darajalari:")
        for grade, count in results["grade_distribution"].items():
            lines.append(f"- {grade}: {count} ta")

        await update.message.reply_text("\n".join(lines))

        if results["top_students"]:
            top = ["\n🥇 Eng yaxshi 5 talabgor:"]
            for i, (name, score) in enumerate(results["top_students"], start=1):
                top.append(f"{i}. {name}: {score:.2f}")
            await update.message.reply_text("\n".join(top))

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        text = (update.message.text or "").strip()
        if not text:
            await update.message.reply_text("Matn yuboring.")
            return

        try:
            lines = [ln for ln in text.splitlines() if ln.strip()]
            data = []
            for line in lines:
                row = [cell.strip() for cell in (line.split("\t") if "\t" in line else line.split(","))]
                if not row:
                    continue
                name = row[0]
                answers = [int(x) for x in row[1:] if x in ("0", "1")]
                if answers:
                    data.append([name] + answers)

            if not data:
                await update.message.reply_text("❌ Formatda xato. Namuna: Ism,1,0,1,0")
                return

            df = pd.DataFrame(data)
            df.columns = ["student_name"] + [f"q{i+1}" for i in range(len(df.columns) - 1)]
            context.user_data["data_matrix"] = df
            await update.message.reply_text(
                f"✅ Qabul qilindi. Talabgorlar: {len(df)}, Savollar: {len(df.columns) - 1}. /analyze ni bosing."
            )
        except Exception as exc:
            logger.exception("Parse error")
            await update.message.reply_text(f"❌ Parse xatosi: {exc}")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("Matritsa yuboring va /analyze ni bosing.")

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text("✅ Tanlandi!")

    def run(self) -> None:
        # Thread ichida event loop tayyorlash
        import asyncio
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        logger.info("Rasch Bot ishga tushmoqda...")
        self.application.run_polling()


def start_bot() -> None:
    bot = RaschBot()
    bot.run()
