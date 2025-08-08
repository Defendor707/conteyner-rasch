from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from loguru import logger

from src.api.routes import router as api_router
from threading import Thread
from src.bot.bot import start_bot

app = FastAPI(title="Rasch Bot API", version="1.0.0")

# CORS sozlamalari
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routelarini qo'shish
app.include_router(api_router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    logger.info("Rasch Bot API ishga tushmoqda...")
    # Botni alohida threadda ishga tushirish (API ni bloklamaslik uchun)
    Thread(target=start_bot, daemon=True).start()

@app.get("/")
async def root():
    return {"message": "Rasch Bot API ishga tushgan"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
