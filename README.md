# Text2Pod

<p align="center">
  <strong>Transform Documents into Engaging Podcast-Style Audio</strong>
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-getting-started">Getting Started</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-contributing">Contributing</a>
</p>

<!-- Build & Deploy -->
[![CI](https://img.shields.io/github/actions/workflow/status/MarkAC007/text2pod/ci.yml?branch=main&label=CI&logo=github)](https://github.com/MarkAC007/text2pod/actions/workflows/ci.yml)

<!-- Security -->
[![CodeQL](https://img.shields.io/github/actions/workflow/status/MarkAC007/text2pod/codeql.yml?branch=main&label=CodeQL&logo=github)](https://github.com/MarkAC007/text2pod/actions/workflows/codeql.yml)
[![Semgrep](https://img.shields.io/github/actions/workflow/status/MarkAC007/text2pod/semgrep.yml?branch=main&label=Semgrep&logo=semgrep)](https://github.com/MarkAC007/text2pod/actions/workflows/semgrep.yml)
[![Gitleaks](https://img.shields.io/github/actions/workflow/status/MarkAC007/text2pod/gitleaks.yml?branch=main&label=Gitleaks&logo=git)](https://github.com/MarkAC007/text2pod/actions/workflows/gitleaks.yml)
[![License Check](https://img.shields.io/github/actions/workflow/status/MarkAC007/text2pod/license-check.yml?branch=main&label=Licenses&logo=github)](https://github.com/MarkAC007/text2pod/actions/workflows/license-check.yml)

<!-- Tech Stack -->
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-412991?logo=openai&logoColor=white)](https://openai.com/)
[![ElevenLabs](https://img.shields.io/badge/ElevenLabs-Voice%20AI-000000?logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB4PSI2IiB5PSI0IiB3aWR0aD0iNCIgaGVpZ2h0PSIxNiIgZmlsbD0id2hpdGUiLz48cmVjdCB4PSIxNCIgeT0iNCIgd2lkdGg9IjQiIGhlaWdodD0iMTYiIGZpbGw9IndoaXRlIi8+PC9zdmc+)](https://elevenlabs.io/)

<!-- Project Info -->
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Last Commit](https://img.shields.io/github/last-commit/MarkAC007/text2pod)](https://github.com/MarkAC007/text2pod/commits/main)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/MarkAC007/text2pod/pulls)

---

Text2Pod is a Python CLI application that transforms consulting knowledge documents into engaging podcast-style audio content. It processes PDF documents, analyzes their content using AI, and generates natural-sounding podcast conversations with multiple speakers.

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Document Processing** | Extract and analyze content from PDF documents |
| **AI Script Generation** | Convert documents into natural dialogue with multiple speakers |
| **Voice Synthesis** | Generate professional audio using ElevenLabs voices |
| **Multiple Formats** | Support for host-expert interviews, panel discussions |
| **Technical Accuracy** | Preserve technical terms while making content accessible |
| **Interactive Mode** | Step-by-step control over the generation process |

## 🛠️ Tech Stack

- **Python 3.10+** - Core runtime
- **OpenAI GPT-4** - Content analysis and script generation
- **ElevenLabs** - Voice synthesis and audio generation
- **PyPDF2** - PDF document processing
- **pytest** - Testing framework

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- OpenAI API key (for content analysis)
- ElevenLabs API key (for voice synthesis)

### Installation

```bash
# Clone the repository
git clone https://github.com/MarkAC007/text2pod.git
cd text2pod

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r text2pod/requirements.txt
```

### Configuration

Create a `.env` file in the `text2pod/` directory:

```bash
OPENAI_API_KEY=your_openai_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here
```

## 📖 Usage

### Document Processing Mode

Process PDF documents and generate analysis files:

```bash
# Non-interactive (processes all PDFs automatically)
cd text2pod
python src/cli.py

# Interactive mode (step-by-step confirmation)
python src/cli.py --interactive
```

### Podcast Generation Mode

Generate audio from a processed analysis file:

```bash
# Generate podcast from analysis
python src/cli.py --podcast path/to/analysis.json

# With interactive mode
python src/cli.py --podcast path/to/analysis.json --interactive
```

### Additional Options

| Flag | Description |
|------|-------------|
| `--interactive`, `-i` | Enable interactive mode with confirmations |
| `--format` | Override suggested podcast format |
| `--cleanup` | Clean up intermediate audio files |
| `--debug` | Enable detailed debug logging |

## 🔄 Processing Pipeline

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  PDF Document   │ ──▶ │ Content Analysis│ ──▶ │ Script Generation│
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Final Audio    │ ◀── │ Audio Assembly  │ ◀── │ Voice Synthesis │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

1. **Document Processing** - Extract text and structure from PDFs
2. **Content Analysis** - Identify topics, technical terms, complexity
3. **Script Generation** - Create natural dialogue with speaker roles
4. **Voice Synthesis** - Generate speech with ElevenLabs voices
5. **Audio Assembly** - Compile segments into final podcast

## 📁 Project Structure

```
text2pod/
├── src/
│   ├── cli.py                 # Command-line interface
│   ├── document_processor.py  # PDF processing
│   ├── script_generator.py    # Dialogue generation
│   ├── podcast_generator.py   # Audio generation
│   └── utils/
│       ├── audio_generator.py # Voice synthesis
│       ├── voice_mapper.py    # Voice assignment
│       ├── content_analyzer.py# Content analysis
│       ├── json_processor.py  # Data handling
│       ├── openai_client.py   # OpenAI integration
│       └── ...
├── tests/                     # Test suite
├── input/                     # Input PDF documents
├── output/                    # Generated content
└── requirements.txt           # Dependencies
```

## 🧪 Testing

```bash
cd text2pod
pytest tests/ -v
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run linting: `flake8 src/ && black src/ && isort src/`
5. Commit with clear messages
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenAI](https://openai.com/) for GPT-4 API
- [ElevenLabs](https://elevenlabs.io/) for voice synthesis
- All contributors and users of the project

---

<p align="center">
  Made with ❤️ for turning documents into conversations
</p>
