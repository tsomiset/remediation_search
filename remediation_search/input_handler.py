"""Compatibility shim for input handlers."""

from remediation_search.handlers.input_handler import (
    FileInputHandler,
    InputHandler,
    InputHandlerChain,
    QueryInputHandler,
)

__all__ = [
    "InputHandler",
    "FileInputHandler",
    "QueryInputHandler",
    "InputHandlerChain",
]

