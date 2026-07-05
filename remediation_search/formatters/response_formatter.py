"""
Response formatting service for presentation layer.

Responsible for:
  - Formatting remediation results for display
  - Building human-readable output
"""

from abc import ABC, abstractmethod

from remediation_search.core.domain_models import RemediationResult


class ResponseFormatter(ABC):
    """Abstract base class for response formatting."""
    
    @abstractmethod
    def format(self, result: RemediationResult) -> str:
        """
        Format a remediation result for output.
        
        Args:
            result: The remediation result to format
            
        Returns:
            Formatted string ready for display
        """
        pass


class DetailedResponseFormatter(ResponseFormatter):
    """Formats results with detailed information."""
    
    def format(self, result: RemediationResult) -> str:
        """Format with alert name, root cause, and remediation steps."""
        lines = []
        
        # Header
        lines.append("=" * 70)
        lines.append(f"ALERT: {result.alert_name}")
        lines.append("=" * 70)
        lines.append("")
        
        # Root cause
        lines.append(f"Root Cause: {result.root_cause}")
        lines.append("")
        
        # Status and remediation steps
        if result.has_matches():
            lines.append("Status: ✓ Remediation steps found")
            lines.append("")
            lines.append("-" * 70)
            lines.append("REMEDIATION STEPS:")
            lines.append("-" * 70)
            lines.append("")
            
            for index, match in enumerate(result.matches, start=1):
                chunk = match.chunk
                lines.append(f"Step {index}: {chunk.metadata.source}")
                lines.append(f"          [Reference: chunk_{chunk.chunk_id}]")
                lines.append("")
                lines.append(chunk.content.strip())
                lines.append("")
            
            lines.append("-" * 70)
        else:
            lines.append("Status: ⚠️  No matching remediation steps found.")
            lines.append("")
            lines.append("Recommendation: Check if the alert keyword is correct or ingestion")
            lines.append("of related documentation may be needed.")
        
        return "\n".join(lines).strip()


class CompactResponseFormatter(ResponseFormatter):
    """Formats results in a compact format."""
    
    def format(self, result: RemediationResult) -> str:
        """Format in compact form."""
        lines = []
        
        lines.append(f"Alert: {result.alert_name}")
        lines.append(f"Root Cause: {result.root_cause}")
        lines.append("")
        
        if result.has_matches():
            lines.append(f"Found {result.match_count()} remediation steps:")
            for index, match in enumerate(result.matches, start=1):
                lines.append(f"  {index}. {match.chunk.metadata.source}")
        else:
            lines.append("No remediation steps found.")
        
        return "\n".join(lines).strip()


class FormatterFactory:
    """Factory for creating response formatters."""
    
    _formatters = {
        "detailed": DetailedResponseFormatter,
        "compact": CompactResponseFormatter
    }
    
    @classmethod
    def create(cls, format_type: str = "detailed") -> ResponseFormatter:
        """
        Create a response formatter.
        
        Args:
            format_type: Type of formatter ("detailed" or "compact")
            
        Returns:
            ResponseFormatter instance
            
        Raises:
            ValueError: If format type is unknown
        """
        if format_type not in cls._formatters:
            raise ValueError(
                f"Unknown format type: {format_type}. "
                f"Available: {list(cls._formatters.keys())}"
            )
        return cls._formatters[format_type]()
    
    @classmethod
    def register(cls, format_type: str, formatter_class):
        """Register a new formatter type."""
        cls._formatters[format_type] = formatter_class

