"""
Tests for command-line interface.
"""

import json
import tempfile
from argparse import Namespace
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from scixtract.cli import (
    extract_command,
    generate_markdown,
    knowledge_command,
    main,
    save_results,
)
from scixtract.models import DocumentMetadata, ExtractionResult, PageContent


class TestSaveResults:
    """Test result saving functionality."""

    def test_save_results(self):
        """Test saving extraction results."""
        # Create test data
        metadata = DocumentMetadata(
            cite_key="test2024", title="Test Paper", authors=["Smith, J."], year="2024"
        )
        pages = [
            PageContent(
                page_num=1,
                raw_text="Test content",
                processed_text="Processed test content",
            )
        ]
        result = ExtractionResult(
            metadata=metadata,
            pages=pages,
            sections={"abstract": []},
            all_keywords=["test", "keyword"],
            key_concepts=["concept1"],
        )

        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            pdf_path = Path("test.pdf")

            saved_files = save_results(result, output_dir, pdf_path)

            # Check that files were created
            assert "extraction_data" in saved_files
            assert "markdown" in saved_files
            assert "keywords" in saved_files

            # Check extraction data file
            extraction_file = Path(saved_files["extraction_data"])
            assert extraction_file.exists()

            with open(extraction_file, "r") as f:
                data = json.load(f)

            assert data["metadata"]["cite_key"] == "test2024"
            assert len(data["pages"]) == 1

            # Check markdown file
            markdown_file = Path(saved_files["markdown"])
            assert markdown_file.exists()

            with open(markdown_file, "r") as f:
                content = f.read()

            assert "Test Paper" in content
            assert "test2024" in content

            # Check keywords file
            keywords_file = Path(saved_files["keywords"])
            assert keywords_file.exists()

            with open(keywords_file, "r") as f:
                keywords_data = json.load(f)

            assert keywords_data["cite_key"] == "test2024"
            assert "test" in keywords_data["keywords"]


class TestGenerateMarkdown:
    """Test markdown generation."""

    def test_generate_markdown_basic(self):
        """Test basic markdown generation."""
        metadata = DocumentMetadata(
            cite_key="test2024",
            title="Test Paper",
            authors=["Smith, J.", "Doe, A."],
            year="2024",
            journal="Test Journal",
        )
        pages = [
            PageContent(
                page_num=1,
                raw_text="Test content",
                processed_text="Processed test content",
                content_type="abstract",
            )
        ]
        result = ExtractionResult(
            metadata=metadata,
            pages=pages,
            sections={
                "abstract": [
                    {
                        "page": 1,
                        "content": "This is the abstract content.",
                        "structured": {"objective": "test objective"},
                    }
                ]
            },
            all_keywords=["test", "keyword", "catalysis"],
            key_concepts=["concept1", "concept2"],
        )

        pdf_path = Path("test.pdf")
        markdown = generate_markdown(result, pdf_path)

        # Check basic structure
        assert "# Test Paper" in markdown
        assert "## Document Information" in markdown
        assert "**Citation Key:** `test2024`" in markdown
        assert "Smith, J., Doe, A." in markdown
        assert "2024" in markdown
        assert "Test Journal" in markdown

        # Check keywords section
        assert "## Keywords and Concepts" in markdown
        assert "test, keyword, catalysis" in markdown
        assert "concept1, concept2" in markdown

        # Check content sections
        assert "## Abstract" in markdown
        assert "### Page 1" in markdown
        assert "This is the abstract content." in markdown

        # Check structured data
        assert "**Structured Information:**" in markdown
        assert "```json" in markdown
        assert "test objective" in markdown

    def test_generate_markdown_with_references(self):
        """Test markdown generation with references section."""
        metadata = DocumentMetadata(cite_key="test2024", title="Test Paper")
        pages: list[PageContent] = []
        result = ExtractionResult(
            metadata=metadata,
            pages=pages,
            sections={
                "references": [
                    {
                        "page": 10,
                        "content": "1. Smith, J. et al. (2023). Test reference.",
                        "structured": {},
                    }
                ]
            },
            all_keywords=[],
            key_concepts=[],
        )

        pdf_path = Path("test.pdf")
        markdown = generate_markdown(result, pdf_path)

        assert "## References" in markdown
        assert "### Page 10" in markdown
        assert "1. Smith, J. et al. (2023). Test reference." in markdown


