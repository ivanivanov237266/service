import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # LLM Provider
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gigachat")
    LLM_MAX_RETRIES = 3
    LLM_RETRY_DELAY = 2

    # GigaChat
    GIGACHAT_AUTH_KEY = os.getenv("GIGACHAT_AUTH_KEY")  # если задан, использовать его
    GIGACHAT_CLIENT_ID = os.getenv("GIGACHAT_CLIENT_ID")
    GIGACHAT_CLIENT_SECRET = os.getenv("GIGACHAT_CLIENT_SECRET")
    GIGACHAT_SCOPE = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
    GIGACHAT_MODEL = os.getenv("GIGACHAT_MODEL", "GigaChat-Pro")
    LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "30"))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "300"))
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
    MIN_TEXT_LENGTH = int(os.getenv("MIN_TEXT_LENGTH", "20"))
    MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", "10000"))
    GIGACHAT_AUTH_URL = os.getenv("GIGACHAT_AUTH_URL", "https://ngw.devices.sberbank.ru:9443/api/v2/oauth")
    GIGACHAT_BASE_URL = os.getenv("GIGACHAT_BASE_URL", "https://gigachat.devices.sberbank.ru/api/v1")
    GIGACHAT_AUTH_TIMEOUT = int(os.getenv("GIGACHAT_AUTH_TIMEOUT", "10"))

    # Cache
    CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))
    CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", "100"))

    # API
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()