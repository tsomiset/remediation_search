"""Legacy API for backward compatibility."""

from remediation_search.legacy.remediation_finder import (
    CHUNKS_DIR,
    build_response,
    find_remediation,
    load_chunks,
    tokenize,
)

__all__ = [
    "load_chunks",
    "find_remediation",
    "build_response",
    "CHUNKS_DIR",
    "tokenize",
]

