from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.search_query import SearchQuery


class SearchQueryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, query_id: int) -> Optional[SearchQuery]:
        """Get search query by ID."""
        return self.db.query(SearchQuery).filter(SearchQuery.id == query_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[SearchQuery]:
        """Get all search queries with pagination."""
        return (
            self.db.query(SearchQuery)
            .order_by(SearchQuery.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[SearchQuery]:
        """Get all search queries created by a specific user."""
        return (
            self.db.query(SearchQuery)
            .filter(SearchQuery.created_user_id == user_id)
            .order_by(SearchQuery.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_generated_query(self, generated_query: str) -> Optional[SearchQuery]:
        """Get search query by generated query text."""
        return (
            self.db.query(SearchQuery)
            .filter(SearchQuery.generated_query == generated_query)
            .first()
        )

    def create(
        self, user_input: str, generated_query: str, created_user_id: int
    ) -> SearchQuery:
        """Create or update search query with deduplication based on generated_query."""
        # Check for existing query with same generated_query
        existing_query = self.get_by_generated_query(generated_query)

        if existing_query:
            # Update existing record
            existing_query.user_input = user_input
            existing_query.last_search_date = datetime.now(timezone.utc)
            existing_query.last_run_user_id = created_user_id
            self.db.commit()
            self.db.refresh(existing_query)
            return existing_query

        # Create new record
        db_query = SearchQuery(
            user_input=user_input,
            generated_query=generated_query,
            created_user_id=created_user_id,
        )
        self.db.add(db_query)
        self.db.commit()
        self.db.refresh(db_query)
        return db_query

    def update_last_search(
        self, query_id: int, last_run_user_id: int
    ) -> Optional[SearchQuery]:
        """Update the last search date and user."""
        db_query = self.get_by_id(query_id)
        if not db_query:
            return None

        db_query.last_search_date = datetime.now(timezone.utc)
        db_query.last_run_user_id = last_run_user_id
        self.db.commit()
        self.db.refresh(db_query)
        return db_query

    def update_generated_query(
        self, query_id: int, new_generated_query: str
    ) -> Optional[SearchQuery]:
        """Update the generated query text."""
        db_query = self.get_by_id(query_id)
        if not db_query:
            return None

        db_query.generated_query = new_generated_query
        self.db.commit()
        self.db.refresh(db_query)
        return db_query

    def delete(self, query_id: int) -> bool:
        """Delete a search query."""
        db_query = self.get_by_id(query_id)
        if not db_query:
            return False

        self.db.delete(db_query)
        self.db.commit()
        return True

    def search_by_user_input(
        self, search_term: str, skip: int = 0, limit: int = 100
    ) -> List[SearchQuery]:
        """Search queries by user input text (case-insensitive)."""
        return (
            self.db.query(SearchQuery)
            .filter(func.lower(SearchQuery.user_input).like(f"%{search_term.lower()}%"))
            .order_by(SearchQuery.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
