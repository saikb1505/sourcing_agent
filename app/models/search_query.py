from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class SearchQuery(Base):
    __tablename__ = "search_queries"

    id = Column(Integer, primary_key=True, index=True)
    user_input = Column(Text, nullable=False)
    generated_query = Column(Text, nullable=False)
    last_search_date = Column(DateTime(timezone=True), nullable=True)
    created_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    last_run_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    created_user = relationship(
        "User", back_populates="created_search_queries", foreign_keys=[created_user_id]
    )
    last_run_user = relationship(
        "User",
        back_populates="last_run_search_queries",
        foreign_keys=[last_run_user_id],
    )
    search_results = relationship(
        "SearchResult", back_populates="search_query", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<SearchQuery(id={self.id}, user_input={self.user_input[:50]}...)>"
