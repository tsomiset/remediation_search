"""Compatibility API for remediation lookup utilities."""

import re
from pathlib import Path

from remediation_search.core.domain_models import (
    ChunkMetadata,
    DocumentChunk,
    RemediationMatch,
    RemediationResult,
)
from remediation_search.formatters.response_formatter import DetailedResponseFormatter
from remediation_search.services.chunking_service import ChunkingService
from remediation_search.strategies.matching_strategy import CompositeMatchingStrategy

CHUNKS_DIR = Path("outputs") / "processed_chunks"
TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9_]+")


def tokenize(text):
    """Legacy tokenizer used by tests and callers."""
    return {
        token.lower()
        for token in TOKEN_PATTERN.findall(text)
        if len(token) > 2
    }


def load_chunks(chunks_dir=CHUNKS_DIR):
    """Load chunk files and return legacy dict format."""
    service = ChunkingService(Path(chunks_dir))
    chunks = service.load_chunks()
    return [
        {
            "chunk_id": chunk.chunk_id,
            "content": chunk.content,
            "metadata": {
                "source": chunk.metadata.source,
                "file_type": chunk.metadata.file_type,
            },
            "path": Path(chunks_dir) / f"chunk_{int(chunk.chunk_id):03d}.json",
        }
        for chunk in chunks
    ]


def _to_domain_chunk(document):
    return DocumentChunk(
        chunk_id=str(document.get("chunk_id", "")),
        content=document.get("content", ""),
        metadata=ChunkMetadata(
            source=document.get("metadata", {}).get("source", "Unknown"),
            file_type=document.get("metadata", {}).get("file_type", "unknown"),
        ),
    )


def find_remediation(root_cause, documents, limit=3):
    """Find remediation from provided documents (legacy behavior)."""
    strategy = CompositeMatchingStrategy()
    scored = []

    for document in documents:
        chunk = _to_domain_chunk(document)
        score = strategy.score(root_cause, chunk)
        if score > 0:
            scored.append(RemediationMatch(score=score, chunk=chunk))

    scored.sort(key=lambda item: (-item.score, item.chunk.chunk_id))

    return [
        {
            "chunk_id": int(match.chunk.chunk_id) if str(match.chunk.chunk_id).isdigit() else match.chunk.chunk_id,
            "content": match.chunk.content,
            "metadata": {
                "source": match.chunk.metadata.source,
                "file_type": match.chunk.metadata.file_type,
            },
        }
        for match in scored[:limit]
    ]


def build_response(root_cause, matched_chunks):
    """Build formatted response using the categorized formatter layer."""
    matches = tuple(
        RemediationMatch(
            score=0,
            chunk=_to_domain_chunk(chunk),
        )
        for chunk in matched_chunks
    )

    alert_name = root_cause
    if matched_chunks:
        alert_name = matched_chunks[0].get("metadata", {}).get("source", root_cause)

    result = RemediationResult(
        alert_name=alert_name,
        root_cause=root_cause,
        matches=matches,
    )
    return DetailedResponseFormatter().format(result)


__all__ = [
    "CHUNKS_DIR",
    "tokenize",
    "load_chunks",
    "find_remediation",
    "build_response",
]

