from typing import List, Dict, Any, Optional
import httpx
from app.core.config import settings


class SerperSearchService:
    """Service for executing searches via Serper API (Google Search API alternative)."""

    BASE_URL = "https://google.serper.dev/search"

    def __init__(self):
        self.api_key = settings.SERPER_API_KEY

    def execute_search(
        self,
        query: str,
        num_results: int = 10,
        page: int = 1,
    ) -> Dict[str, Any]:
        """
        Execute a search query using Serper API.

        Args:
            query: The search query string
            num_results: Number of results to return (max 100 per request)
            page: Page number for pagination (1-based)

        Returns:
            Dictionary containing search results and metadata
        """
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }

        payload = {
            "q": query,
            "page": page,
        }

        with httpx.Client(timeout=30.0) as client:
            response = client.post(self.BASE_URL, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()

    def search_and_parse(
        self,
        query: str,
        num_results: int = 10,
        page: int = 1,
    ) -> List[Dict[str, Any]]:
        """
        Execute search and parse results into a clean format.

        Args:
            query: The search query string
            num_results: Number of results to return
            page: Page number for pagination

        Returns:
            List of parsed search result items
        """
        raw_results = self.execute_search(query, num_results, page)
        items = raw_results.get("organic", [])
        parsed_results = []

        for item in items:
            # Extract metatags from pagemap
            metatags = {}
            pagemap = item.get("pagemap", {})
            metatags_list = pagemap.get("metatags", [])
            if metatags_list:
                metatags = metatags_list[0]
    
            first_name = metatags.get("profile:first_name", "")
            last_name = metatags.get("profile:last_name", "")
            name = f"{first_name} {last_name}".strip()


            parsed_item = {
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "name": name,
                "og_description": metatags.get("og:description", ""),
                "display_link": item.get("displayLink", ""),
                "formatted_url": item.get("link", ""),
                "position": item.get("position"),
                "date": item.get("date"),
                "sitelinks": item.get("sitelinks", []),
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

        Args:
            query: The search query string
            total_results: Total number of results desired

        Returns:
            List of all parsed search result items
        """
        all_results = []
        results_per_page = 10
        pages_needed = (total_results + results_per_page - 1) // results_per_page

        for page in range(1, pages_needed + 1):
            try:
                results = self.search_and_parse(query, results_per_page, page)
                all_results.extend(results)

                # If we got fewer results than requested, there are no more
                # if len(results) < results_per_page:
                #     break

                # Stop if we have enough results
                if len(all_results) >= total_results:
                    break
            except httpx.HTTPStatusError as e:
                print(f"Error fetching page {page}: {e}")
                break

        return all_results[:total_results]

    def get_search_metadata(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata about a search query.

        Args:
            query: The search query string

        Returns:
            Dictionary containing search metadata or None if error
        """
        try:
            raw_results = self.execute_search(query, num_results=1)
            search_params = raw_results.get("searchParameters", {})
            return {
                "query": search_params.get("q", ""),
                "type": search_params.get("type", "search"),
                "engine": search_params.get("engine", "google"),
                "credits_used": raw_results.get("credits", 1),
            }
        except Exception:
            return None


# Singleton instance for easy import
serper_search_service = SerperSearchService()
