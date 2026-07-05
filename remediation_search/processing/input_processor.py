"""
Input processing module for detecting and routing user input.

Uses handler chain pattern with dependency injection
for clean separation of concerns.
"""

import sys
from pathlib import Path

from remediation_search.services.document_processor import SUPPORTED_EXTENSIONS
from remediation_search.handlers.input_handler import InputHandlerChain


def process_input(raw_input: str) -> None:
    """
    Main input processor: classify and route to appropriate handler.
    
    Args:
        raw_input: User-provided input string
        
    Raises:
        Exception: If input processing or handling fails
    """
    if not raw_input or not raw_input.strip():
        raise ValueError("Input cannot be empty")
    
    handler_chain = InputHandlerChain()
    
    try:
        handler_chain.handle(raw_input)
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")
        sys.exit(1)
    except Exception as error:
        print(f"Unexpected error: {error}")
        sys.exit(1)


def get_usage_text() -> str:
    """Return the usage help text."""
    return f"""
Usage:
  python -m remediation_search <input>

Examples:
  python -m remediation_search "Pod(s)inPendingState.docx"  # Process a document
  python -m remediation_search "Pod Pending State"           # Find remediation steps

Supported document types: {", ".join(sorted(SUPPORTED_EXTENSIONS))}
""".strip()

