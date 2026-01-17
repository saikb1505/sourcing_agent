from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any, List


class SearchResultBase(BaseModel):
    search_query_id: int
    result_payload: Any


class SearchResultCreate(SearchResultBase):
    executed_by_user_id: int


class SearchResultResponse(SearchResultBase):
    id: int
    search_timestamp: datetime
    enriched_timestamp: Optional[datetime] = None
    executed_by_user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class SearchResultItem(BaseModel):
    title: str
    link: str
    snippet: Optional[str] = None
    display_link: Optional[str] = None


class SearchResultsListResponse(BaseModel):
    search_query_id: int
    total_results: int
    results: List[SearchResultResponse]


class EnrichResultRequest(BaseModel):
    result_id: int


class EnrichResultResponse(BaseModel):
    id: int
    enriched_timestamp: datetime
