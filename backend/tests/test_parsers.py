"""
Tests for document parsers (CSV, TXT, PDF).
"""
import pytest
from ingestion.csv_parser import parse_csv
from ingestion.text_parser import parse_text
from ingestion.normalizer import normalize_content
from models.mission import SourceType


class TestCSVParser:
    """Test suite for CSV parsing functionality."""
    
    def test_parse_valid_csv(self, sample_csv_content: bytes):
        """Test parsing a valid CSV file."""
        result = parse_csv(sample_csv_content, "test.csv")
        
        assert "text" in result
        assert "metadata" in result
        assert result["metadata"]["row_count"] == 3
        assert result["metadata"]["column_count"] == 4
        assert "threat_id" in result["text"]
        assert "APT Alpha" in result["text"]
    
    def test_parse_empty_csv(self):
        """Test parsing an empty CSV file."""
        result = parse_csv(b"", "empty.csv")
        
        # Empty CSV still generates summary text
        assert "CSV Data Summary" in result["text"]
        assert result["metadata"]["row_count"] == 0
    
    def test_parse_csv_with_special_chars(self):
        """Test CSV with special characters."""
        content = b'name,description\n"Test, Inc.","A ""quoted"" value"'
        result = parse_csv(content, "special.csv")
        
        assert "Test, Inc." in result["text"]
    
    def test_csv_metadata_extraction(self, sample_csv_content: bytes):
        """Test that CSV metadata is correctly extracted."""
        result = parse_csv(sample_csv_content, "threats.csv")
        
        # Check actual metadata keys from parser
        assert "columns" in result["metadata"]
        assert "threat_id" in result["metadata"]["columns"]
        assert result["metadata"]["column_count"] == 4
    
    def test_csv_headers_extracted(self, sample_csv_content: bytes):
        """Test that headers are properly extracted."""
        result = parse_csv(sample_csv_content, "test.csv")
        
        assert "headers" in result
        assert result["headers"] == ["threat_id", "threat_name", "category", "severity"]


class TestTextParser:
    """Test suite for TXT parsing functionality."""
    
    def test_parse_valid_text(self):
        """Test parsing valid text content."""
        content = "This is a test document.\nWith multiple lines."
        result = parse_text(content, "notes.txt")
        
        assert result["text"] == content
        # Actual key is character_count, not char_count
        assert result["metadata"]["character_count"] == len(content)
    
    def test_parse_empty_text(self):
        """Test parsing empty text."""
        result = parse_text("", "empty.txt")
        
        assert result["text"] == ""
        assert result["metadata"]["character_count"] == 0
    
    def test_text_line_count(self):
        """Test line count in metadata."""
        content = "Line 1\nLine 2\nLine 3"
        result = parse_text(content, "lines.txt")
        
        assert result["metadata"]["line_count"] == 3
    
    def test_text_word_count(self):
        """Test word count in metadata."""
        content = "One two three four five"
        result = parse_text(content, "words.txt")
        
        assert result["metadata"]["word_count"] == 5
    
    def test_text_whitespace_normalization(self):
        """Test that excessive whitespace is normalized."""
        content = "Line 1\n\n\n\nLine 2"  # 4 newlines
        result = parse_text(content, "whitespace.txt")
        
        # Should be reduced to max 2 newlines
        assert "\n\n\n" not in result["text"]


class TestNormalizer:
    """Test suite for content normalization."""
    
    def test_normalize_csv_content(self, sample_csv_content: bytes):
        """Test normalizing CSV parsed content."""
        parsed = parse_csv(sample_csv_content, "test.csv")
        result = normalize_content(parsed, SourceType.CSV, filename="test.csv")
        
        assert "content" in result
        assert "is_valid" in result
        assert "metadata" in result
        assert result["is_valid"] is True
    
    def test_normalize_text_content(self):
        """Test normalizing text content."""
        parsed = parse_text("Test content here.", "test.txt")
        result = normalize_content(parsed, SourceType.TEXT, filename="test.txt")
        
        assert result["is_valid"] is True
        assert len(result["content"]) > 0
    
    def test_normalize_empty_content(self):
        """Test normalizing empty content returns errors."""
        parsed = {"text": "", "metadata": {}}
        result = normalize_content(parsed, SourceType.TEXT, filename="empty.txt")
        
        # Empty content should still be valid but noted
        assert "errors" in result
    
    def test_normalize_preserves_content(self, sample_csv_content: bytes):
        """Test that content is preserved through normalization."""
        parsed = parse_csv(sample_csv_content, "data.csv")
        result = normalize_content(parsed, SourceType.CSV, filename="data.csv")
        
        # Content should contain the original CSV text
        assert "APT Alpha" in result["content"]
