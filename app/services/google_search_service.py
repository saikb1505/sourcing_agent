from typing import List, Dict, Any, Optional
import httpx
from app.core.config import settings


class GoogleSearchService:
    """Service for executing searches via Google Custom Search API."""

    BASE_URL = "https://www.googleapis.com/customsearch/v1"

    def __init__(self):
        self.api_key = settings.GOOGLE_API_KEY
        self.cse_id = settings.GOOGLE_CSE_ID

    def execute_search(
        self,
        query: str,
        num_results: int = 10,
        start_index: int = 1,
    ) -> Dict[str, Any]:
        """
        Execute a search query using Google Custom Search API.

        Args:
            query: The search query string
            num_results: Number of results to return (max 10 per request)
            start_index: Starting index for pagination (1-based)

        Returns:
            Dictionary containing search results and metadata
        """
        params = {
            "key": self.api_key,
            "cx": self.cse_id,
            "q": query,
            "num": min(num_results, 10),  # API limit is 10 per request
            "start": start_index,
        }

        with httpx.Client(timeout=30.0) as client:
            response = client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            return response.json()

    def search_and_parse(
        self,
        query: str,
        num_results: int = 10,
        start_index: int = 1,
    ) -> List[Dict[str, Any]]:
        """
        Execute search and parse results into a clean format.

        Args:
            query: The search query string
            num_results: Number of results to return
            start_index: Starting index for pagination

        Returns:
            List of parsed search result items
        """
        raw_results = self.execute_search(query, num_results, start_index)
        items = raw_results.get("items", [])
        parsed_results = []

        for item in items:
            # Extract name and description from pagemap metatags
            pagemap = item.get("pagemap", {})
            metatags = pagemap.get("metatags", [{}])
            metatag = metatags[0] if metatags else {}

            # Extract name from profile metatags
            first_name = metatag.get("profile:first_name", "")
            last_name = metatag.get("profile:last_name", "")
            name = f"{first_name} {last_name}".strip() if first_name or last_name else ""

            # Extract description from og:description or twitter:description
            description = metatag.get("og:description", "") or metatag.get("twitter:description", "")

            parsed_item = {
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "display_link": item.get("displayLink", ""),
                "formatted_url": item.get("formattedUrl", ""),
                "html_snippet": item.get("htmlSnippet", ""),
                "cache_id": item.get("cacheId"),
                "pagemap": pagemap,
                "name": name,
                "description": description,
            }
            parsed_results.append(parsed_item)

        return parsed_results

    def search_multiple_pages(
        self,
        query: str,
        total_results: int = 30,
    ) -> List[Dict[str, Any]]:
        """
        Execute search across multiple pages to get more results.

        Note: Google Custom Search API allows max 100 results per query (10 pages of 10).
        Free tier is limited to 100 queries per day.

        Args:
            query: The search query string
            total_results: Total number of results desired (max 100)

        Returns:
            List of all parsed search result items
        """
        all_results = []
        total_results = min(total_results, 100)  # API limit

        for start in range(1, total_results + 1, 10):
            num_to_fetch = min(10, total_results - start + 1)

            try:
                results = self.search_and_parse(query, num_to_fetch, start)
                all_results.extend(results)

                # If we got fewer results than requested, there are no more
                if len(results) < num_to_fetch:
                    break
            except httpx.HTTPStatusError as e:
                # Log error but return what we have so far
                print(f"Error fetching page starting at {start}: {e}")
                break

        return all_results

    def get_search_metadata(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata about a search query without fetching results.

        Args:
            query: The search query string

        Returns:
            Dictionary containing search metadata or None if error
        """
        try:
            raw_results = self.execute_search(query, num_results=1)
            search_info = raw_results.get("searchInformation", {})
            return {
                "total_results": search_info.get("totalResults", "0"),
                "search_time": search_info.get("searchTime", 0),
                "formatted_total_results": search_info.get("formattedTotalResults", "0"),
                "formatted_search_time": search_info.get("formattedSearchTime", "0"),
            }
        except Exception:
            return None


# Singleton instance for easy import
google_search_service = GoogleSearchService()
