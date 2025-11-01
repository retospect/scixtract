# scixtract

[![Python](https://img.shields.io/pypi/pyversions/scixtract.svg)](https://pypi.org/project/scixtract/)
[![License](https://img.shields.io/pypi/l/scixtract.svg)](https://github.com/retostamm/scixtract/blob/main/LICENSE)
[![Tests](https://github.com/retostamm/scixtract/actions/workflows/test.yml/badge.svg)](https://github.com/retostamm/scixtract/actions/workflows/test.yml)

**AI-powered scientific PDF extraction using Ollama**

A comprehensive library for extracting text from academic PDFs using AI, with advanced knowledge tracking and search capabilities. Specifically optimized for scientific literature with features like chemical formula preservation, citation integrity, and intelligent content classification.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Features](#features)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

## Installation

### From PyPI (recommended)

```bash
pip install scixtract
```

### From Source

```bash
git clone https://github.com/retostamm/scixtract.git
cd scixtract
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/retostamm/scixtract.git
cd scixtract
pip install -e ".[dev]"
```

## Quick Start

### 1. Setup Ollama (AI Engine)

```bash
# Install Ollama (macOS)
brew install ollama

# Start Ollama service
ollama serve &

# Install recommended model
ollama pull qwen2.5:32b-instruct-q4_K_M

# Or use the setup helper
scixtract-setup-ollama
```

### 2. Extract PDF with AI

```bash
# Basic extraction
scixtract extract paper.pdf

# With specific model
scixtract extract paper.pdf --model qwen2.5:32b-instruct-q4_K_M

# With bibliography integration
scixtract extract paper.pdf --bib-file references.bib --update-knowledge
```

### 3. Search Knowledge Base

```bash
# Search for keywords
scixtract knowledge --search "catalysis"

# Find related concepts
scixtract knowledge --related "ammonia"

# View statistics
scixtract knowledge --stats
```

## Features

### 🤖 **AI-Powered Processing**
- **Multi-pass analysis** with keyword extraction → classification → enhancement
- **Intelligent text fixing** that preserves chemical formulas and citations
- **Content classification** (abstract, methods, results, discussion, etc.)
- **Advanced prompting strategies** optimized for academic papers

### 📚 **Knowledge Management**
- **SQLite database** for fast, searchable knowledge indexing
- **Cross-document concept networks** and relationship mapping
- **Author tracking** and citation networks
- **Knowledge graph export** for visualization

### 🔬 **Academic Optimization**
- **Chemical formula preservation** (NOₓ, NH₃, H₂O, etc.)
- **Citation integrity** maintenance
- **Bibliography integration** from BibTeX files
- **Research context linking** between processed content and bibliography

### 📄 **Multiple Output Formats**
- **Structured JSON** with comprehensive metadata
- **Enhanced Markdown** with AI-generated summaries
- **Keyword indices** for fast searching
- **Knowledge graphs** for visualization

### 🛠 **Professional Tools**
- **Command-line interface** for batch processing
- **Python API** for integration
- **Comprehensive testing** with 95%+ coverage
- **Type hints** throughout

## Usage

### Command Line Interface

#### PDF Extraction

```bash
# Basic extraction
scixtract extract paper.pdf

# Advanced options
scixtract extract paper.pdf \
    --model qwen2.5:32b-instruct-q4_K_M \
    --output-dir ./extractions \
    --bib-file references.bib \
    --update-knowledge

# Batch processing
for pdf in papers/*.pdf; do
    scixtract extract "$pdf" --update-knowledge
done
```

#### Knowledge Management

```bash
# Search for concepts
scixtract knowledge --search "electrochemical conversion"

# Find related concepts
scixtract knowledge --related "NOx reduction"

# Export knowledge graph
scixtract knowledge --export-graph knowledge_graph.json

# View database statistics
scixtract knowledge --stats
```

#### Ollama Setup

```bash
# Check Ollama status
scixtract-setup-ollama --check-only

# List available models
scixtract-setup-ollama --list-models

# Complete setup with recommended model
scixtract-setup-ollama --model qwen2.5:32b-instruct-q4_K_M
```

### Python API

#### Basic Usage

```python
from scixtract import AdvancedPDFProcessor
from pathlib import Path

# Initialize processor
processor = AdvancedPDFProcessor(
    model="qwen2.5:32b-instruct-q4_K_M",
    bib_file=Path("references.bib")
)

# Process PDF
result = processor.process_pdf(Path("paper.pdf"))

# Access results
print(f"Title: {result.metadata.title}")
print(f"Authors: {', '.join(result.metadata.authors)}")
print(f"Keywords: {', '.join(result.all_keywords[:10])}")
print(f"Processing time: {result.metadata.processing_time:.1f}s")
```

#### Knowledge Tracking

```python
from scixtract import KnowledgeTracker

# Initialize tracker
tracker = KnowledgeTracker()

# Add extraction result
tracker.add_extraction_result(result.to_dict(), "paper.pdf")

# Search knowledge base
results = tracker.search_keywords("catalysis")
for result in results:
    print(f"{result['cite_key']}: {result['context']}")

# Get statistics
stats = tracker.get_document_stats()
print(f"Documents: {stats['document_count']}")
print(f"Keywords: {stats['unique_keywords']}")
```

#### Advanced Processing

```python
from scixtract import OllamaAIProcessor

# Custom AI processor
ai = OllamaAIProcessor("custom-model")

# Extract keywords
keywords = ai.extract_keywords_and_concepts("Your text here")
print(keywords["technical_keywords"])

# Classify content
content_type = ai.classify_content_type("Abstract text", 1, 10)
print(f"Content type: {content_type}")

# Fix text spacing
fixed_text = ai.fix_text_spacing("Textwithnospaces")
print(f"Fixed: {fixed_text}")
```

## API Reference

### Core Classes

#### `AdvancedPDFProcessor`
Main processor for PDF extraction with AI enhancement.

```python
processor = AdvancedPDFProcessor(
    model: str = "llama3.2",
    bib_file: Optional[Path] = None
)

result = processor.process_pdf(
    pdf_path: Path,
    bib_file: Optional[Path] = None
) -> ExtractionResult
```

#### `KnowledgeTracker`
Knowledge indexing and search system.

```python
tracker = KnowledgeTracker(db_path: Optional[Path] = None)

tracker.add_extraction_result(result_data: Dict, file_path: str)
results = tracker.search_keywords(query: str, limit: int = 20)
stats = tracker.get_document_stats()
```

#### `OllamaAIProcessor`
AI processing engine using Ollama.

```python
ai = OllamaAIProcessor(
    model: str = "llama3.2",
    base_url: str = "http://localhost:11434"
)

keywords = ai.extract_keywords_and_concepts(text: str)
content_type = ai.classify_content_type(text: str, page_num: int, total_pages: int)
fixed_text = ai.fix_text_spacing(text: str)
```

### Data Models

#### `ExtractionResult`
Complete extraction result with metadata, pages, and analysis.

#### `DocumentMetadata`
Document metadata including title, authors, keywords, and processing info.

#### `PageContent`
Individual page content with classification and keywords.

## Examples

See the [examples/](examples/) directory for complete examples:

- **[basic_extraction.py](examples/basic_extraction.py)** - Simple PDF processing
- **[batch_processing.py](examples/batch_processing.py)** - Process multiple PDFs
- **[knowledge_analysis.py](examples/knowledge_analysis.py)** - Knowledge base analysis
- **[custom_processing.py](examples/custom_processing.py)** - Advanced customization

## Recommended Models

Based on extensive testing with academic papers:

### **Best Overall: qwen2.5:32b-instruct-q4_K_M**
- ✅ **Perfect JSON output** - No parsing errors
- ✅ **Excellent keyword extraction** - High accuracy
- ✅ **Academic content optimized** - Understands research papers
- 📦 **Size**: 19GB

### **Lightweight: llama3.2**
- ✅ **Good performance** - Reliable results
- ✅ **Small size** - Only 2GB
- ✅ **Fast processing** - Quick turnaround
- ⚠ **Occasional JSON issues** - May need post-processing

### **High-End: qwen2:72b**
- ✅ **Superior accuracy** - Best quality results
- ✅ **Complex reasoning** - Handles difficult papers
- ❌ **Large size** - 40GB storage required
- ❌ **Slow processing** - Higher compute requirements

## Requirements

- **Python**: 3.10+
- **Ollama**: For AI processing
- **PyMuPDF**: For PDF text extraction
- **SQLite**: For knowledge indexing (included with Python)

### Optional Dependencies

- **bibtexparser**: For bibliography integration
- **pdfplumber**: Alternative PDF processing
- **unstructured**: Advanced document parsing

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
git clone https://github.com/retostamm/scixtract.git
cd scixtract
pip install -e ".[dev]"
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=scixtract --cov-report=html

# Run specific test file
pytest tests/test_extractor.py -v
```

### Code Quality

```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint code
flake8 src/ tests/
mypy src/

# Security scan
bandit -r src/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this software in your research, please cite:

```bibtex
@software{stamm2024_scixtract,
  author = {Stamm, Reto},
  title = {scixtract: AI-powered scientific PDF extraction using Ollama},
  year = {2024},
  url = {https://github.com/retostamm/scixtract},
  version = {0.1.0}
}
```

## Acknowledgments

- Developed for NOx to Ammonia catalysis research at University of Limerick
- Supervised by Prof. Matthias Vandichel
- Built with [Ollama](https://ollama.ai/) for AI processing
- Uses [PyMuPDF](https://pymupdf.readthedocs.io/) for PDF extraction

---

**Made with ❤️ for the research community**
