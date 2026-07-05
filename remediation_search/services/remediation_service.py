"""
Remediation service for finding remediation steps.

Responsible for:
  - Scoring chunks against a query
  - Finding matching remediation steps
  - Formatting remediation results
"""

from typing import List

from remediation_search.services.chunking_service import ChunkingService
from remediation_search.core.domain_models import (
    DocumentChunk,
    RemediationMatch,
    RemediationResult,
)
from remediation_search.strategies.matching_strategy import CompositeMatchingStrategy


class RemediationService:
    """Service for finding remediation steps."""
    
    def __init__(
        self,
        chunking_service: ChunkingService = None,
        matching_strategy: CompositeMatchingStrategy = None,
        result_limit: int = 3
    ):
        """
        Initialize the remediation service.
        
        Args:
            chunking_service: Service for loading chunks
            matching_strategy: Strategy for scoring matches
            result_limit: Maximum number of results to return
        """
        self.chunking_service = chunking_service or ChunkingService()
        self.matching_strategy = matching_strategy or CompositeMatchingStrategy()
        self.result_limit = result_limit
    
    def find_remediation(self, root_cause: str) -> RemediationResult:
        """
        Find remediation steps for a given root cause.
        
        Args:
            root_cause: Description of the root cause/alert
            
        Returns:
            RemediationResult with matches
            
        Raises:
            FileNotFoundError: If chunks don't exist
            ValueError: If chunks are malformed
        """
        chunks = self.chunking_service.load_chunks()
        if not chunks:
            return RemediationResult(
                alert_name=root_cause,
                root_cause=root_cause,
                matches=()
            )
        
        # Score all chunks
        scored_matches = self._score_chunks(root_cause, chunks)
        
        # Extract alert name from best match
        alert_name = self._extract_alert_name(root_cause, scored_matches)
        
        return RemediationResult(
            alert_name=alert_name,
            root_cause=root_cause,
            matches=tuple(scored_matches[:self.result_limit])
        )
    
    def _score_chunks(self, query: str, chunks: List[DocumentChunk]) -> List[RemediationMatch]:
        """
        Score all chunks and return sorted matches.
        
        Args:
            query: Search query
            chunks: List of chunks to score
            
        Returns:
            List of RemediationMatch objects, sorted by score (descending)
        """
        matches = []
        
        for chunk in chunks:
            score = self.matching_strategy.score(query, chunk)
            if score > 0:
                matches.append(RemediationMatch(score=score, chunk=chunk))
        
        # Sort by score (descending), then by chunk_id for determinism
        matches.sort(key=lambda m: (-m.score, m.chunk.chunk_id))
        return matches
    
    def _extract_alert_name(
        self,
        root_cause: str,
        matches: List[RemediationMatch]
    ) -> str:
        """
        Extract alert name from best match or use root cause as fallback.
        
        Args:
            root_cause: The original root cause query
            matches: List of remediation matches
            
        Returns:
            Alert name string
        """
        if matches:
            return matches[0].chunk.metadata.source
        return root_cause

