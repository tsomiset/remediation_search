"""Pluggable matching strategies."""

from remediation_search.strategies.matching_strategy import (
    CompositeMatchingStrategy,
    ExactPhraseStrategy,
    FuzzyMatchStrategy,
    KeywordSequenceStrategy,
    MatchingStrategy,
    TokenOverlapStrategy,
)

__all__ = [
    "MatchingStrategy",
    "TokenOverlapStrategy",
    "ExactPhraseStrategy",
    "KeywordSequenceStrategy",
    "FuzzyMatchStrategy",
    "CompositeMatchingStrategy",
]

