"""Compatibility shim for legacy remediation lookup helpers."""

from remediation_search.legacy.remediation_finder import (
    CHUNKS_DIR,
    build_response,
    find_remediation,
    load_chunks,
    tokenize,
)

__all__ = [
    "CHUNKS_DIR",
    "tokenize",
    "load_chunks",
    "find_remediation",
    "build_response",
]

