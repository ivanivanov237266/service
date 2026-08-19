# LLM Summarization Service (GigaChat)

Сервис суммаризации текста на базе **GigaChat** от Сбера. Предоставляет HTTP API для получения краткого содержания (3–5 предложений) по переданному тексту. Реализованы обработка ошибок, кеширование, логирование и fallback-механизм при недоступности LLM.

## Содержание

- [Возможности](#возможности)
- [Требования](#требования)
- [Установка и запуск](#установка-и-запуск)
- [Конфигурация](#конфигурация)
- [API](#api)
- [Примеры запросов](#примеры-запросов)
- [Архитектура](#архитектура)
- [Тестирование](#тестирование)
- [Устранение неполадок](#устранение-неполадок)

## Возможности

- Суммаризация текста через GigaChat (модель `GigaChat-Pro` или другая).
- Валидация входных данных (длина текста от 20 до 10 000 символов).
- Fallback-ответ при ошибках LLM (извлекает первые предложения).
- In-memory кеш с TTL для повторяющихся запросов.
- Структурированное логирование (JSON) ключевых этапов.
- Конфигурация через переменные окружения.
- CI (GitHub Actions) с линтером и тестами.

## Требования

- Python 3.9+
- Аккаунт разработчика GigaChat API (Client ID и Client Secret)
- Утилита `curl` или Postman для проверки API

## Установка и запуск

1. **Клонируйте репозиторий:**

   ```bash
   git clone https://github.com/<ваш_username>/llm-summarization-service.git
   cd llm-summarization-service
2. **Создайте и активируйте виртуальное окружение:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # или venv\Scripts\activate для Windows

3. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt

4. **Настройте переменные окружения:
Создайте файл .env в корне проекта по образцу .env.example:**
   ```ini
    LLM_PROVIDER=gigachat
    GIGACHAT_CLIENT_ID=ваш_client_id
    GIGACHAT_CLIENT_SECRET=ваш_client_secret
    GIGACHAT_SCOPE=GIGACHAT_API_PERS
    GIGACHAT_MODEL=GigaChat-Pro
    LLM_TIMEOUT=30
    LLM_MAX_TOKENS=300
    LLM_TEMPERATURE=0.3
    CACHE_TTL=3600
    CACHE_MAX_SIZE=100
    API_HOST=0.0.0.0
    API_PORT=8000
    LOG_LEVEL=INFO
    MIN_TEXT_LENGTH=20
    MAX_TEXT_LENGTH=10000

Запустите сервер:

bash
uvicorn main:app --reload
или

bash
python main.py
Сервис будет доступен по адресу http://localhost:8000.

Конфигурация
Все параметры задаются через переменные окружения (файл .env). Основные:

Переменная	Описание	По умолчанию
LLM_PROVIDER	Провайдер LLM (gigachat)	gigachat
GIGACHAT_CLIENT_ID	Client ID от GigaChat API	—
GIGACHAT_CLIENT_SECRET	Client Secret от GigaChat API	—
GIGACHAT_SCOPE	Scope для OAuth	GIGACHAT_API_PERS
GIGACHAT_MODEL	Модель GigaChat	GigaChat-Pro
LLM_TIMEOUT	Таймаут запроса к LLM (сек)	30
LLM_MAX_TOKENS	Максимум токенов в ответе	300
LLM_TEMPERATURE	Температура генерации	0.3
CACHE_TTL	Время жизни кеша (сек)	3600
CACHE_MAX_SIZE	Максимальное количество записей в кеше	100
MIN_TEXT_LENGTH	Минимальная длина входного текста	20
MAX_TEXT_LENGTH	Максимальная длина входного текста	10000
API
POST /api/v1/summarize
Принимает JSON с полем text и возвращает суммаризацию.

Тело запроса:

json
{
  "text": "Ваш текст для суммаризации..."
}
Успешный ответ (200):

json
{
  "summary": "Сгенерированная суммаризация...",
  "status": "success",
  "execution_time": 1.23,
  "model_used": "GigaChat-Pro",
  "cached": false
}
Ответ из кеша (200):

json
{
  "summary": "Сгенерированная суммаризация...",
  "status": "cache",
  "execution_time": 0.003,
  "cached": true
}
Fallback-ответ при недоступности LLM (200):

json
{
  "summary": "Первые предложения исходного текста...",
  "status": "fallback",
  "execution_time": 0.01,
  "cached": false
}
Ошибка валидации (422):

json
{
  "detail": [
    {
      "loc": ["body", "text"],
      "msg": "ensure this value has at least 20 characters",
      "type": "value_error.any_str.min_length",
      "ctx": {"limit_value": 20}
    }
  ]
}

Архитектура
Проект разделён на слои:

text
api/               # HTTP интерфейс, схемы запросов/ответов
services/          # Бизнес-логика, оркестрация
llm/               # Работа с GigaChat API, промпты
config.py          # Конфигурация из переменных окружения
main.py            # Точка входа FastAPI
tests/             # Модульные тесты
Поток данных:

API получает запрос → валидирует через Pydantic.

Бизнес-логика проверяет кеш → при попадании возвращает результат.

При промахе формирует промпт и вызывает LLMClient.generate_summary().

LLMClient аутентифицируется в GigaChat, отправляет запрос, обрабатывает ответ.

Пост-обработка очищает текст.

Результат сохраняется в кеш и возвращается пользователю.

При любой ошибке LLM (таймаут, сеть, неверный формат) генерируется fallback-ответ.