"""Pydantic schemas for API request and response models."""

from typing import List, Optional

from pydantic import BaseModel, Field


class RemediationRequest(BaseModel):
    """Request payload for remediation lookup."""

    alert_name: Optional[str] = Field(
        default=None,
        description="UI alert name, used as fallback context if root_cause is omitted.",
        examples=["Kubernetes Pod Pending Alert"],
    )
    root_cause: Optional[str] = Field(
        default=None,
        description="Root cause text to search for remediation steps.",
        examples=["pod in pending"],
    )
    limit: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum number of remediation steps to return.",
    )


class RemediationStep(BaseModel):
    """Single remediation step returned to the UI."""

    rank: int
    score: int
    source: str
    chunk_id: str
    content: str


class RemediationResponse(BaseModel):
    """Response payload for remediation lookup."""

    alert_name: str
    root_cause: str
    status: str
    steps: List[RemediationStep]
    message: str


class IngestionResponse(BaseModel):
    """Response payload for document ingestion."""

    status: str
    filename: str
    chunks_saved: int
    output_dir: str
    message: str


class HealthResponse(BaseModel):
    """Service health response model."""

    status: str
    service: str
    version: str
