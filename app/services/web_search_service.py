import logging
from tavily import TavilyClient

from app.config.settings import settings

logger = logging.getLogger(__name__)


class WebSearchService:
    """
    Wrapper around Tavily Search API.
    """

    def __init__(self):
        self.client = TavilyClient(api_key=settings.TAVILY_API_KEY)

    def search(
        self,
        query: str,
        max_results: int,
    ) -> list[dict]:

        logger.info("Searching web for: %s", query)

        response = self.client.search(
            query=query,
            max_results=max_results,
        )

        return response.get("results", [])