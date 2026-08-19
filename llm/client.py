import requests
import json
import logging
import time
from config import settings
import uuid
import base64

logger = logging.getLogger(__name__)


def _get_access_token(self):
    if self.access_token and time.time() < self.token_expires_at:
        return self.access_token

    auth_url = settings.GIGACHAT_AUTH_URL
    rq_uid = str(uuid.uuid4())  # уникальный UUID для каждого запроса
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": rq_uid
    }

    # Определяем Authorization Key
    if settings.GIGACHAT_AUTH_KEY:
        auth_key = settings.GIGACHAT_AUTH_KEY
    elif settings.GIGACHAT_CLIENT_ID and settings.GIGACHAT_CLIENT_SECRET:
        credentials = f"{settings.GIGACHAT_CLIENT_ID}:{settings.GIGACHAT_CLIENT_SECRET}"
        auth_key = base64.b64encode(credentials.encode()).decode()
    else:
        raise ValueError("GigaChat credentials not configured")

    headers["Authorization"] = f"Basic {auth_key}"

    data = {"scope": settings.GIGACHAT_SCOPE}

    try:
        response = requests.post(auth_url, data=data, headers=headers, timeout=settings.GIGACHAT_AUTH_TIMEOUT)
        response.raise_for_status()
        token_data = response.json()
        self.access_token = token_data["access_token"]
        # Используем expires_at, если есть
        if "expires_at" in token_data:
            self.token_expires_at = token_data["expires_at"]  # предполагается Unix timestamp
        else:
            # fallback на expires_in, если нет
            expires_in = token_data.get("expires_in", 1800)
            self.token_expires_at = time.time() + expires_in - 60
        logger.info("Successfully obtained GigaChat access token")
        return self.access_token
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get GigaChat token: {e}")
        if e.response is not None:
            logger.error(f"Response status: {e.response.status_code}")
            logger.error(f"Response body: {e.response.text}")
        raise ConnectionError("Failed to authenticate with GigaChat")


class LLMClient:
    def __init__(self):
        self.api_key = settings.GIGACHAT_AUTH_KEY
        self.client_id = settings.GIGACHAT_CLIENT_ID
        self.client_secret = settings.GIGACHAT_CLIENT_SECRET
        self.scope = settings.GIGACHAT_SCOPE
        self.model = settings.GIGACHAT_MODEL
        self.timeout = settings.LLM_TIMEOUT
        self.access_token = None
        self.token_expires_at = 0
        self.base_url = "https://gigachat.devices.sberbank.ru/api/v1"

    def _get_access_token(self):
        """Получение access token для GigaChat API"""
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token

        auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        auth_data = {
            "scope": self.scope
        }
        auth_headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "RqUID": self.client_id,
            "Authorization": f"Basic {self.client_secret}"
        }

        try:
            response = requests.post(
                auth_url,
                data=auth_data,
                headers=auth_headers,
                timeout=10
            )
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data["access_token"]
            self.token_expires_at = time.time() + token_data.get("expires_in", 1800) - 60
            logger.info("Successfully obtained GigaChat access token")
            return self.access_token

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get GigaChat token: {e}")
            raise ConnectionError("Failed to authenticate with GigaChat")

    def generate_summary(self, prompt: str) -> str:
        try:
            token = self._get_access_token()
            logger.info(f"Calling GigaChat with prompt length {len(prompt)}")

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }

            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "Ты — ассистент, который делает краткие выжимки из текста на русском языке."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": settings.LLM_MAX_TOKENS,
                "temperature": settings.LLM_TEMPERATURE
            }

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()
            summary = result["choices"][0]["message"]["content"].strip()
            logger.info(f"GigaChat response received, length={len(summary)}")
            return summary

        except requests.exceptions.Timeout as e:
            logger.error(f"GigaChat timeout: {e}")
            raise TimeoutError("GigaChat request timed out")
        except requests.exceptions.RequestException as e:
            logger.error(f"GigaChat API error: {e}")
            raise ConnectionError("GigaChat API error")
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            logger.error(f"Invalid GigaChat response format: {e}")
            raise ValueError("Invalid response from GigaChat")
        except Exception as e:
            logger.error(f"Unexpected GigaChat error: {e}")
            raise