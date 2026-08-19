import time
import re
import logging
from typing import Dict, Any

from llm.client import LLMClient
from llm.prompts import build_summarization_prompt  # импорт из отдельного модуля
from services.cache import TTLCache
from services.postprocessing import clean_summary
from config import settings

logger = logging.getLogger(__name__)


class SummarizationService:
    """Сервис суммаризации текста: оркестрирует кеш, LLM и постобработку."""

    def __init__(self):
        self.llm_client = LLMClient()
        self.cache = TTLCache(ttl=settings.CACHE_TTL, max_size=settings.CACHE_MAX_SIZE)

    def _get_generation_params(self) -> Dict[str, Any]:
        """
        Параметры генерации, влияющие на ключ кеша.
        Если какой-то из них изменится, для того же текста будет создан новый кеш-ключ.
        """
        return {
            "model": settings.GIGACHAT_MODEL,
            "temperature": settings.LLM_TEMPERATURE,
            "max_tokens": settings.LLM_MAX_TOKENS,
            # Если системный промпт тоже становится настраиваемым, добавьте его сюда
            # "system_prompt": settings.GIGACHAT_SYSTEM_PROMPT
        }

    def process(self, text: str) -> Dict[str, Any]:
        start_time = time.time()

        # 1. Проверка кеша
        params = self._get_generation_params()
        cached_result = self.cache.get(text, params)
        if cached_result:
            logger.info("Возвращаем результат из кеша")
            return {
                "summary": cached_result,
                "status": "cache",
                "execution_time": time.time() - start_time,
                "cached": True,
            }

        # 2. Формирование промпта (используем функцию из llm.prompts)
        prompt = build_summarization_prompt(text)
        logger.debug(f"Сформирован промпт длиной {len(prompt)} символов")

        # 3. Вызов LLM с fallback
        try:
            raw_summary = self.llm_client.generate_summary(prompt)
            summary = clean_summary(raw_summary)

            # Простейшая проверка качества
            if len(summary) < 10:
                raise ValueError("Суммаризация слишком короткая")

            # 4. Кеширование успешного результата
            self.cache.set(text, params, summary)
            logger.info("Успешно сгенерирована и закеширована суммаризация")
            return {
                "summary": summary,
                "status": "success",
                "execution_time": time.time() - start_time,
                "model_used": settings.GIGACHAT_MODEL,
                "cached": False,
            }

        except (TimeoutError, ConnectionError, ValueError) as e:
            logger.error(f"LLM failed: {e}, используем fallback")
            fallback = self._fallback_summary(text)
            return {
                "summary": fallback,
                "status": "fallback",
                "execution_time": time.time() - start_time,
                "cached": False,
            }

    def _fallback_summary(self, text: str) -> str:
        """
        Простая экстрактивная суммаризация: первые 2-3 предложения.
        Используется при недоступности LLM.
        Улучшена: разбиение по знакам препинания с учётом переносов строк,
        обрезка по словам, а не по символам.
        """
        # Разбиваем на предложения (учитываем пробелы, табуляции, переводы строк)
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        if len(sentences) >= 3:
            result = " ".join(sentences[:3])
            if len(result) > 400:
                result = result[:400].rsplit(" ", 1)[0] + "..."
            return result
        elif len(sentences) >= 2:
            result = " ".join(sentences[:2])
            if len(result) > 300:
                result = result[:300].rsplit(" ", 1)[0] + "..."
            return result
        else:
            result = text[:300]
            if len(text) > 300:
                result = result.rsplit(" ", 1)[0] + "..."
            return result