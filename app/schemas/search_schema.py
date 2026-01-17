from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SearchQueryBase(BaseModel):
    user_input: str


class SearchQueryCreate(SearchQueryBase):
    pass


class SearchQueryResponse(SearchQueryBase):
    id: int
    generated_query: str
    last_search_date: Optional[datetime] = None
    created_user_id: int
    last_run_user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SearchQueryWithResults(SearchQueryResponse):
    results_count: int = 0


class GenerateQueryRequest(BaseModel):
    user_input: str


class GenerateQueryResponse(BaseModel):
    id: int
    user_input: str
    generated_query: str
    created_at: datetime


class ExecuteSearchRequest(BaseModel):
    search_query_id: int


class ExecuteSearchResponse(BaseModel):
    search_query_id: int
    results_count: int
    search_timestamp: datetime
