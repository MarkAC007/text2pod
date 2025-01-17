"""Setup configuration for Text2Pod."""
from setuptools import setup, find_packages

setup(
    name="text2pod",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'python-dotenv>=1.0.0',
        'PyPDF2>=3.0.0',
        'python-docx>=1.0.0',
        'tqdm>=4.66.0',
        'openai>=1.0.0',
        'elevenlabs>=0.3.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'black>=23.0.0',
            'flake8>=6.1.0',
            'isort>=5.12.0',
        ],
    },
    python_requires='>=3.8',
) 