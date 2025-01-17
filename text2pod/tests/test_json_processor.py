"""Tests for the JSON Processing module."""

import json
import pytest
from pathlib import Path
from text2pod.src.utils.json_processor import (
    JSONProcessor,
    JSONProcessingError,
    PodcastFormat,
    PodcastSegment,
    PodcastData
)

@pytest.fixture
def json_processor():
    return JSONProcessor()

@pytest.fixture
def sample_json_path(tmp_path):
    """Create a valid sample JSON file"""
    sample_data = {
        "podcast_format": {
            "style": "interview",
            "technical_level": "intermediate",
            "estimated_duration": "25min"
        },
        "segments": [
            {
                "id": "intro_001",
                "speaker": "host",
                "content": "Welcome to the show",
                "tone": "welcoming",
                "technical_terms": []
            },
            {
                "id": "expert_001",
                "speaker": "expert",
                "content": "Let me explain the concept",
                "tone": "authoritative",
                "technical_terms": ["term1"]
            }
        ],
        "technical_glossary": {
            "term1": "Definition of term1"
        }
    }
    
    json_file = tmp_path / "test_podcast.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(sample_data, f)
    return json_file

def test_load_json(json_processor, sample_json_path):
    """Test loading a valid JSON file"""
    data = json_processor.load_json(sample_json_path)
    assert isinstance(data, dict)
    assert "podcast_format" in data
    assert "segments" in data

def test_load_invalid_json(json_processor, tmp_path):
    """Test loading an invalid JSON file"""
    invalid_file = tmp_path / "invalid.json"
    with open(invalid_file, "w") as f:
        f.write("invalid json content")
    
    with pytest.raises(JSONProcessingError):
        json_processor.load_json(invalid_file)

def test_validate_format(json_processor):
    """Test podcast format validation"""
    valid_format = {
        "style": "interview",
        "technical_level": "intermediate",
        "estimated_duration": "25min"
    }
    result = json_processor.validate_format(valid_format)
    assert isinstance(result, PodcastFormat)
    assert result.style == "interview"
    assert result.technical_level == "intermediate"

def test_validate_format_invalid_style(json_processor):
    """Test format validation with invalid style"""
    invalid_format = {
        "style": "invalid_style",
        "technical_level": "intermediate",
        "estimated_duration": "25min"
    }
    with pytest.raises(JSONProcessingError, match="Unsupported podcast style"):
        json_processor.validate_format(invalid_format)

def test_validate_segment(json_processor):
    """Test segment validation"""
    valid_segment = {
        "id": "test_001",
        "speaker": "host",
        "content": "Test content",
        "tone": "neutral",
        "technical_terms": []
    }
    result = json_processor.validate_segment(valid_segment)
    assert isinstance(result, PodcastSegment)
    assert result.id == "test_001"
    assert result.speaker == "host"

def test_validate_segment_missing_content(json_processor):
    """Test segment validation with missing content"""
    invalid_segment = {
        "id": "test_001",
        "speaker": "host",
        "tone": "neutral"
    }
    with pytest.raises(JSONProcessingError, match="Segment must have content"):
        json_processor.validate_segment(invalid_segment)

def test_process_json(json_processor, sample_json_path):
    """Test complete JSON processing"""
    result = json_processor.process_json(sample_json_path)
    assert isinstance(result, PodcastData)
    assert len(result.segments) == 2
    assert result.podcast_format.style == "interview"
    assert "term1" in result.technical_glossary

def test_get_pronunciation_guide(json_processor, sample_json_path):
    """Test pronunciation guide generation"""
    data = json_processor.process_json(sample_json_path)
    guide = json_processor.get_pronunciation_guide(data)
    assert isinstance(guide, dict)
    assert "term1" in guide 