class TestExtractCommand:
    """Test extract command functionality."""

    @patch("scixtract.cli.AdvancedPDFProcessor")
    @patch("scixtract.cli.save_results")
    def test_extract_command_success(self, mock_save_results, mock_processor_class):
        """Test successful extract command."""
        # Setup mocks
        mock_processor = Mock()
        mock_processor.ai.available = True

        metadata = DocumentMetadata(cite_key="test2024", processing_time=1.5)
        pages = [PageContent(page_num=1, raw_text="test")]
        result = ExtractionResult(
            metadata=metadata,
            pages=pages,
            sections={},
            all_keywords=["test"],
            key_concepts=[],
        )

        mock_processor.process_pdf.return_value = result
        mock_processor_class.return_value = mock_processor

        mock_save_results.return_value = {
            "extraction_data": Path("test_extraction.json"),
            "markdown": Path("test.md"),
            "keywords": Path("test_keywords.json"),
        }

        # Create test arguments
        args = Namespace(
            pdf_file="test.pdf",
            model="test-model",
            output_dir="output",
            bib_file=None,
            update_knowledge=False,
            knowledge_db=None,
        )

        # Create temporary PDF file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
            temp_pdf_path = Path(temp_pdf.name)

        try:
            args.pdf_file = str(temp_pdf_path)

            # Should not raise exception
            extract_command(args)

            # Verify processor was called
            mock_processor_class.assert_called_once()
            mock_processor.process_pdf.assert_called_once()
            mock_save_results.assert_called_once()

        finally:
            if temp_pdf_path.exists():
                temp_pdf_path.unlink()

    def test_extract_command_file_not_found(self):
        """Test extract command with non-existent file."""
        args = Namespace(
            pdf_file="nonexistent.pdf",
            model="test-model",
            output_dir="output",
            bib_file=None,
            update_knowledge=False,
            knowledge_db=None,
        )

        with pytest.raises(SystemExit):
            extract_command(args)

    @patch("scixtract.cli.AdvancedPDFProcessor")
    def test_extract_command_ollama_not_available(self, mock_processor_class):
        """Test extract command when Ollama not available."""
        mock_processor = Mock()
        mock_processor.ai.available = False
        mock_processor_class.return_value = mock_processor

        args = Namespace(
            pdf_file="test.pdf",
            model="test-model",
            output_dir="output",
            bib_file=None,
            update_knowledge=False,
            knowledge_db=None,
        )

        # Create temporary PDF file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
            temp_pdf_path = Path(temp_pdf.name)

        try:
            args.pdf_file = str(temp_pdf_path)

            with pytest.raises(SystemExit):
                extract_command(args)

        finally:
            if temp_pdf_path.exists():
                temp_pdf_path.unlink()

    @patch("scixtract.cli.AdvancedPDFProcessor")
    @patch("scixtract.cli.KnowledgeTracker")
    @patch("scixtract.cli.save_results")
    def test_extract_command_with_knowledge_update(
        self, mock_save_results, mock_tracker_class, mock_processor_class
    ):
        """Test extract command with knowledge update."""
        # Setup mocks
        mock_processor = Mock()
        mock_processor.ai.available = True

        result = ExtractionResult(
            metadata=DocumentMetadata(cite_key="test2024", processing_time=1.0),
            pages=[],
            sections={},
            all_keywords=[],
            key_concepts=[],
        )
        mock_processor.process_pdf.return_value = result
        mock_processor_class.return_value = mock_processor

        mock_tracker = Mock()
        mock_tracker_class.return_value = mock_tracker

        extraction_file = Path("test_extraction.json")
        mock_save_results.return_value = {"extraction_data": extraction_file}

        args = Namespace(
            pdf_file="test.pdf",
            model="test-model",
            output_dir="output",
            bib_file=None,
            update_knowledge=True,
            knowledge_db=None,
        )

        # Create temporary files
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
            temp_pdf_path = Path(temp_pdf.name)

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as temp_json:
            temp_json_path = Path(temp_json.name)
            json.dump({"test": "data"}, temp_json)

        try:
            args.pdf_file = str(temp_pdf_path)
            mock_save_results.return_value = {"extraction_data": temp_json_path}

            extract_command(args)

            # Verify knowledge tracker was used
            mock_tracker_class.assert_called_once()
            mock_tracker.add_extraction_result.assert_called_once()

        finally:
            for path in [temp_pdf_path, temp_json_path]:
                if path.exists():
                    path.unlink()


