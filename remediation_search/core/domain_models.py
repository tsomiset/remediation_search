"""Core domain models and entities."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class ChunkMetadata:
    """Metadata associated with a document chunk."""
    source: str
    file_type: str
    
    def __str__(self) -> str:
        return f"{self.source} ({self.file_type})"


@dataclass(frozen=True)
class DocumentChunk:
    """Represents a chunk of a document."""
    chunk_id: str
    content: str
    metadata: ChunkMetadata
    
    def __str__(self) -> str:
        return f"[{self.chunk_id}] {self.metadata}"


@dataclass(frozen=True)
class RemediationMatch:
    """A single remediation match result."""
    score: int
    chunk: DocumentChunk
    
    def __str__(self) -> str:
        return f"Score: {self.score} | {self.chunk}"


@dataclass(frozen=True)
class RemediationResult:
    """Complete remediation lookup result."""
    alert_name: str
    root_cause: str
    matches: tuple  # List of RemediationMatch
    
    def has_matches(self) -> bool:
        return bool(self.matches)
    
    def match_count(self) -> int:
        return len(self.matches)


@dataclass(frozen=True)
class ProcessingResult:
    """Result of input processing (file or query)."""
    success: bool
    message: str
    error: Optional[str] = None
    
    @classmethod
    def success_result(cls, message: str) -> "ProcessingResult":
        return cls(success=True, message=message)
    
    @classmethod
    def failure_result(cls, error: str) -> "ProcessingResult":
        return cls(success=False, message="", error=error)
