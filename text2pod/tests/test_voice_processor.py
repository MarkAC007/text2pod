"""Test voice processing functionality."""
import json
from pathlib import Path
import pytest

from src.voice_processor import VoiceProcessor
from src.utils.error_handler import VoiceProcessingError

# Test data
SAMPLE_ANALYSIS = {
    "podcast_format": {
        "recommended": "host_expert",
        "reasoning": "Technical content suits expert explanation"
    },
    "segments": [
        {
            "title": "Introduction to Testing",
            "key_points": [
                "Testing is essential for software quality",
                "Different types of tests serve different purposes"
            ],
            "discussion_questions": [
                "Why is testing important?",
                "How do you choose what to test?"
            ],
            "technical_terms": [
                {
                    "term": "Unit Testing",
                    "definition": "Testing individual components in isolation"
                }
            ]
        }
    ]
}

@pytest.fixture
def test_analysis_file(tmp_path):
    """Create a temporary analysis file for testing."""
    analysis_file = tmp_path / "test_analysis.json"
    with open(analysis_file, 'w') as f:
        json.dump(SAMPLE_ANALYSIS, f)
    return analysis_file

def test_voice_processor_initialization(test_analysis_file):
    """Test VoiceProcessor initialization."""
    processor = VoiceProcessor(test_analysis_file)
    assert processor.analysis == SAMPLE_ANALYSIS

def test_ssml_formatting(test_analysis_file):
    """Test SSML tag generation."""
    processor = VoiceProcessor(test_analysis_file, use_ssml=True)
    text = "This is a test"
    formatted = processor._add_ssml(text, "HOST")
    assert "<speak>" in formatted
    assert "</speak>" in formatted
    assert "<prosody" in formatted

def test_script_validation(test_analysis_file):
    """Test script validation."""
    processor = VoiceProcessor(test_analysis_file)
    valid_script = """
=== SEGMENT 1 ===
[HOST]
Welcome to the show
[EXPERT]
Let me explain this topic
"""
    assert processor.validate_script(valid_script) == True

def test_invalid_script(test_analysis_file):
    """Test invalid script detection."""
    processor = VoiceProcessor(test_analysis_file)
    invalid_script = "No proper structure or roles"
    with pytest.raises(VoiceProcessingError):
        processor.validate_script(invalid_script) 