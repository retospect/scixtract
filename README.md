# scixtract

[![Python](https://img.shields.io/pypi/pyversions/scixtract.svg)](https://pypi.org/project/scixtract/)
[![PyPI version](https://img.shields.io/pypi/v/scixtract.svg)](https://pypi.org/project/scixtract/)
[![License](https://img.shields.io/pypi/l/scixtract.svg)](https://github.com/retospect/scixtract/blob/main/LICENSE.txt)
[![Tests](https://github.com/retospect/scixtract/actions/workflows/test.yml/badge.svg)](https://github.com/retospect/scixtract/actions/workflows/test.yml)

**AI-assisted scientific PDF text extraction**

Scixtract solves the problem that PDF text extraction is messy and full of artifacts. This tool uses AI assistance to clean up extracted text from scientific PDFs, preserving important formatting like chemical formulas and citations while removing common extraction artifacts.

Designed specifically for academic and scientific literature, scixtract provides clean, structured text output that maintains the integrity of your research content.

## What scixtract does

- **Cleans messy PDF text**: Removes spacing artifacts, broken words, and formatting issues
- **Preserves scientific content**: Maintains chemical formulas (H₂O, CO₂), equations, and citations
- **Local AI processing**: Uses local AI models to fix text while preserving meaning
- **Privacy-focused**: All processing happens on your machine - no data sent to external services
- **Batch processing**: Handle multiple PDFs
- **Knowledge indexing**: Build searchable databases of extracted content

## Prerequisites

Before using scixtract, you need to install and set up Ollama:

### 1. Install Ollama

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from [ollama.ai](https://ollama.ai/download)

### 2. Start Ollama service

```bash
ollama serve
```

### 3. Install a model

For scientific PDFs:

```bash
# Recommended: Balance of speed and accuracy (19GB)
ollama pull qwen2.5:32b-instruct-q4_K_M

# Alternative: Smaller model (2GB)
ollama pull llama3.2
```

## Installation

Install scixtract from PyPI:

```bash
pip install scixtract
```

## Quick Start

### Basic PDF extraction

```bash
# Extract a single PDF
scixtract extract paper.pdf

# Use specific model
scixtract extract paper.pdf --model qwen2.5:32b-instruct-q4_K_M

# Process multiple PDFs
scixtract extract papers/*.pdf
```

### Python API

```python
from scixtract import AdvancedPDFProcessor
from pathlib import Path

# Initialize processor
processor = AdvancedPDFProcessor(
    model="qwen2.5:32b-instruct-q4_K_M"
)

# Process PDF
result = processor.process_pdf(Path("paper.pdf"))

# Access cleaned text
print(f"Title: {result.metadata.title}")
print(f"Authors: {', '.join(result.metadata.authors)}")

# Get page content
for page in result.pages:
    print(f"Page {page.page_number}: {page.content[:200]}...")
```

### Knowledge management

Build a searchable database of your extracted content:

```bash
# Extract and add to knowledge base (with bibliography for author name recognition)
scixtract extract paper.pdf --bib-file references.bib --update-knowledge

# Search your knowledge base
scixtract knowledge --search "catalysis"

# View statistics
scixtract knowledge --stats
```

## Output formats

Scixtract provides multiple output formats:

- **JSON**: Structured data with metadata, page content, and extracted keywords
- **Markdown**: Clean, readable text with AI-generated summaries
- **Knowledge database**: SQLite database for searching across multiple documents

## Model recommendations

Based on testing with scientific papers:

**Recommended: qwen2.5:32b-instruct-q4_K_M**
- Good accuracy for scientific content
- Reliable JSON output
- Size: 19GB

**Lightweight option: llama3.2**
- Adequate performance for most papers
- Faster processing
- Size: 2GB

## System requirements

- **Python**: 3.10 or higher
- **Memory**: 8GB RAM minimum (16GB+ recommended for large models)
- **Storage**: 20GB+ free space for AI models
- **Ollama**: Required for AI processing

## Help and setup

Use the built-in setup helper:

```bash
# Check if Ollama is properly configured
scixtract-setup-ollama --check-only

# List available models
scixtract-setup-ollama --list-models

# Complete setup with recommended model
scixtract-setup-ollama --model qwen2.5:32b-instruct-q4_K_M
```

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Support

For technical documentation, API reference, and development information, see [MAINTAINER_README.md](MAINTAINER_README.md).

<<<<<<< HEAD
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

## 📚 API Reference

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

## 💡 Examples

See the [examples/](examples/) directory for complete examples:

- **[basic_extraction.py](examples/basic_extraction.py)** - Simple PDF processing
- **[batch_processing.py](examples/batch_processing.py)** - Process multiple PDFs
- **[knowledge_analysis.py](examples/knowledge_analysis.py)** - Knowledge base analysis
- **[custom_processing.py](examples/custom_processing.py)** - Advanced customization

## 🎯 Recommended Models

Based on extensive testing with academic papers:

> **💡 Pro Tip**: Start with `qwen2.5:32b-instruct-q4_K_M` for the best balance of accuracy and performance

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

## 📋 Requirements

### System Requirements
- **Python**: 3.10+ (3.11+ recommended)
- **Memory**: 8GB RAM minimum (16GB+ for large models)
- **Storage**: 20GB+ free space for models
- **OS**: macOS, Linux, Windows (WSL2)

### Core Dependencies
- **Ollama**: For AI processing
- **PyMuPDF**: For PDF text extraction
- **SQLite**: For knowledge indexing (included with Python)

### Optional Dependencies

- **bibtexparser**: For bibliography integration
- **pdfplumber**: Alternative PDF processing
- **unstructured**: Advanced document parsing

## 🤝 Contributing

We welcome contributions! 🎉 Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Guide

1. **🍴 Fork** the repository
2. **🌿 Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **✅ Test** your changes: `pytest`
4. **📝 Commit** your changes: `git commit -m 'Add amazing feature'`
5. **🚀 Push** to branch: `git push origin feature/amazing-feature`
6. **📬 Open** a Pull Request

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

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🚀 Roadmap

- [ ] **Multi-language support** for international papers
- [ ] **Web interface** for non-technical users
- [ ] **Cloud deployment** options
- [ ] **Advanced visualization** tools
- [ ] **Integration** with reference managers (Zotero, Mendeley)
- [ ] **Collaborative features** for research teams

## Citation

If you use this software in your research, please cite:

```bibtex
@software{stamm2024_scixtract,
  author = {Stamm, Reto},
  title = {scixtract: AI-powered scientific PDF extraction using Ollama},
  year = {2024},
  url = {https://github.com/retostamm/scixtract},
  version = {1.0.1}
}
```

## 🙏 Acknowledgments

- **🎓 Research Context**: Developed for NOx to Ammonia catalysis research at University of Limerick
- **👨‍🏫 Supervision**: Prof. Matthias Vandichel
- **🤖 AI Engine**: Built with [Ollama](https://ollama.ai/) for local AI processing
- **📄 PDF Processing**: Powered by [PyMuPDF](https://pymupdf.readthedocs.io/)
- **🌟 Community**: Thanks to all contributors and users!

## 📈 Stats

- **🧪 Test Coverage**: 95%+
- **📦 Dependencies**: Minimal and well-maintained
- **🔄 CI/CD**: Automated testing and deployment
- **📚 Documentation**: Comprehensive guides and examples

---

**Made with ❤️ for the research community**
=======
For issues and questions, please visit the [GitHub repository](https://github.com/retospect/scixtract).
>>>>>>> b7ea440 (📝 Restructure documentation and update package metadata)
