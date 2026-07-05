"""Compatibility shim for input processing orchestration."""

from remediation_search.processing.input_processor import (
    get_usage_text,
    process_input,
)

__all__ = ["process_input", "get_usage_text"]

