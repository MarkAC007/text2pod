# Text2Pod

Text2Pod is a Python-based CLI application that transforms consulting knowledge documents into engaging podcast-style audio content through an automated workflow.

## 🎯 Features

- Convert PDF and Word documents into natural dialogue scripts
- Generate professional audio using ElevenLabs voices
- Maintain content integrity while making it engaging
- Customize format and technical depth
- Robust error handling and progress tracking

## 🛠️ Technical Stack

- Python 3.x
- OpenAI GPT-4 API
- ElevenLabs API
- Document Processing: PyPDF2, python-docx
- Environment Management: python-dotenv
- Progress Tracking: tqdm

## 🚀 Getting Started

### Prerequisites

- Python 3.x
- OpenAI API key
- ElevenLabs API key

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

### Usage

Basic usage:
```bash
python -m text2pod [options] input_file
```

Available options:
- `--format`: Override suggested format
- `--technical-depth`: Set technical depth (low/medium/high)
- `--target-duration`: Set target duration in minutes
- `--regenerate-segment`: Regenerate specific segment

## 🔄 Workflow

1. **Document Processing**: Input PDF/Word documents are processed and cleaned
2. **Content Analysis**: Document structure and topics are analyzed
3. **Script Generation**: Content is transformed into natural dialogue
4. **Voice Processing**: Voices are assigned to different parts
5. **Audio Generation**: Final podcast-style audio is generated

## 🏗️ Project Structure

```plaintext
text2pod/
├── src/
│   ├── document_processor.py
│   ├── script_generator.py
│   ├── audio_generator.py
│   ├── utils/
│   │   ├── config.py
│   │   ├── error_handler.py
│   │   └── progress.py
│   └── cli.py
├── tests/
├── config/
└── requirements.txt
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Follow code style guidelines:
   - PEP 8 for Python code
   - Google style docstrings
   - Conventional Commits for commit messages
4. Run tests: `pytest`
5. Submit a pull request

## 📝 License

[Add your license information here]

## 🔮 Future Plans

- Web-based interface
- Multi-user support
- Audio post-processing capabilities
- Custom voice training
- Script template library
- Batch processing support

## ⚠️ Security Notes

- API keys are stored securely in `.env`
- Content validation is implemented
- Rate limiting compliance is enforced
- Error messages are sanitized

## 🆘 Support

[Add support contact information or link to issues]