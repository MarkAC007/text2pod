"""Tests for the document processor module."""
import pytest
from pathlib import Path

from text2pod.src.document_processor import DocumentProcessor
from text2pod.src.utils.error_handler import DocumentProcessingError

def test_document_processor_init_invalid_file():
    """Test initialization with non-existent file."""
    with pytest.raises(DocumentProcessingError, match="File not found"):
        DocumentProcessor("nonexistent.pdf")

def test_document_processor_init_invalid_type():
    """Test initialization with unsupported file type."""
    with pytest.raises(DocumentProcessingError, match="Unsupported file type"):
        DocumentProcessor("test.doc")

def test_clean_text():
    """Test text cleaning functionality."""
    processor = DocumentProcessor(str(Path(__file__).parent / "test_files/sample.pdf"))
    test_text = "This  is\x00 a   test"
    cleaned = processor._clean_text(test_text)
    assert cleaned == "This is a test" 