from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class SearchResult(Base):
    __tablename__ = "search_results"

    id = Column(Integer, primary_key=True, index=True)
    search_query_id = Column(
        Integer, ForeignKey("search_queries.id"), nullable=False, index=True
    )
    linkedin_url = Column(String(768), nullable=True, index=True)
    name = Column(String(512), nullable=True)
    snippet = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    result_payload = Column(JSON, nullable=False)
    search_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    enriched_timestamp = Column(DateTime(timezone=True), nullable=True)
    executed_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    search_query = relationship("SearchQuery", back_populates="search_results")
    executed_by_user = relationship("User", back_populates="search_results")

    def __repr__(self):
        return f"<SearchResult(id={self.id}, search_query_id={self.search_query_id})>"
