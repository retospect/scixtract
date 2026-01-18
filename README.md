# scixtract

[![Python](https://img.shields.io/pypi/pyversions/scixtract.svg)](https://pypi.org/project/scixtract/)
[![PyPI version](https://img.shields.io/pypi/v/scixtract.svg)](https://pypi.org/project/scixtract/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://github.com/retospect/scixtract/blob/main/LICENSE.txt)
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
# Default model (4.7GB)
ollama pull qwen3:8b
```

## Installation

Install scixtract from PyPI:

```bash
pip install scixtract
```

## Quick Start

### Automatic batch processing (simplest method)

Scixtract uses a directory-based workflow by default. Just create a `pdf/` directory, add your PDFs, and run:

```bash
# Process all PDFs in pdf/ directory automatically
scixtract extract
```

**What happens:**
- First run creates `pdf/`, `md/`, and `working/` directories
- Place PDFs in `pdf/` directory
- Run `scixtract extract` to process all PDFs
- Final cleaned markdown appears in `md/` directory
- Intermediate files stored in `working/` directory
- Uses `qwen3:8b` model by default (no config needed)

**Directory structure:**
```
your-project/
├── pdf/              # Put your PDF files here
├── md/               # Polished markdown outputs go here
└── working/          # Intermediate processing files
```

### Single file extraction

```bash
# Extract a single PDF to custom location
scixtract extract paper.pdf

# Specify output directory
scixtract extract paper.pdf --output-dir results/
```

### Python API

```python
from scixtract import AdvancedPDFProcessor
from pathlib import Path

# Initialize processor
processor = AdvancedPDFProcessor(
    model="qwen3:8b"
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

### Text cleanup utility

Fix PDF-extracted text by removing hyphenation artifacts and reflowing paragraphs:

```bash
# Fix text from a file
scixtract text-fix extracted.txt --output cleaned.txt

# Process from stdin/stdout (useful for pipelines)
cat messy.txt | scixtract text-fix - > clean.txt

# Disable automatic paragraph inference
scixtract text-fix input.txt --no-infer-paragraphs
```

**What it fixes:**
- Removes line-break hyphens (e.g., "hyphen-\nated" → "hyphenated")
- Reflows paragraphs to single lines
- Automatically infers paragraph breaks from sentence endings (enabled by default)

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

**Default: qwen3:8b**
- Good balance of performance and size
- Reliable JSON output for scientific content
- Size: 4.7GB

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

# Complete setup with default model
scixtract-setup-ollama --model qwen3:8b
```

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE.txt](LICENSE.txt) file for details.

## Support

For technical documentation, API reference, and development information, see [MAINTAINER_README.md](MAINTAINER_README.md).

For issues and questions, please visit the [GitHub repository](https://github.com/retospect/scixtract).

---

Built with [Windsurf](https://codeium.com/windsurf).
