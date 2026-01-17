from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    created_search_queries = relationship(
        "SearchQuery",
        back_populates="created_user",
        foreign_keys="SearchQuery.created_user_id",
    )
    last_run_search_queries = relationship(
        "SearchQuery",
        back_populates="last_run_user",
        foreign_keys="SearchQuery.last_run_user_id",
    )
    search_results = relationship("SearchResult", back_populates="executed_by_user")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"
