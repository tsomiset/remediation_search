"""
Input handlers for processing different input types.

Implements strategy pattern with pluggable handlers
for file and query inputs.
"""

from abc import ABC, abstractmethod
from pathlib import Path

from remediation_search.services.document_processor import (
    SUPPORTED_EXTENSIONS,
    is_supported_document,
    process_document,
)
from remediation_search.services.remediation_service import RemediationService
from remediation_search.formatters.response_formatter import FormatterFactory


class InputHandler(ABC):
    """Abstract base class for input handlers."""
    
    @abstractmethod
    def can_handle(self, raw_input: str) -> bool:
        """
        Check if this handler can process the input.
        
        Args:
            raw_input: The raw user input
            
        Returns:
            True if this handler can process it
        """
        pass
    
    @abstractmethod
    def handle(self, raw_input: str) -> None:
        """
        Process the input.
        
        Args:
            raw_input: The raw user input
            
        Raises:
            Exception: If processing fails
        """
        pass


class FileInputHandler(InputHandler):
    """Handler for processing document files."""
    
    def can_handle(self, raw_input: str) -> bool:
        """Check if input is a file path."""
        candidate = Path(raw_input)
        
        # Existing file
        if candidate.exists() and candidate.is_file():
            return True
        
        # Non-existing file with supported extension
        if is_supported_document(raw_input):
            return True
        
        return False
    
    def handle(self, raw_input: str) -> None:
        """Process document file."""
        candidate = Path(raw_input)
        
        if not candidate.exists():
            raise FileNotFoundError(f"File not found: {raw_input}")
        
        if not candidate.is_file():
            raise ValueError(f"Not a file: {raw_input}")
        
        print(f"Processing document: {candidate.name}")
        process_document(candidate)
        print("✓ Document ingestion complete")


class QueryInputHandler(InputHandler):
    """Handler for processing remediation queries."""
    
    def __init__(
        self,
        remediation_service: RemediationService = None,
        formatter_type: str = "detailed"
    ):
        """
        Initialize the query handler.
        
        Args:
            remediation_service: Service for finding remediations
            formatter_type: Response formatter type
        """
        self.remediation_service = remediation_service or RemediationService()
        self.formatter = FormatterFactory.create(formatter_type)
    
    def can_handle(self, raw_input: str) -> bool:
        """Query handler can handle any non-file input."""
        return True
    
    def handle(self, raw_input: str) -> None:
        """Process query and find remediations."""
        print(f"Searching for remediation steps for: '{raw_input}'")
        print("Processing...\n")
        
        try:
            result = self.remediation_service.find_remediation(raw_input)
            formatted = self.formatter.format(result)
            print(formatted)
        except FileNotFoundError:
            raise FileNotFoundError(
                "No processed chunks found. Ingest a document first:\n"
                f'  python -m remediation_search "YourDocument.docx"'
            )
        except ValueError as error:
            raise ValueError(f"Query processing error: {error}")


class InputHandlerChain:
    """Chain of responsibility for input handlers."""
    
    def __init__(self, handlers: list = None):
        """
        Initialize with handlers.
        
        Args:
            handlers: List of InputHandler instances
        """
        self.handlers = handlers or [
            FileInputHandler(),
            QueryInputHandler()
        ]
    
    def add_handler(self, handler: InputHandler) -> "InputHandlerChain":
        """Add a handler to the chain."""
        self.handlers.insert(0, handler)
        return self
    
    def handle(self, raw_input: str) -> None:
        """
        Process input using first matching handler.
        
        Args:
            raw_input: The raw user input
            
        Raises:
            ValueError: If no handler can process input
            Exception: If handler raises an error
        """
        for handler in self.handlers:
            if handler.can_handle(raw_input):
                handler.handle(raw_input)
                return
        
        raise ValueError(f"No handler found for input: {raw_input}")