class TestKnowledgeCommand:
    """Test knowledge command functionality."""

    @patch("scixtract.cli.KnowledgeTracker")
    def test_knowledge_command_search(self, mock_tracker_class):
        """Test knowledge search command."""
        mock_tracker = Mock()
        mock_tracker.search_keywords.return_value = [
            {
                "cite_key": "test2024",
                "title": "Test Paper",
                "authors": ["Smith, J."],
                "keyword": "catalysis",
                "context": "This paper discusses catalysis and its applications.",
                "page_num": 1,
            }
        ]
        mock_tracker_class.return_value = mock_tracker

        args = Namespace(
            search="catalysis",
            stats=False,
            related=None,
            export_graph=None,
            knowledge_db=None,
        )

        # Should not raise exception
        knowledge_command(args)

        mock_tracker.search_keywords.assert_called_once_with("catalysis")

    @patch("scixtract.cli.KnowledgeTracker")
    def test_knowledge_command_stats(self, mock_tracker_class):
        """Test knowledge stats command."""
        mock_tracker = Mock()
        mock_tracker.get_document_stats.return_value = {
            "document_count": 5,
            "page_count": 50,
            "unique_keywords": 100,
            "total_keyword_instances": 500,
            "top_keywords": [("catalysis", 25), ("ammonia", 20)],
            "top_authors": [("Smith, J.", 3), ("Doe, A.", 2)],
        }
        mock_tracker_class.return_value = mock_tracker

        args = Namespace(
            search=None, stats=True, related=None, export_graph=None, knowledge_db=None
        )

        knowledge_command(args)

        mock_tracker.get_document_stats.assert_called_once()

    @patch("scixtract.cli.KnowledgeTracker")
    def test_knowledge_command_related(self, mock_tracker_class):
        """Test knowledge related concepts command."""
        mock_tracker = Mock()
        mock_tracker.get_related_concepts.return_value = [
            ("ammonia", 5),
            ("synthesis", 3),
            ("electrochemical", 2),
        ]
        mock_tracker_class.return_value = mock_tracker

        args = Namespace(
            search=None,
            stats=False,
            related="catalysis",
            export_graph=None,
            knowledge_db=None,
        )

        knowledge_command(args)

        mock_tracker.get_related_concepts.assert_called_once_with("catalysis")


class TestMainCLI:
    """Test main CLI functionality."""

    @patch("scixtract.cli.extract_command")
    def test_main_extract_command(self, mock_extract):
        """Test main CLI with extract command."""
        test_args = ["ai-pdf-extract", "extract", "test.pdf", "--model", "test-model"]

        with patch("sys.argv", test_args):
            main()

        mock_extract.assert_called_once()

    @patch("scixtract.cli.knowledge_command")
    def test_main_knowledge_command(self, mock_knowledge):
        """Test main CLI with knowledge command."""
        test_args = ["ai-pdf-extract", "knowledge", "--search", "catalysis"]

        with patch("sys.argv", test_args):
            main()

        mock_knowledge.assert_called_once()

    def test_main_no_command(self):
        """Test main CLI with no command."""
        test_args = ["ai-pdf-extract"]

        with patch("sys.argv", test_args):
            with patch("argparse.ArgumentParser.print_help") as mock_help:
                main()
                mock_help.assert_called_once()


class TestIntegration:
    """Integration tests for CLI."""

    def test_cli_help(self):
        """Test that CLI help works."""
        test_args = ["ai-pdf-extract", "--help"]

        with patch("sys.argv", test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()

            # Help should exit with code 0
            assert exc_info.value.code == 0

    def test_extract_help(self):
        """Test extract subcommand help."""
        test_args = ["ai-pdf-extract", "extract", "--help"]

        with patch("sys.argv", test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 0

    def test_knowledge_help(self):
        """Test knowledge subcommand help."""
        test_args = ["ai-pdf-extract", "knowledge", "--help"]

        with patch("sys.argv", test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 0
