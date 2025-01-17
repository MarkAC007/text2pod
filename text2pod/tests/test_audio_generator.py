"""Tests for the Audio Generator module."""

import os
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from text2pod.src.utils.audio_generator import (
    AudioGenerator,
    AudioGenerationError
)
from text2pod.src.utils.json_processor import PodcastSegment
from text2pod.src.utils.voice_mapper import VoiceConfig

@pytest.fixture
def mock_ffmpeg():
    """Mock ffmpeg availability."""
    with patch('shutil.which', return_value='/usr/bin/ffmpeg'):
        yield

@pytest.fixture
def audio_generator(mock_ffmpeg, tmp_path):
    """Create AudioGenerator instance with mock API key."""
    with patch.dict('os.environ', {'ELEVENLABS_API_KEY': 'mock_key'}):
        return AudioGenerator(output_dir=tmp_path)

@pytest.fixture
def sample_segment():
    """Create a sample podcast segment."""
    return PodcastSegment(
        id="test_001",
        speaker="host",
        content="Test content",
        tone="neutral",
        technical_terms=[]
    )

@pytest.fixture
def sample_voice_config():
    """Create a sample voice configuration."""
    return VoiceConfig(
        voice_id="voice_123",
        name="TestVoice",
        settings={
            "stability": 0.71,
            "similarity_boost": 0.5,
            "style": 0.0,
            "use_speaker_boost": True
        }
    )

@pytest.fixture
def mock_audio_content():
    """Mock MP3 audio content."""
    return b"mock_audio_data"

def test_init_without_ffmpeg():
    """Test initialization without ffmpeg."""
    with patch('shutil.which', return_value=None):
        with pytest.raises(AudioGenerationError, match="ffmpeg not found"):
            AudioGenerator()

def test_init_without_api_key(mock_ffmpeg):
    """Test initialization without API key."""
    with patch.dict('os.environ', clear=True):
        with pytest.raises(AudioGenerationError, match="ELEVENLABS_API_KEY not found"):
            AudioGenerator()

def test_generate_segment_audio(
    audio_generator,
    sample_segment,
    sample_voice_config,
    mock_audio_content
):
    """Test generating audio for a single segment."""
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.content = mock_audio_content
        
        output_path = audio_generator.generate_segment_audio(
            segment=sample_segment,
            voice_config=sample_voice_config
        )
        
        assert output_path.exists()
        with open(output_path, 'rb') as f:
            assert f.read() == mock_audio_content
        
        # Verify API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0].endswith(f"/text-to-speech/{sample_voice_config.voice_id}")
        assert call_args[1]["json"]["text"] == sample_segment.content
        assert call_args[1]["json"]["voice_settings"] == sample_voice_config.settings

def test_generate_segment_audio_failure(
    audio_generator,
    sample_segment,
    sample_voice_config
):
    """Test handling API failure in segment generation."""
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 400
        mock_post.return_value.text = "API Error"
        
        with pytest.raises(AudioGenerationError, match="TTS request failed"):
            audio_generator.generate_segment_audio(
                segment=sample_segment,
                voice_config=sample_voice_config
            )

@patch('pydub.AudioSegment.from_mp3')
@patch('pydub.AudioSegment.export')
def test_merge_audio_segments(
    mock_export,
    mock_from_mp3,
    audio_generator,
    tmp_path
):
    """Test merging audio segments."""
    # Create mock segment files
    segment_files = [
        tmp_path / "segment1.mp3",
        tmp_path / "segment2.mp3"
    ]
    for file in segment_files:
        file.write_bytes(b"mock_audio")
    
    # Mock AudioSegment behavior
    mock_segment = Mock()
    mock_segment.append.return_value = mock_segment
    mock_from_mp3.return_value = mock_segment
    
    output_file = tmp_path / "merged.mp3"
    result = audio_generator.merge_audio_segments(
        segment_files=segment_files,
        output_file=output_file
    )
    
    assert result == output_file
    mock_export.assert_called_once()
    mock_segment.append.assert_called_once()

def test_merge_audio_segments_missing_file(audio_generator, tmp_path):
    """Test merging with missing segment file."""
    segment_files = [
        tmp_path / "nonexistent1.mp3",
        tmp_path / "nonexistent2.mp3"
    ]
    
    with pytest.raises(AudioGenerationError, match="Audio segment not found"):
        audio_generator.merge_audio_segments(
            segment_files=segment_files,
            output_file=tmp_path / "merged.mp3"
        )

@patch('pydub.AudioSegment.from_mp3')
@patch('pydub.AudioSegment.export')
def test_generate_podcast_audio(
    mock_export,
    mock_from_mp3,
    audio_generator,
    sample_segment,
    sample_voice_config,
    mock_audio_content
):
    """Test generating complete podcast audio."""
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.content = mock_audio_content
        
        # Mock AudioSegment behavior
        mock_segment = Mock()
        mock_segment.append.return_value = mock_segment
        mock_from_mp3.return_value = mock_segment
        
        segments = [(sample_segment, sample_voice_config)]
        merged_file, segment_files = audio_generator.generate_podcast_audio(
            segments=segments,
            project_name="test_project"
        )
        
        assert merged_file.name == "complete_podcast.mp3"
        assert len(segment_files) == 1
        assert all(file.exists() for file in segment_files)

def test_cleanup_segments(audio_generator, tmp_path):
    """Test cleaning up segment files."""
    # Create test files
    files = [
        tmp_path / "segment1.mp3",
        tmp_path / "segment2.mp3"
    ]
    for file in files:
        file.write_bytes(b"test_content")
    
    audio_generator.cleanup_segments(files)
    assert not any(file.exists() for file in files) 