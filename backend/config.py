# backend/config.py
from pydantic_settings import BaseSettings
from typing import Optional
import pytz


class Settings(BaseSettings):
    # App
    APP_NAME: str = "BML College AI Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "bml-chatbot-secret-key-change-in-production-2024"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./bml_chatbot.db"

    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "phi3"
    OLLAMA_TIMEOUT: int = 20  # Keep website chat responsive

    # Working Hours (UK time)
    TIMEZONE: str = "Europe/London"
    WORKING_HOURS_START: int = 9   # 9 AM
    WORKING_HOURS_END: int = 17    # 5 PM
    WORKING_DAYS: list = [0, 1, 2, 3, 4]  # Mon-Fri

    # WhatsApp (Twilio)
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_WHATSAPP_NUMBER: str = "whatsapp:+14155238886"
    WHATSAPP_VERIFY_TOKEN: str = "bml-whatsapp-verify-token"

    # College Info
    COLLEGE_PHONE_UK: str = "+44 (0) 121 523 0141"
    COLLEGE_PHONE_SL: str = "+94 (0) 112 19 6789"
    COLLEGE_EMAIL: str = "info@bmlcollege.com"
    COLLEGE_ADDRESS_UK: str = "Farm Street, Hockley, Birmingham, B19 2TZ, United Kingdom"
    COLLEGE_ADDRESS_SL: str = "163/4, New Kandy Road, Malabe, 10115, Sri Lanka"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()