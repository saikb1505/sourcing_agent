import csv
import io
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.repositories.search_query_repository import SearchQueryRepository
from app.repositories.search_result_repository import SearchResultRepository
from app.services.openai_service import openai_service
from app.services.google_search_service import google_search_service
from app.services import serper_search_service 
from app.schemas.search_schema import (
    GenerateQueryRequest,
    GenerateQueryResponse,
    SearchQueryResponse,
    ExecuteSearchResponse,
)
from app.schemas.result_schema import (
    SearchResultResponse,
    SearchResultsListResponse,
)
from app.models.user import User
from app.core.config import settings

router = APIRouter(prefix="/api/search", tags=["Search"])


@router.post("/generate", response_model=GenerateQueryResponse)
async def generate_search_query(
    request: GenerateQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate an optimized search query from free-text input using OpenAI.

    This endpoint:
    1. Takes natural language input (e.g., "Find Ruby on Rails developers in Hyderabad")
    2. Uses OpenAI to generate an optimized LinkedIn/Google search query
    3. Saves both the input and generated query to the database
    """
    # Generate the optimized search query using OpenAI
    generated_query = openai_service.generate_search_query(request.user_input)

    # Save to database
    query_repo = SearchQueryRepository(db)
    db_query = query_repo.create(
        user_input=request.user_input,
        generated_query=generated_query,
        created_user_id=current_user.id,
    )

    return GenerateQueryResponse(
        id=db_query.id,
        user_input=db_query.user_input,
        generated_query=db_query.generated_query,
        created_at=db_query.created_at,
    )


@router.post("/execute/{query_id}", response_model=ExecuteSearchResponse)
async def execute_search(
    query_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Execute a saved search query using Google Custom Search API.

    This endpoint:
    1. Retrieves the saved search query
    2. Executes it via Google Custom Search (with pagination)
    3. Saves results to the database
    4. Updates the last_search_date and last_run_user

    Number of results is controlled by MAX_GOOGLE_SEARCH_RESULTS env variable (default 100).
    """
    query_repo = SearchQueryRepository(db)
    result_repo = SearchResultRepository(db)

    # Get the search query
    db_query = query_repo.get_by_id(query_id)
    if not db_query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search query not found",
        )

    # Execute the search with pagination
    search_results = google_search_service.search_multiple_pages(
        query=db_query.generated_query,
        total_results=settings.MAX_GOOGLE_SEARCH_RESULTS,
    )

    

    # Save results to database
    if search_results:
        result_repo.create_batch(
            search_query_id=query_id,
            results_payload=search_results,
            executed_by_user_id=current_user.id,
        )

    # Update last search info
    query_repo.update_last_search(query_id, current_user.id)

    # Get the latest result to return timestamp
    latest_result = result_repo.get_latest_by_query_id(query_id)

    return ExecuteSearchResponse(
        search_query_id=query_id,
        results_count=len(search_results),
        search_timestamp=latest_result.search_timestamp if latest_result else db_query.updated_at,
    )


