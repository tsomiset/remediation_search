"""Compatibility shim for document processing services."""

from remediation_search.services.document_processor import (
    DEFAULT_CHUNKS_DIR,
    SUPPORTED_EXTENSIONS,
    is_supported_document,
    load_documents,
    process_document,
    save_chunks_locally,
)

__all__ = [
    "SUPPORTED_EXTENSIONS",
    "DEFAULT_CHUNKS_DIR",
    "is_supported_document",
    "load_documents",
    "save_chunks_locally",
    "process_document",
]

