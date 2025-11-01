# Maintainer Documentation

This document contains technical information for developers and maintainers of scixtract.

## Development Setup

### Installation from source

```bash
git clone https://github.com/retospect/scixtract.git
cd scixtract
pip install -e ".[dev]"
pre-commit install
```

### Running tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=scixtract --cov-report=html

# Run specific test file
pytest tests/test_extractor.py -v
```

### Code quality

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

## API Reference

### Core Classes

#### `AdvancedPDFProcessor`
Main processor for PDF extraction with AI enhancement.

```python
processor = AdvancedPDFProcessor(
    model: str = "qwen2.5:7b",
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
    model: str = "qwen2.5:7b",
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

## Advanced Usage Examples

### Custom AI processor

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

### Knowledge tracking

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

### Bibliography integration

```python
from scixtract import AdvancedPDFProcessor
from pathlib import Path

# Initialize processor with bibliography
processor = AdvancedPDFProcessor(
    model="qwen2.5:32b-instruct-q4_K_M",
    bib_file=Path("references.bib")
)

# Process PDF with bibliography context
result = processor.process_pdf(Path("paper.pdf"))

# Access bibliography-linked metadata
print(f"Cite key: {result.metadata.cite_key}")
print(f"Bibliography context: {result.metadata.bib_context}")
```

## Command Line Interface

### PDF Extraction

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

### Knowledge Management

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

### Ollama Setup

```bash
# Check Ollama status
scixtract-setup-ollama --check-only

# List available models
scixtract-setup-ollama --list-models

# Complete setup with recommended model
scixtract-setup-ollama --model qwen2.5:32b-instruct-q4_K_M
```

## Features

### AI-Powered Processing
- Multi-pass analysis with keyword extraction → classification → enhancement
- Intelligent text fixing that preserves chemical formulas and citations
- Content classification (abstract, methods, results, discussion, etc.)
- Advanced prompting strategies optimized for academic papers

### Knowledge Management
- SQLite database for fast, searchable knowledge indexing
- Cross-document concept networks and relationship mapping
- Author tracking and citation networks
- Knowledge graph export for visualization

### Academic Optimization
- Chemical formula preservation (NOₓ, NH₃, H₂O, etc.)
- Citation integrity maintenance
- Bibliography integration from BibTeX files
- Research context linking between processed content and bibliography

### Multiple Output Formats
- Structured JSON with comprehensive metadata
- Enhanced Markdown with AI-generated summaries
- Keyword indices for fast searching
- Knowledge graphs for visualization

### Professional Tools
- Command-line interface for batch processing
- Python API for integration
- Comprehensive testing with 95%+ coverage
- Type hints throughout

## Examples

See the [examples/](examples/) directory for complete examples:

- **[basic_extraction.py](examples/basic_extraction.py)** - Simple PDF processing
- **[batch_processing.py](examples/batch_processing.py)** - Process multiple PDFs
- **[knowledge_analysis.py](examples/knowledge_analysis.py)** - Knowledge base analysis
- **[custom_processing.py](examples/custom_processing.py)** - Advanced customization

## Model Performance

Based on extensive testing with academic papers:

### qwen2.5:32b-instruct-q4_K_M (Recommended)
- Perfect JSON output - No parsing errors
- Excellent keyword extraction - High accuracy
- Academic content optimized - Understands research papers
- Size: 19GB

### qwen2.5:7b (Lightweight)
- Good performance - Reliable results
- Small size - Only 2GB
- Fast processing - Quick turnaround
- Occasional JSON issues - May need post-processing

### qwen2:72b (High-End)
- Superior accuracy - Best quality results
- Complex reasoning - Handles difficult papers
- Large size - 40GB storage required
- Slow processing - Higher compute requirements

## Dependencies

### Core Dependencies
- **Ollama**: For AI processing
- **PyMuPDF**: For PDF text extraction
- **SQLite**: For knowledge indexing (included with Python)

### Optional Dependencies
- **bibtexparser**: For bibliography integration
- **pdfplumber**: Alternative PDF processing
- **unstructured**: Advanced document parsing

## Contributing

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Test your changes: `pytest`
4. Commit your changes: `git commit -m 'Add amazing feature'`
5. Push to branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

### Development Standards

- **Code Style**: Black formatting, isort imports
- **Type Hints**: Required for all public APIs
- **Testing**: Minimum 90% coverage for new code
- **Documentation**: Docstrings for all public methods
- **Security**: Bandit security scanning

## Architecture

### Processing Pipeline

1. **PDF Text Extraction**: PyMuPDF extracts raw text
2. **AI Enhancement**: Ollama models clean and structure text
3. **Knowledge Indexing**: SQLite stores searchable metadata
4. **Output Generation**: Multiple formats (JSON, Markdown, etc.)

### AI Processing Strategy

- **Multi-pass approach**: Extract → Classify → Enhance → Validate
- **Context-aware prompting**: Different strategies for different content types
- **Error recovery**: Fallback mechanisms for AI failures
- **Performance optimization**: Batch processing and caching

## Troubleshooting

### Common Issues

**Ollama connection errors:**
- Ensure Ollama service is running: `ollama serve`
- Check model availability: `ollama list`
- Verify network connectivity to localhost:11434

**Memory issues with large models:**
- Use smaller models (qwen2.5:7b) for limited RAM
- Close other applications to free memory
- Consider cloud deployment for large-scale processing

**PDF processing errors:**
- Verify PDF is not corrupted or password-protected
- Check file permissions
- Try alternative PDF processing backends

## Performance Tuning

### Model Selection
- Use qwen2.5:32b for best accuracy
- Use qwen2.5:7b for speed and memory efficiency
- Consider model quantization for resource constraints

### Batch Processing
- Process multiple PDFs in parallel
- Use knowledge database updates in batches
- Implement progress tracking for long-running jobs

### Resource Management
- Monitor memory usage during processing
- Implement cleanup for temporary files
- Use connection pooling for database operations
