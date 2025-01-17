"""Integration tests for the Text2Pod pipeline."""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from text2pod.src.utils.json_processor import JSONProcessor
from text2pod.src.utils.voice_mapper import VoiceMapper
from text2pod.src.utils.audio_generator import AudioGenerator

@pytest.fixture
def mock_ffmpeg():
    """Mock ffmpeg availability."""
    with patch('shutil.which', return_value='/usr/bin/ffmpeg'):
        yield

@pytest.fixture
def mock_env():
    """Set up mock environment variables."""
    with patch.dict('os.environ', {
        'ELEVENLABS_API_KEY': 'mock_key',
        'OPENAI_API_KEY': 'mock_key'
    }):
        yield

@pytest.fixture
def sample_json_file(tmp_path):
    """Create a sample podcast JSON file."""
    json_data = {
        "podcast_format": {
            "style": "interview",
            "technical_level": "intermediate",
            "estimated_duration": "25min"
        },
        "segments": [
            {
                "id": "intro_001",
                "speaker": "host",
                "content": "Welcome to our technical podcast about AI development.",
                "tone": "welcoming",
                "technical_terms": []
            },
            {
                "id": "expert_001",
                "speaker": "expert",
                "content": "Let me explain how neural networks process information.",
                "tone": "authoritative",
                "technical_terms": ["neural networks", "deep learning"]
            },
            {
                "id": "host_002",
                "speaker": "host",
                "content": "That's fascinating! Could you elaborate on the training process?",
                "tone": "curious",
                "technical_terms": ["training"]
            }
        ],
        "technical_glossary": {
            "neural networks": "A computing system inspired by biological neural networks",
            "deep learning": "A subset of machine learning based on artificial neural networks",
            "training": "The process of teaching a model using data"
        }
    }
    
    json_file = tmp_path / "test_podcast.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2)
    return json_file

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
            }
        ]
    }

@pytest.fixture
def mock_audio_content():
    """Mock MP3 audio content."""
    return b"mock_audio_data"

def test_complete_pipeline(
    mock_env,
    mock_ffmpeg,
    sample_json_file,
    mock_voices_response,
    mock_audio_content,
    tmp_path
):
    """Test the complete podcast generation pipeline."""
    # Set up output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Initialize components
    json_processor = JSONProcessor()
    voice_mapper = VoiceMapper()
    audio_generator = AudioGenerator(output_dir=output_dir)
    
    # Mock ElevenLabs API calls
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post, \
         patch('pydub.AudioSegment.from_mp3') as mock_from_mp3, \
         patch('pydub.AudioSegment.export') as mock_export:
        
        # Mock voice listing
        mock_get.return_value.json.return_value = mock_voices_response
        mock_get.return_value.raise_for_status = Mock()
        
        # Mock audio generation
        mock_post.return_value.status_code = 200
        mock_post.return_value.content = mock_audio_content
        
        # Mock audio merging
        mock_segment = Mock()
        mock_segment.append.return_value = mock_segment
        mock_from_mp3.return_value = mock_segment
        
        # Process JSON
        podcast_data = json_processor.process_json(sample_json_file)
        assert len(podcast_data.segments) == 3
        assert podcast_data.podcast_format.style == "interview"
        
        # Map voices
        voice_mappings = voice_mapper.map_voices(podcast_data)
        assert len(voice_mappings) == 3
        
        # Generate audio
        merged_file, segment_files = audio_generator.generate_podcast_audio(
            segments=voice_mappings,
            project_name="test_podcast"
        )
        
        # Verify outputs
        assert merged_file.exists()
        assert len(segment_files) == 3
        assert all(file.exists() for file in segment_files)
        
        # Verify API calls
        assert mock_get.call_count >= 1  # Voice listing
        assert mock_post.call_count == 3  # One per segment
        assert mock_from_mp3.call_count >= 1  # Audio merging
        assert mock_export.call_count >= 1  # Final export

def test_pipeline_with_pronunciation(
    mock_env,
    mock_ffmpeg,
    sample_json_file,
    mock_voices_response,
    mock_audio_content,
    tmp_path
):
    """Test pipeline with technical term pronunciation handling."""
    # Set up output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Initialize components
    json_processor = JSONProcessor()
    voice_mapper = VoiceMapper()
    audio_generator = AudioGenerator(output_dir=output_dir)
    
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post, \
         patch('pydub.AudioSegment.from_mp3') as mock_from_mp3, \
         patch('pydub.AudioSegment.export') as mock_export:
        
        # Mock API responses
        mock_get.return_value.json.return_value = mock_voices_response
        mock_get.return_value.raise_for_status = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.content = mock_audio_content
        
        # Mock audio handling
        mock_segment = Mock()
        mock_segment.append.return_value = mock_segment
        mock_from_mp3.return_value = mock_segment
        
        # Process data
        podcast_data = json_processor.process_json(sample_json_file)
        voice_mappings = voice_mapper.map_voices(podcast_data)
        
        # Get pronunciation guide
        pronunciations = json_processor.get_pronunciation_guide(podcast_data)
        assert "neural networks" in pronunciations
        assert "deep learning" in pronunciations
        
        # Generate audio
        merged_file, segment_files = audio_generator.generate_podcast_audio(
            segments=voice_mappings,
            project_name="test_podcast_with_terms"
        )
        
        # Verify outputs
        assert merged_file.exists()
        assert len(segment_files) == 3
        
        # Verify API calls for segments with technical terms
        expert_segment_call = None
        for call in mock_post.call_args_list:
            if "neural networks" in call[1]["json"]["text"]:
                expert_segment_call = call
                break
        
        assert expert_segment_call is not None
        assert "neural networks" in expert_segment_call[1]["json"]["text"]
        assert "deep learning" in expert_segment_call[1]["json"]["text"]

def test_pipeline_error_handling(
    mock_env,
    mock_ffmpeg,
    sample_json_file,
    mock_voices_response,
    tmp_path
):
    """Test pipeline error handling."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    json_processor = JSONProcessor()
    voice_mapper = VoiceMapper()
    audio_generator = AudioGenerator(output_dir=output_dir)
    
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post:
        
        # Mock successful voice listing
        mock_get.return_value.json.return_value = mock_voices_response
        mock_get.return_value.raise_for_status = Mock()
        
        # Mock failed audio generation
        mock_post.return_value.status_code = 400
        mock_post.return_value.text = "API Error"
        
        # Process should work up to audio generation
        podcast_data = json_processor.process_json(sample_json_file)
        voice_mappings = voice_mapper.map_voices(podcast_data)
        
        # Audio generation should fail
        with pytest.raises(Exception):
            audio_generator.generate_podcast_audio(
                segments=voice_mappings,
                project_name="test_podcast_error"
            ) 