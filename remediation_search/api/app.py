"""FastAPI application exposing remediation backend endpoints."""

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status

from remediation_search.api.dependencies import require_api_key
from remediation_search.api.schemas import (
    HealthResponse,
    RemediationRequest,
    RemediationResponse,
    RemediationStep,
)
from remediation_search.services.remediation_service import RemediationService

app = FastAPI(
    title="Remediation_Search API",
    description="Backend API for alert-based remediation lookup.",
    version="0.1.0",
)


def run() -> None:
    """Run the API server via console script."""
    uvicorn.run("remediation_search.api.app:app", host="0.0.0.0", port=8000, reload=False)


@app.get("/api/remediation/search", response_model=RemediationResponse)
def get_remediation_by_query(
    query: str,
    limit: int = 3,
    _auth: None = Depends(require_api_key),
) -> RemediationResponse:
    """
    Langflow-friendly GET endpoint. Pass query as a URL parameter.

    Example: GET /api/remediation/search?query=pod+in+pending&limit=3
    """
    query_text = query.strip()
    if not query_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="query parameter must not be empty.",
        )

    service = RemediationService(result_limit=limit)

    try:
        result = service.find_remediation(query_text)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No processed chunks found. Ingest a document first.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid chunk data: {exc}",
        ) from exc

    steps = [
        RemediationStep(
            rank=index,
            score=match.score,
            source=match.chunk.metadata.source,
            chunk_id=str(match.chunk.chunk_id),
            content=match.chunk.content,
        )
        for index, match in enumerate(result.matches, start=1)
    ]

    if steps:
        status_text = "success"
        message = f"Found {len(steps)} remediation step(s)."
    else:
        status_text = "no_matches"
        message = "No remediation steps matched the provided alert context."

    return RemediationResponse(
        alert_name=result.alert_name,
        root_cause=result.root_cause,
        status=status_text,
        steps=steps,
        message=message,
    )


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Liveness endpoint for probes and monitoring."""
    return HealthResponse(
        status="ok",
        service="Remediation_Search",
        version="0.1.0",
    )


@app.post("/api/remediation", response_model=RemediationResponse)
def get_remediation(
    request: RemediationRequest,
    _auth: None = Depends(require_api_key),
) -> RemediationResponse:
    """
    Return remediation steps for a UI alert.

    Priority for query text:
    1. request.root_cause
    2. request.alert_name
    """
    query_text = (request.root_cause or request.alert_name or "").strip()
    if not query_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Either root_cause or alert_name must be provided.",
        )

    service = RemediationService(result_limit=request.limit)

    try:
        result = service.find_remediation(query_text)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No processed chunks found. Ingest a document first.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid chunk data: {exc}",
        ) from exc

    steps = [
        RemediationStep(
            rank=index,
            score=match.score,
            source=match.chunk.metadata.source,
            chunk_id=str(match.chunk.chunk_id),
            content=match.chunk.content,
        )
        for index, match in enumerate(result.matches, start=1)
    ]

    if steps:
        status_text = "success"
        message = f"Found {len(steps)} remediation step(s)."
    else:
        status_text = "no_matches"
        message = "No remediation steps matched the provided alert context."

    return RemediationResponse(
        alert_name=result.alert_name,
        root_cause=result.root_cause,
        status=status_text,
        steps=steps,
        message=message,
    )

