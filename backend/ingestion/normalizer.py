"""
Normalizer - converts all input formats to a shared internal schema.
"""
from typing import Dict, Any
from datetime import datetime
from models.mission import SourceType


def normalize_content(
    parsed_data: Dict[str, Any],
    source_type: SourceType,
    filename: str = None,
    source_label: str = None
) -> Dict[str, Any]:
    """
    Convert parsed content into a normalized internal schema.
    
    This creates a consistent structure regardless of input type (PDF, CSV, text).
    
    Args:
        parsed_data: Output from one of the parsers
        source_type: Type of source (pdf, csv, text)
        filename: Original filename if applicable
        source_label: Label for text inputs
        
    Returns:
        Normalized content dictionary
    """
    normalized = {
        "source_type": source_type.value,
        "source_identifier": filename or source_label or "unknown",
        "content": parsed_data.get("text", ""),
        "content_length": len(parsed_data.get("text", "")),
        "word_count": len(parsed_data.get("text", "").split()),
        "metadata": parsed_data.get("metadata", {}),
        "errors": parsed_data.get("errors", []),
        "normalized_at": datetime.utcnow().isoformat(),
        "is_valid": True
    }
    
    # Mark as invalid if there are critical errors or no content
    if not normalized["content"].strip():
        normalized["is_valid"] = False
        if "No content extracted" not in str(normalized["errors"]):
            normalized["errors"].append("No content extracted")
    
    # Add source-specific metadata
    if source_type == SourceType.PDF:
        normalized["metadata"]["page_count"] = parsed_data.get("page_count", 0)
    elif source_type == SourceType.CSV:
        normalized["metadata"]["row_count"] = parsed_data.get("row_count", 0)
        normalized["metadata"]["headers"] = parsed_data.get("headers", [])
    
    return normalized