@router.post("/generate-and-execute", response_model=ExecuteSearchResponse)
async def generate_and_execute_search(
    request: GenerateQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate a search query and immediately execute it.

    Combines the generate and execute steps into one API call.

    Number of results is controlled by MAX_GOOGLE_SEARCH_RESULTS env variable (default 100).
    """
    query_repo = SearchQueryRepository(db)
    result_repo = SearchResultRepository(db)

    # Generate the search query
    generated_query = openai_service.generate_search_query(request.user_input)

    # Save to database
    db_query = query_repo.create(
        user_input=request.user_input,
        generated_query=generated_query,
        created_user_id=current_user.id,
    )

    # Execute the search with pagination
    search_results = google_search_service.search_multiple_pages(
        query=generated_query,
        total_results=settings.MAX_GOOGLE_SEARCH_RESULTS,
    )

    # search_results = serper_search_service.search_multiple_pages(
    #     query=db_query.generated_query,
    #     total_results=settings.MAX_GOOGLE_SEARCH_RESULTS,
    # )


    # Save results
    if search_results:
        result_repo.create_batch(
            search_query_id=db_query.id,
            results_payload=search_results,
            executed_by_user_id=current_user.id,
        )

    # Update last search info
    query_repo.update_last_search(db_query.id, current_user.id)

    latest_result = result_repo.get_latest_by_query_id(db_query.id)

    return ExecuteSearchResponse(
        search_query_id=db_query.id,
        results_count=len(search_results),
        search_timestamp=latest_result.search_timestamp if latest_result else db_query.updated_at,
    )


@router.get("/queries", response_model=List[SearchQueryResponse])
async def get_my_queries(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all search queries created by the current user."""
    query_repo = SearchQueryRepository(db)
    queries = query_repo.get_by_user(current_user.id, skip=skip, limit=limit)
    return queries


@router.get("/queries/{query_id}", response_model=SearchQueryResponse)
async def get_query(
    query_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific search query by ID."""
    query_repo = SearchQueryRepository(db)
    db_query = query_repo.get_by_id(query_id)

    if not db_query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search query not found",
        )

    return db_query


@router.get("/queries/{query_id}/results", response_model=SearchResultsListResponse)
async def get_query_results(
    query_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all search results for a specific query."""
    query_repo = SearchQueryRepository(db)
    result_repo = SearchResultRepository(db)

    # Verify query exists
    db_query = query_repo.get_by_id(query_id)
    if not db_query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search query not found",
        )

    results = result_repo.get_by_query_id(query_id, skip=skip, limit=limit)
    total = result_repo.count_by_query_id(query_id)

    return SearchResultsListResponse(
        search_query_id=query_id,
        total_results=total,
        results=results,
    )


@router.delete("/queries/{query_id}")
async def delete_query(
    query_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a search query and all its results."""
    query_repo = SearchQueryRepository(db)

    db_query = query_repo.get_by_id(query_id)
    if not db_query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search query not found",
        )

    # Only allow deletion by creator or admin
    if db_query.created_user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this query",
        )

    query_repo.delete(query_id)
    return {"message": "Search query deleted successfully"}


@router.post("/results/{result_id}/enrich")
async def mark_result_enriched(
    result_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a search result as enriched (e.g., after scraping additional data)."""
    result_repo = SearchResultRepository(db)

    db_result = result_repo.get_by_id(result_id)
    if not db_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search result not found",
        )

    updated_result = result_repo.mark_enriched(result_id)

    return {
        "id": updated_result.id,
        "enriched_timestamp": updated_result.enriched_timestamp,
    }


@router.get("/queries/{query_id}/export")
async def export_query_results_to_csv(
    query_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Export search results for a specific query to CSV format.

    Returns a CSV file with columns:
    - user_input: The original search input from the user
    - generated_query: The optimized search query generated by OpenAI
    - name: Name extracted from the search result
    - snippet: Text snippet from the search result
    - linkedin_url: LinkedIn profile URL
    - created_time: When the search result was created
    """
    query_repo = SearchQueryRepository(db)
    result_repo = SearchResultRepository(db)

    # Verify query exists
    db_query = query_repo.get_by_id(query_id)
    if not db_query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search query not found",
        )

    # Get all results for this query (no pagination for export)
    results = result_repo.get_by_query_id(query_id, skip=0, limit=10000)

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        "user_input",
        "generated_query",
        "name",
        "snippet",
        "linkedin_url",
        "created_time",
    ])

    # Write data rows
    for result in results:
        writer.writerow([
            db_query.user_input,
            db_query.generated_query,
            result.name or "",
            result.snippet or "",
            result.linkedin_url or "",
            result.created_at.isoformat() if result.created_at else "",
        ])

    # Reset stream position
    output.seek(0)

    # Return as streaming response with CSV content type
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=search_results_{query_id}.csv"
        },
    )
