"""Compatibility shim for core domain models."""

from remediation_search.core.domain_models import (
    ChunkMetadata,
    DocumentChunk,
    ProcessingResult,
    RemediationMatch,
    RemediationResult,
)

__all__ = [
    "ChunkMetadata",
    "DocumentChunk",
    "RemediationMatch",
    "RemediationResult",
    "ProcessingResult",
]

