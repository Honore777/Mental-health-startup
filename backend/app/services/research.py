import httpx

from app.core.config import get_settings


class TavilyResearchService:
    BASE_URL = "https://api.tavily.com/search"

    def __init__(self):
        self.settings = get_settings()

    async def search(self, query: str) -> list[dict]:
        if not self.settings.tavily_api_key:
            return []

        payload = {
            "api_key": self.settings.tavily_api_key,
            "query": query,
            "search_depth": "advanced",
            "max_results": self.settings.tavily_max_results,
            "topic": "general",
            "include_answer": False,
            "include_images": False,
        }

        try:
            async with httpx.AsyncClient(timeout=self.settings.tavily_timeout_seconds) as client:
                response = await client.post(self.BASE_URL, json=payload)
                response.raise_for_status()
                data = response.json()
        except Exception:  # noqa: BLE001
            return []

        results = data.get("results", [])
        normalized: list[dict] = []
        for item in results:
            normalized.append(
                {
                    "source": item.get("title") or item.get("url") or "External source",
                    "url": item.get("url", ""),
                    "content": item.get("content", ""),
                }
            )
        return normalized


def get_research_service() -> TavilyResearchService:
    return TavilyResearchService()
