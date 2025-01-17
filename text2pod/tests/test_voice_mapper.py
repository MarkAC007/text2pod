"""Tests for the Voice Mapper module."""

import pytest
from unittest.mock import Mock, patch
from text2pod.src.utils.voice_mapper import (
    VoiceMapper,
    VoiceMappingError,
    VoiceConfig
)
from text2pod.src.utils.json_processor import (
    PodcastData,
    PodcastFormat,
    PodcastSegment
)

@pytest.fixture
def mock_voices_response():
    """Mock response from ElevenLabs voices endpoint."""
    return {
        "voices": [
            {
                "voice_id": "jessica_id",
                "name": "Jessica",
                "category": "professional"
            },
            {
                "voice_id": "daniel_id",
                "name": "Daniel",
                "category": "professional"
            },
            {
                "voice_id": "adam_id",
                "name": "Adam",
                "category": "professional"
            }
        ]
    }

@pytest.fixture
def sample_podcast_data():
    """Create sample podcast data for testing."""
    return PodcastData(
        podcast_format=PodcastFormat(
            style="interview",
            technical_level="intermediate",
            estimated_duration="25min"
        ),
        segments=[
            PodcastSegment(
                id="intro_001",
                speaker="host",
                content="Welcome to the show",
                tone="welcoming",
                technical_terms=[]
            ),
            PodcastSegment(
                id="expert_001",
                speaker="expert",
                content="Technical explanation",
                tone="authoritative",
                technical_terms=["term1"]
            )
        ],
        technical_glossary={"term1": "Definition 1"}
    )

@pytest.fixture
def voice_mapper():
    """Create VoiceMapper instance with mock API key."""
    with patch.dict('os.environ', {'ELEVENLABS_API_KEY': 'mock_key'}):
        return VoiceMapper()

def test_init_without_api_key():
    """Test initialization without API key."""
    with patch.dict('os.environ', clear=True):
        with pytest.raises(VoiceMappingError, match="ELEVENLABS_API_KEY not found"):
            VoiceMapper()

def test_get_available_voices(voice_mapper, mock_voices_response):
    """Test fetching available voices."""
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_voices_response
        mock_get.return_value.raise_for_status = Mock()
        
        voices = voice_mapper.get_available_voices()
        assert len(voices) == 3
        assert voices[0]["name"] == "Jessica"
        assert voices[1]["name"] == "Daniel"

def test_get_voice_id_with_cache(voice_mapper):
    """Test voice ID retrieval with cache."""
    voice_mapper.voice_id_cache["Jessica"] = "cached_id"
    assert voice_mapper.get_voice_id("Jessica") == "cached_id"

def test_get_voice_id_from_api(voice_mapper, mock_voices_response):
    """Test voice ID retrieval from API."""
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_voices_response
        mock_get.return_value.raise_for_status = Mock()
        
        voice_id = voice_mapper.get_voice_id("Jessica")
        assert voice_id == "jessica_id"
        assert voice_mapper.voice_id_cache["Jessica"] == "jessica_id"

def test_get_voice_id_not_found(voice_mapper, mock_voices_response):
    """Test voice ID retrieval for non-existent voice."""
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_voices_response
        mock_get.return_value.raise_for_status = Mock()
        
        with pytest.raises(VoiceMappingError, match="Voice not found"):
            voice_mapper.get_voice_id("NonExistentVoice")

def test_get_voice_config(voice_mapper, mock_voices_response):
    """Test voice configuration retrieval."""
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_voices_response
        mock_get.return_value.raise_for_status = Mock()
        
        # Test host voice with welcoming tone
        config = voice_mapper.get_voice_config("host", "welcoming")
        assert isinstance(config, VoiceConfig)
        assert config.name == "Jessica"
        assert config.voice_id == "jessica_id"
        assert config.settings["stability"] == 0.65  # Welcoming tone adjustment
        
        # Test expert voice with authoritative tone
        config = voice_mapper.get_voice_config("expert", "authoritative")
        assert config.name == "Daniel"
        assert config.voice_id == "daniel_id"
        assert config.settings["stability"] == 0.8  # Authoritative tone adjustment

def test_map_voices(voice_mapper, sample_podcast_data, mock_voices_response):
    """Test mapping voices to podcast segments."""
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_voices_response
        mock_get.return_value.raise_for_status = Mock()
        
        mappings = voice_mapper.map_voices(sample_podcast_data)
        assert len(mappings) == 2
        
        # Check host segment mapping
        segment, config = mappings[0]
        assert segment.speaker == "host"
        assert config.name == "Jessica"
        assert config.settings["stability"] == 0.65  # Welcoming tone
        
        # Check expert segment mapping
        segment, config = mappings[1]
        assert segment.speaker == "expert"
        assert config.name == "Daniel"
        assert config.settings["stability"] == 0.8  # Authoritative tone

def test_test_voice_connection(voice_mapper, mock_voices_response):
    """Test voice connection testing."""
    with patch('requests.get') as mock_get:
        # Test successful connection
        mock_get.return_value.json.return_value = mock_voices_response
        mock_get.return_value.raise_for_status = Mock()
        assert voice_mapper.test_voice_connection() is True
        
        # Test failed connection
        mock_get.side_effect = Exception("Connection failed")
        assert voice_mapper.test_voice_connection() is False 