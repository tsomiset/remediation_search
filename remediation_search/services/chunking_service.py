"""
Chunking service for loading and managing document chunks.

Responsible for:
  - Loading chunks from disk
  - Validating chunk structure
  - Providing access to chunk data
"""

import json
from pathlib import Path
from typing import List

from remediation_search.core.domain_models import ChunkMetadata, DocumentChunk


class ChunkingService:
    """Service for managing document chunks."""
    
    def __init__(self, chunks_dir: Path = None):
        """
        Initialize the chunking service.
        
        Args:
            chunks_dir: Directory containing chunk files. Defaults to outputs/processed_chunks.
        """
        if chunks_dir is None:
            chunks_dir = Path("outputs") / "processed_chunks"
        self.chunks_dir = chunks_dir
    
    def chunks_exist(self) -> bool:
        """Check if chunks directory exists."""
        return self.chunks_dir.exists()
    
    def load_chunks(self) -> List[DocumentChunk]:
        """
        Load all chunks from disk.
        
        Returns:
            List of DocumentChunk objects
            
        Raises:
            FileNotFoundError: If chunks directory doesn't exist
            ValueError: If chunk files are malformed
        """
        if not self.chunks_exist():
            raise FileNotFoundError(
                f"Chunks directory not found: {self.chunks_dir}"
            )
        
        chunks = []
        
        for chunk_file in sorted(self.chunks_dir.glob("chunk_*.json")):
            try:
                chunk = self._load_chunk_file(chunk_file)
                if chunk:
                    chunks.append(chunk)
            except (json.JSONDecodeError, KeyError) as error:
                raise ValueError(
                    f"Malformed chunk file {chunk_file.name}: {error}"
                )
        
        return chunks
    
    def _load_chunk_file(self, chunk_file: Path) -> DocumentChunk:
        """
        Load a single chunk file.
        
        Args:
            chunk_file: Path to chunk JSON file
            
        Returns:
            DocumentChunk object or None if file is empty
        """
        with open(chunk_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        metadata_dict = data.get("metadata", {})
        metadata = ChunkMetadata(
            source=metadata_dict.get("source", "Unknown"),
            file_type=metadata_dict.get("file_type", "unknown")
        )
        
        return DocumentChunk(
            chunk_id=data.get("chunk_id"),
            content=data.get("content", ""),
            metadata=metadata
        )
    
    def get_chunk_count(self) -> int:
        """Get total number of chunks available."""
        if not self.chunks_exist():
            return 0
        return len(list(self.chunks_dir.glob("chunk_*.json")))

