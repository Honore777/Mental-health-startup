import asyncio

import httpx

from app.core.config import get_settings
from app.services.retry import async_retry


class LLMOrchestratorSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._client = httpx.AsyncClient(timeout=30.0)
        return cls._instance

    async def _call_gemini(self, prompt: str) -> str:
        settings = get_settings()
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured")

        endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        response = await self._client.post(
            endpoint,
            params={"key": settings.gemini_api_key},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.2},
            },
        )
        response.raise_for_status()
        payload = response.json()
        return payload["candidates"][0]["content"]["parts"][0]["text"]

    async def _call_chatgroq(self, prompt: str) -> str:
        settings = get_settings()
        if not settings.chatgroq_api_key:
            raise RuntimeError("CHATGROQ_API_KEY is not configured")

        response = await self._client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.chatgroq_api_key}"},
            json={
                "model": "llama-3.3-70b-versatile",
                "temperature": 0.2,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        response.raise_for_status()
        payload = response.json()
        return payload["choices"][0]["message"]["content"]

    async def generate(self, prompt: str) -> str:
        settings = get_settings()

        async def primary_operation() -> str:
            return await asyncio.wait_for(self._call_gemini(prompt), timeout=settings.primary_llm_timeout_seconds)

        async def fallback_operation() -> str:
            return await asyncio.wait_for(self._call_chatgroq(prompt), timeout=settings.fallback_llm_timeout_seconds)

        try:
            return await async_retry(
                operation=primary_operation,
                attempts=settings.llm_retry_attempts,
                base_delay=settings.llm_retry_base_delay_seconds,
                max_delay=settings.llm_retry_max_delay_seconds,
            )
        except Exception:  # noqa: BLE001
            return await async_retry(
                operation=fallback_operation,
                attempts=settings.llm_retry_attempts,
                base_delay=settings.llm_retry_base_delay_seconds,
                max_delay=settings.llm_retry_max_delay_seconds,
            )


def get_llm_orchestrator() -> LLMOrchestratorSingleton:
    return LLMOrchestratorSingleton()
