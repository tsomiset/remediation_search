"""
Matching strategies for finding relevant remediation chunks.

Implements different scoring algorithms to rank chunk relevance
to a given root cause query.
"""

import re
from abc import ABC, abstractmethod
from difflib import SequenceMatcher
from typing import Set

from remediation_search.core.domain_models import DocumentChunk


class MatchingStrategy(ABC):
    """Abstract base class for matching strategies."""
    
    @abstractmethod
    def score(self, query: str, chunk: DocumentChunk) -> int:
        """
        Score a chunk against a query.
        
        Args:
            query: The search query text
            chunk: The chunk to score
            
        Returns:
            Integer score (higher = better match)
        """
        pass


class TokenOverlapStrategy(MatchingStrategy):
    """Score based on overlapping tokens between query and chunk."""
    
    TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9_]+")
    MIN_TOKEN_LENGTH = 3
    OVERLAP_WEIGHT = 2
    
    def tokenize(self, text: str) -> Set[str]:
        """Extract tokens from text."""
        return {
            token.lower()
            for token in self.TOKEN_PATTERN.findall(text)
            if len(token) > self.MIN_TOKEN_LENGTH
        }
    
    def score(self, query: str, chunk: DocumentChunk) -> int:
        """Score based on token overlap."""
        query_tokens = self.tokenize(query)
        if not query_tokens:
            return 0
        
        searchable_text = self._build_searchable_text(chunk)
        chunk_tokens = self.tokenize(searchable_text)
        
        overlap = len(query_tokens & chunk_tokens)
        return overlap * self.OVERLAP_WEIGHT
    
    def _build_searchable_text(self, chunk: DocumentChunk) -> str:
        """Build searchable text from chunk content and metadata."""
        return " ".join([
            chunk.content,
            chunk.metadata.source,
            chunk.metadata.file_type
        ]).lower()


class ExactPhraseStrategy(MatchingStrategy):
    """Score based on exact phrase match."""
    
    EXACT_PHRASE_BONUS = 10
    
    def score(self, query: str, chunk: DocumentChunk) -> int:
        """Score based on exact phrase presence."""
        searchable_text = " ".join([
            chunk.content,
            chunk.metadata.source
        ]).lower()
        
        return self.EXACT_PHRASE_BONUS if query.lower() in searchable_text else 0


class KeywordSequenceStrategy(MatchingStrategy):
    """Score based on query keywords appearing in sequence."""
    
    SEQUENCE_BONUS = 8
    
    def score(self, query: str, chunk: DocumentChunk) -> int:
        """Score based on keyword sequence match."""
        searchable_text = " ".join([
            chunk.content,
            chunk.metadata.source
        ]).lower()
        
        if self._contains_keyword_sequence(query, searchable_text):
            return self.SEQUENCE_BONUS
        return 0
    
    @staticmethod
    def _contains_keyword_sequence(query: str, target: str) -> bool:
        """Check if query keywords appear in order in target."""
        query_lower = query.lower()
        target_lower = target.lower()
        
        if query_lower in target_lower:
            return True
        
        query_tokens = query_lower.split()
        target_tokens = target_lower.split()
        
        query_idx = 0
        for target_token in target_tokens:
            if query_idx < len(query_tokens) and query_tokens[query_idx] in target_token:
                query_idx += 1
        
        return query_idx == len(query_tokens)


class FuzzyMatchStrategy(MatchingStrategy):
    """Score based on fuzzy string matching."""
    
    MIN_RATIO = 0.7
    FUZZY_WEIGHT = 5
    
    def score(self, query: str, chunk: DocumentChunk) -> int:
        """Score based on fuzzy match ratio."""
        searchable_text = " ".join([
            chunk.content,
            chunk.metadata.source
        ]).lower()
        
        ratio = SequenceMatcher(None, query.lower(), searchable_text).ratio()
        
        if ratio > self.MIN_RATIO:
            return int(ratio * self.FUZZY_WEIGHT)
        return 0


class CompositeMatchingStrategy(MatchingStrategy):
    """Combines multiple strategies with weighted scoring."""
    
    def __init__(self):
        """Initialize with all available strategies."""
        self.strategies = [
            TokenOverlapStrategy(),
            ExactPhraseStrategy(),
            KeywordSequenceStrategy(),
            FuzzyMatchStrategy()
        ]
    
    def score(self, query: str, chunk: DocumentChunk) -> int:
        """
        Score chunk using all strategies.
        
        Args:
            query: The search query
            chunk: The chunk to score
            
        Returns:
            Combined score from all strategies
        """
        total_score = 0
        for strategy in self.strategies:
            total_score += strategy.score(query, chunk)
        return total_score

