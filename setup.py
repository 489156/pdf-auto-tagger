"""
AI-Powered PDF Auto-Tagging System Setup
"""

from setuptools import setup, find_packages
from pathlib import Path

# README 읽기
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="pdf-auto-tagger",
    version="0.1.0",
    description="AI 기반 PDF 자동 태깅 시스템",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="APATS Development Team",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "PyMuPDF>=1.23.8",
        "pdfplumber>=0.10.3",
        "pypdf>=3.17.4",
        "reportlab>=4.0.7",
        "openai>=1.12.0",
        "langchain>=0.1.0",
        "Pillow>=10.2.0",
        "opencv-python>=4.9.0",
        "pytesseract>=0.3.10",
        "numpy>=1.26.3",
        "pandas>=2.0.3",
        "pyyaml>=6.0.1",
        "python-dotenv>=1.0.0",
        "tqdm>=4.66.1",
        "click>=8.1.7",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "black>=23.12.0",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pdf-tagger=src.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
    ],
)
