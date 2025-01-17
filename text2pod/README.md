# Text2Pod

Convert technical documents into engaging podcast-style audio content using AI.

## Overview

Text2Pod is a Python CLI application that transforms technical documentation and knowledge articles into natural-sounding podcast dialogues. It uses AI to analyze content, generate conversational scripts, and create professional audio output.

## Features

- **Intelligent Document Processing**
  - PDF document support
  - Smart content analysis and cleaning
  - Automatic removal of supplementary content
  - Structure-aware processing

- **AI-Powered Script Generation**
  - Format analysis and selection
  - Natural dialogue generation
  - Multiple conversation styles:
    - Host/Expert interviews
    - Two-expert discussions
    - Panel conversations

- **Professional Audio Output**
  - ElevenLabs voice synthesis
  - Multiple voice characters
  - Natural conversation flow

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/text2pod.git
cd text2pod
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your API keys:
```env
# API Keys
OPENAI_API_KEY=your_openai_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here

# Model Configuration
OPENAI_MODEL=gpt-4o-mini

# Processing Configuration
MAX_SEGMENT_LENGTH=5000
MAX_RETRIES=3
RETRY_DELAY=1
```

## Usage

1. Place your PDF documents in the `input` directory

2. Run the conversion:
```bash
python src/cli.py [--debug] [--format {host_expert,two_experts,panel}]
```

3. Find the generated scripts in the `output` directory

## Project Structure

```plaintext
text2pod/
├── src/
│   ├── cli.py              # Command-line interface
│   ├── document_processor.py
│   ├── script_generator.py
│   └── utils/
│       ├── config.py       # Configuration management
│       ├── content_analyzer.py
│       ├── error_handler.py
│       ├── openai_client.py
│       └── progress.py
├── tests/
│   ├── test_document_processor.py
│   └── test_files/
│       └── sample.pdf
├── input/                  # Document input directory
├── output/                # Generated output
├── .env                   # Environment configuration
└── requirements.txt       # Project dependencies
```

## Processing Flow

1. **Document Processing**
   - Extract text from PDF
   - Analyze document structure
   - Clean and prepare content

2. **Content Analysis**
   - Identify document structure
   - Remove supplementary content
   - Determine optimal format

3. **Script Generation**
   - Generate natural dialogue
   - Break content into segments
   - Apply conversation format

4. **Audio Generation** (Coming Soon)
   - Voice assignment
   - Audio synthesis
   - Final compilation

## Development

### Running Tests
```bash
pytest
```

### Debug Mode
```bash
python src/cli.py --debug
```

### Logging
- Logs are written to `text2pod.log`
- Console output shows progress and key information
- Debug mode enables detailed logging

## Error Handling

- Automatic retry for API calls
- Comprehensive error logging
- Graceful failure handling
- Progress preservation

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 