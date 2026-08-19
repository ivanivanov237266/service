# tests/test_api.py
from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)

def test_valid_request(mocker):
    # Мокаем вызов GigaChat
    mocker.patch(
        'services.summarization.LLMClient.generate_summary',
        return_value="Это тестовая суммаризация текста. Она содержит основные идеи."
    )
    response = client.post(
        "/api/v1/summarize",
        json={"text": "Длинный текст для тестирования. " * 30}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == "Это тестовая суммаризация текста. Она содержит основные идеи."
    assert data["status"] == "success"

def test_invalid_request():
    response = client.post("/api/v1/summarize", json={"text": "короткий"})
    assert response.status_code == 422

def test_fallback_on_llm_error(mocker):
    mocker.patch(
        'services.summarization.LLMClient.generate_summary',
        side_effect=ConnectionError("GigaChat API error")
    )
    text = "Это достаточно длинный текст для проверки fallback механизма. " * 10
    response = client.post("/api/v1/summarize", json={"text": text})
    assert response.status_code == 200
    assert response.json()["status"] == "fallback"