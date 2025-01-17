"""Tests for the main Podcast Generator module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, ANY

from text2pod.src.podcast_generator import (
    PodcastGenerator,
    PodcastGenerationError
)
from text2pod.src.utils.json_processor import PodcastData, PodcastFormat

@pytest.fixture
def mock_env():
    """Set up mock environment variables."""
    with patch.dict('os.environ', {
        'ELEVENLABS_API_KEY': 'mock_key',
        'OPENAI_API_KEY': 'mock_key'
    }):
        yield

@pytest.fixture
def mock_ffmpeg():
    """Mock ffmpeg availability."""
    with patch('shutil.which', return_value='/usr/bin/ffmpeg'):
        yield

@pytest.fixture
def mock_components():
    """Mock all component classes."""
    with patch('text2pod.src.podcast_generator.JSONProcessor') as mock_json, \
         patch('text2pod.src.podcast_generator.VoiceMapper') as mock_mapper, \
         patch('text2pod.src.podcast_generator.AudioGenerator') as mock_audio:
        
        # Set up mock returns
        mock_json.return_value.process_json.return_value = PodcastData(
            podcast_format=PodcastFormat(
                style="interview",
                technical_level="intermediate",
                estimated_duration="25min"
            ),
            segments=[],
            technical_glossary={}
        )
        mock_json.return_value.get_pronunciation_guide.return_value = {}
        
        mock_mapper.return_value.map_voices.return_value = []
        mock_mapper.return_value.test_voice_connection.return_value = True
        
        mock_audio.return_value.generate_podcast_audio.return_value = (
            Path("output/test.mp3"),
            [Path("output/segment1.mp3")]
        )
        
        yield mock_json, mock_mapper, mock_audio

def test_init_success(mock_env, mock_ffmpeg, tmp_path):
    """Test successful initialization."""
    generator = PodcastGenerator(output_dir=tmp_path)
    assert generator.output_dir == tmp_path
    assert not generator.cleanup_segments

def test_init_with_cleanup(mock_env, mock_ffmpeg, tmp_path):
    """Test initialization with cleanup enabled."""
    generator = PodcastGenerator(
        output_dir=tmp_path,
        cleanup_segments=True
    )
    assert generator.cleanup_segments

def test_init_creates_output_dir(mock_env, mock_ffmpeg, tmp_path):
    """Test output directory creation."""
    output_dir = tmp_path / "podcast_output"
    generator = PodcastGenerator(output_dir=output_dir)
    assert output_dir.exists()
    assert output_dir.is_dir()

@patch('pathlib.Path.mkdir')
def test_init_failure(mock_mkdir, mock_env, mock_ffmpeg):
    """Test initialization failure."""
    mock_mkdir.side_effect = PermissionError("Access denied")
    
    with pytest.raises(PodcastGenerationError, match="Failed to initialize components"):
        PodcastGenerator()

def test_generate_podcast(
    mock_env,
    mock_ffmpeg,
    mock_components,
    tmp_path
):
    """Test complete podcast generation."""
    mock_json, mock_mapper, mock_audio = mock_components
    
    # Create test JSON file
    json_path = tmp_path / "test.json"
    json_path.touch()
    
    # Initialize generator
    generator = PodcastGenerator(output_dir=tmp_path)
    
    # Generate podcast
    output_file, metadata = generator.generate_podcast(
        json_path=json_path,
        project_name="test_podcast"
    )
    
    # Verify component calls
    mock_json.return_value.process_json.assert_called_once_with(json_path)
    mock_json.return_value.get_pronunciation_guide.assert_called_once()
    mock_mapper.return_value.map_voices.assert_called_once()
    mock_audio.return_value.generate_podcast_audio.assert_called_once_with(
        segments=ANY,
        project_name="test_podcast",
        crossfade_ms=500
    )
    
    # Verify metadata
    assert metadata["title"] == "test_podcast"
    assert metadata["format"] == "interview"
    assert metadata["technical_level"] == "intermediate"

def test_generate_podcast_with_cleanup(
    mock_env,
    mock_ffmpeg,
    mock_components,
    tmp_path
):
    """Test podcast generation with segment cleanup."""
    mock_json, mock_mapper, mock_audio = mock_components
    
    # Create test JSON file
    json_path = tmp_path / "test.json"
    json_path.touch()
    
    # Initialize generator with cleanup
    generator = PodcastGenerator(
        output_dir=tmp_path,
        cleanup_segments=True
    )
    
    # Generate podcast
    generator.generate_podcast(
        json_path=json_path,
        project_name="test_podcast"
    )
    
    # Verify cleanup was called
    mock_audio.return_value.cleanup_segments.assert_called_once()

def test_generate_podcast_failure(
    mock_env,
    mock_ffmpeg,
    mock_components,
    tmp_path
):
    """Test podcast generation failure."""
    mock_json, mock_mapper, mock_audio = mock_components
    
    # Set up failure
    mock_audio.return_value.generate_podcast_audio.side_effect = Exception("Generation failed")
    
    # Create test JSON file
    json_path = tmp_path / "test.json"
    json_path.touch()
    
    # Initialize generator
    generator = PodcastGenerator(output_dir=tmp_path)
    
    # Attempt generation
    with pytest.raises(PodcastGenerationError, match="Failed to generate podcast"):
        generator.generate_podcast(
            json_path=json_path,
            project_name="test_podcast"
        )

def test_test_connections(
    mock_env,
    mock_ffmpeg,
    mock_components,
    tmp_path
):
    """Test connection testing functionality."""
    mock_json, mock_mapper, mock_audio = mock_components
    
    # Initialize generator
    generator = PodcastGenerator(output_dir=tmp_path)
    
    # Test connections
    results = generator.test_connections()
    
    assert "voice_service" in results
    assert "output_directory" in results
    assert results["voice_service"] is True
    assert results["output_directory"] is True

def test_test_connections_failure(
    mock_env,
    mock_ffmpeg,
    mock_components,
    tmp_path
):
    """Test connection testing with failures."""
    mock_json, mock_mapper, mock_audio = mock_components
    
    # Set up voice service failure
    mock_mapper.return_value.test_voice_connection.return_value = False
    
    # Make output directory read-only
    output_dir = tmp_path / "readonly"
    output_dir.mkdir()
    
    # Initialize generator
    generator = PodcastGenerator(output_dir=output_dir)
    
    # Test connections
    results = generator.test_connections()
    
    assert results["voice_service"] is False 