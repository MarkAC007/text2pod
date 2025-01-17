# Text2Pod

Text2Pod is a Python-based CLI application that transforms consulting knowledge documents into engaging podcast-style audio content through an automated workflow. It processes PDF documents, analyzes their content, and generates natural-sounding podcast conversations using AI voices.

## 🎯 Features

- Convert PDF documents into natural dialogue scripts with multiple speakers
- Generate professional audio using ElevenLabs voices
- Maintain technical accuracy while making content engaging and accessible
- Support for multiple podcast formats (host-expert, panel discussions)
- Customizable technical depth and content style
- Built-in technical term handling and pronunciation guide
- Robust error handling and progress tracking

## 🛠️ Technical Stack

- Python 3.x
- OpenAI GPT-4 API for content analysis and script generation
- ElevenLabs API for voice synthesis
- Document Processing: PyPDF2
- Environment Management: python-dotenv
- Progress Tracking: tqdm

## 🚀 Getting Started

### Prerequisites

- Python 3.x
- OpenAI API key (for content analysis and script generation)
- ElevenLabs API key (for voice synthesis)
- Sufficient API credits on both platforms

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/text2pod.git
cd text2pod
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
   - Create a `.env` file in the project root
   - Add your API keys:
```plaintext
OPENAI_API_KEY=your_openai_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here
```

### Directory Setup

1. Create required directories:
```bash
mkdir -p input output
```

2. Place your PDF documents in the `input` directory
3. Generated content will appear in the `output` directory

### Usage

Text2Pod supports two main modes of operation, both of which can be run with or without interactive mode:

1. **Document Processing Mode** (Default):
```bash
# Non-interactive mode (processes all PDFs automatically)
python src/cli.py

# Interactive mode (asks for confirmation at each step)
python src/cli.py --interactive
# or
python src/cli.py -i
```
- Processes all PDF files in the input directory
- Generates analysis and markdown content
- Creates JSON files ready for podcast generation
- Interactive mode allows you to:
  - Confirm which PDF files to process
  - Review and adjust analysis settings
  - Verify processing steps

2. **Podcast Generation Mode**:
```bash
# Non-interactive mode
python src/cli.py --podcast path/to/analysis.json

# Interactive mode
python src/cli.py --podcast path/to/analysis.json --interactive
```
- Takes a processed JSON file
- Generates podcast-style audio content
- Creates final audio file and metadata
- Interactive mode allows you to:
  - Customize the project name
  - Review voice assignments
  - Confirm generation steps

Additional Options:
- `--format`: Override suggested podcast format
- `--cleanup`: Clean up intermediate audio files after generation
- `--debug`: Enable detailed debug logging

## 📁 Project Structure

```plaintext
text2pod/
├── src/
│   ├── document_processor.py   # PDF processing and content extraction
│   ├── script_generator.py     # Converts analysis to dialogue scripts
│   ├── podcast_generator.py    # Handles podcast audio generation
│   ├── utils/
│   │   ├── json_processor.py   # JSON data handling and validation
│   │   ├── voice_mapper.py     # Voice assignment and configuration
│   │   ├── audio_generator.py  # Audio synthesis and processing
│   │   ├── content_analyzer.py # Content analysis and structuring
│   │   ├── token_manager.py    # API token usage tracking
│   │   ├── error_handler.py    # Error handling and reporting
│   │   ├── progress.py        # Progress tracking and display
│   │   ├── interactive.py     # Interactive user prompts
│   │   ├── config.py         # Configuration management
│   │   └── openai_client.py  # OpenAI API integration
│   └── cli.py                # Command-line interface
├── tests/                    # Test files and fixtures
├── input/                    # Input PDF documents
├── output/                   # Generated content
└── requirements.txt          # Project dependencies
```

## 🔄 Processing Pipeline

1. **Document Processing**:
   - PDF text extraction and cleaning
   - Document structure analysis
   - Content segmentation

2. **Content Analysis**:
   - Topic identification
   - Technical term extraction
   - Complexity assessment
   - Format recommendation

3. **Script Generation**:
   - Natural dialogue creation
   - Speaker role assignment
   - Technical accuracy preservation
   - Transition smoothing

4. **Voice Processing**:
   - Voice profile selection
   - Pronunciation guide generation
   - Speech parameter optimization

5. **Audio Generation**:
   - Text-to-speech synthesis
   - Audio segment processing
   - Final file compilation

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Follow code style guidelines
4. Write clear commit messages
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- ElevenLabs for voice synthesis
- All contributors and users of the project