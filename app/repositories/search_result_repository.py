from typing import Optional, List, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.search_result import SearchResult


class SearchResultRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, result_id: int) -> Optional[SearchResult]:
        """Get search result by ID."""
        return self.db.query(SearchResult).filter(SearchResult.id == result_id).first()

    def get_by_query_id(
        self, query_id: int, skip: int = 0, limit: int = 100
    ) -> List[SearchResult]:
        """Get all search results for a specific query."""
        return (
            self.db.query(SearchResult)
            .filter(SearchResult.search_query_id == query_id)
            .order_by(SearchResult.search_timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_latest_by_query_id(self, query_id: int) -> Optional[SearchResult]:
        """Get the most recent search result for a query."""
        return (
            self.db.query(SearchResult)
            .filter(SearchResult.search_query_id == query_id)
            .order_by(SearchResult.search_timestamp.desc())
            .first()
        )

    def get_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[SearchResult]:
        """Get all search results executed by a specific user."""
        return (
            self.db.query(SearchResult)
            .filter(SearchResult.executed_by_user_id == user_id)
            .order_by(SearchResult.search_timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(
        self, search_query_id: int, result_payload: Any, executed_by_user_id: int
    ) -> SearchResult:
        """Create a new search result."""
        db_result = SearchResult(
            search_query_id=search_query_id,
            result_payload=result_payload,
            executed_by_user_id=executed_by_user_id,
        )
        self.db.add(db_result)
        self.db.commit()
        self.db.refresh(db_result)
        return db_result

    def get_by_linkedin_url(self, linkedin_url: str) -> Optional[SearchResult]:
        """Get search result by LinkedIn URL."""
        if not linkedin_url:
            return None
        return (
            self.db.query(SearchResult)
            .filter(SearchResult.linkedin_url == linkedin_url)
            .first()
        )

    def create_batch(
        self,
        search_query_id: int,
        results_payload: List[Any],
        executed_by_user_id: int,
    ) -> List[SearchResult]:
        """Create or update search results with deduplication based on linkedin_url."""
        db_results = []
        for payload in results_payload:
            linkedin_url = payload.get("link", "")

            # Check for existing record by linkedin_url
            existing_result = self.get_by_linkedin_url(linkedin_url) if linkedin_url else None

            if existing_result:
                # Update existing record
                existing_result.snippet = payload.get("snippet", "")
                existing_result.description = payload.get("description", "")
                existing_result.search_timestamp = datetime.now(timezone.utc)
                existing_result.result_payload = payload
                existing_result.executed_by_user_id = executed_by_user_id
                db_results.append(existing_result)
            else:
                # Create new record
                db_result = SearchResult(
                    search_query_id=search_query_id,
                    linkedin_url=linkedin_url,
                    name=payload.get("name", ""),
                    snippet=payload.get("snippet", ""),
                    description=payload.get("description", ""),
                    result_payload=payload,
                    executed_by_user_id=executed_by_user_id,
                )
                self.db.add(db_result)
                db_results.append(db_result)

        self.db.commit()
        for result in db_results:
            self.db.refresh(result)
        return db_results

    def mark_enriched(self, result_id: int) -> Optional[SearchResult]:
        """Mark a search result as enriched."""
        db_result = self.get_by_id(result_id)
        if not db_result:
            return None

        db_result.enriched_timestamp = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(db_result)
        return db_result

    def delete(self, result_id: int) -> bool:
        """Delete a search result."""
        db_result = self.get_by_id(result_id)
        if not db_result:
            return False

        self.db.delete(db_result)
        self.db.commit()
        return True

    def delete_by_query_id(self, query_id: int) -> int:
        """Delete all search results for a query. Returns count of deleted items."""
        deleted_count = (
            self.db.query(SearchResult)
            .filter(SearchResult.search_query_id == query_id)
            .delete()
        )
        self.db.commit()
        return deleted_count

    def count_by_query_id(self, query_id: int) -> int:
        """Count search results for a specific query."""
        return (
            self.db.query(SearchResult)
            .filter(SearchResult.search_query_id == query_id)
            .count()
        )
