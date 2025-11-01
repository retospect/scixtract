"""
Tests for PDF extraction functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json

from scixtract.extractor import OllamaAIProcessor, AdvancedPDFProcessor
from scixtract.models import DocumentMetadata, PageContent


class TestOllamaAIProcessor:
    """Test OllamaAIProcessor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = OllamaAIProcessor("test-model")
    
    @patch('scixtract.extractor.requests.get')
    def test_check_availability_success(self, mock_get):
        """Test successful availability check."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [{"name": "test-model:latest"}]
        }
        mock_get.return_value = mock_response
        
        processor = OllamaAIProcessor("test-model")
        assert processor.available is True
    
    @patch('scixtract.extractor.requests.get')
    def test_check_availability_failure(self, mock_get):
        """Test failed availability check."""
        mock_get.side_effect = Exception("Connection error")
        
        processor = OllamaAIProcessor("test-model")
        assert processor.available is False
    
    @patch('scixtract.extractor.requests.post')
    def test_call_ollama_success(self, mock_post):
        """Test successful Ollama API call."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "test response"}
        mock_post.return_value = mock_response
        
        self.processor.available = True
        result = self.processor._call_ollama("test prompt")
        
        assert result == "test response"
        mock_post.assert_called_once()
    
    def test_call_ollama_not_available(self):
        """Test Ollama API call when not available."""
        self.processor.available = False
        
        with pytest.raises(RuntimeError, match="Ollama not available"):
            self.processor._call_ollama("test prompt")
    
    @patch('scixtract.extractor.requests.post')
    def test_extract_keywords_and_concepts(self, mock_post):
        """Test keyword extraction."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": json.dumps({
                "technical_keywords": ["catalysis", "ammonia"],
                "research_concepts": ["conversion", "efficiency"],
                "chemical_compounds": ["NOx", "NH3"],
                "methodologies": ["electrochemical"],
                "equipment": ["reactor"]
            })
        }
        mock_post.return_value = mock_response
        
        self.processor.available = True
        result = self.processor.extract_keywords_and_concepts("test text")
        
        assert "technical_keywords" in result
        assert "catalysis" in result["technical_keywords"]
        assert "ammonia" in result["technical_keywords"]
    
    @patch('scixtract.extractor.requests.post')
    def test_extract_keywords_invalid_json(self, mock_post):
        """Test keyword extraction with invalid JSON response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "invalid json"}
        mock_post.return_value = mock_response
        
        self.processor.available = True
        result = self.processor.extract_keywords_and_concepts("test text")
        
        # Should return empty structure on JSON parse error
        assert result["technical_keywords"] == []
        assert result["research_concepts"] == []
    
    @patch('scixtract.extractor.requests.post')
    def test_classify_content_type(self, mock_post):
        """Test content type classification."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "abstract"}
        mock_post.return_value = mock_response
        
        self.processor.available = True
        result = self.processor.classify_content_type("test text", 1, 10)
        
        assert result == "abstract"
    
    @patch('scixtract.extractor.requests.post')
    def test_fix_text_spacing(self, mock_post):
        """Test text spacing fix."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "fixed text with proper spacing"}
        mock_post.return_value = mock_response
        
        self.processor.available = True
        result = self.processor.fix_text_spacing("textwithnospaces")
        
        assert result == "fixed text with proper spacing"


class TestAdvancedPDFProcessor:
    """Test AdvancedPDFProcessor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        with patch('scixtract.extractor.OllamaAIProcessor'):
            self.processor = AdvancedPDFProcessor("test-model")
    
    def test_init_without_bib(self):
        """Test initialization without bibliography file."""
        with patch('scixtract.extractor.OllamaAIProcessor'):
            processor = AdvancedPDFProcessor("test-model")
            assert processor.bib_data == {}
    
    @patch('scixtract.extractor.bibtexparser')
    @patch('scixtract.extractor.HAS_BIBTEXPARSER', True)
    def test_load_bibliography_success(self, mock_bibtexparser):
        """Test successful bibliography loading."""
        mock_db = Mock()
        mock_db.entries = [
            {"ID": "test2024", "title": "Test Paper", "author": "Smith, J."}
        ]
        mock_bibtexparser.load.return_value = mock_db
        
        bib_file = Path("test.bib")
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', create=True):
                processor = AdvancedPDFProcessor("test-model", bib_file)
                
        assert "test2024" in processor.bib_data
        assert processor.bib_data["test2024"]["title"] == "Test Paper"
    
    def test_get_metadata_from_bib(self):
        """Test metadata extraction from bibliography."""
        self.processor.bib_data = {
            "test2024": {
                "title": "Test Paper",
                "author": "Smith, J. and Doe, A.",
                "year": "2024",
                "journal": "Test Journal",
                "doi": "10.1000/test",
                "url": "https://example.com"
            }
        }
        
        metadata = self.processor._get_metadata_from_bib("test2024")
        
        assert metadata.cite_key == "test2024"
        assert metadata.title == "Test Paper"
        assert len(metadata.authors) == 2
        assert "Smith, J." in metadata.authors
        assert "Doe, A." in metadata.authors
        assert metadata.year == "2024"
        assert metadata.journal == "Test Journal"
    
    def test_get_metadata_from_bib_not_found(self):
        """Test metadata extraction for non-existent citation."""
        self.processor.bib_data = {}
        
        metadata = self.processor._get_metadata_from_bib("nonexistent2024")
        
        assert metadata.cite_key == "nonexistent2024"
        assert metadata.title == ""
        assert metadata.authors == []
    
    @patch('scixtract.extractor.fitz')
    @patch('scixtract.extractor.HAS_PYMUPDF', True)
    def test_extract_pdf_content(self, mock_fitz):
        """Test PDF content extraction."""
        # Mock PyMuPDF document
        mock_doc = Mock()
        mock_page = Mock()
        mock_page.get_text.return_value = "Test page content"
        mock_doc.load_page.return_value = mock_page
        # Configure the mock to support len() properly
        mock_doc.__len__ = Mock(return_value=2)
        mock_fitz.open.return_value = mock_doc
        
        pdf_path = Path("test.pdf")
        pages = self.processor.extract_pdf_content(pdf_path)
        
        assert len(pages) == 2
        assert pages[0].page_num == 1
        assert pages[0].raw_text == "Test page content"
        assert pages[1].page_num == 2
        mock_doc.close.assert_called_once()
    
    @patch('scixtract.extractor.HAS_PYMUPDF', False)
    def test_extract_pdf_content_no_pymupdf(self):
        """Test PDF extraction without PyMuPDF."""
        pdf_path = Path("test.pdf")
        
        with pytest.raises(RuntimeError, match="PyMuPDF not available"):
            self.processor.extract_pdf_content(pdf_path)
    
    def test_process_with_ai_not_available(self):
        """Test AI processing when Ollama not available."""
        self.processor.ai.available = False
        
        pages = [PageContent(page_num=1, raw_text="test")]
        metadata = DocumentMetadata(cite_key="test2024")
        
        with pytest.raises(RuntimeError, match="AI processing not available"):
            self.processor.process_with_ai(pages, metadata)
    
    def test_process_with_ai_success(self):
        """Test successful AI processing."""
        # Mock AI processor
        self.processor.ai.available = True
        self.processor.ai.extract_keywords_and_concepts = Mock(return_value={
            "technical_keywords": ["test", "keyword"],
            "research_concepts": ["concept1", "concept2"],
            "chemical_compounds": ["H2O"],
            "methodologies": ["method1"],
            "equipment": ["instrument1"]
        })
        self.processor.ai.fix_text_spacing = Mock(return_value="fixed text")
        self.processor.ai.classify_content_type = Mock(return_value="abstract")
        self.processor.ai.extract_structured_content = Mock(return_value={
            "objective": "test objective"
        })
        
        pages = [
            PageContent(page_num=1, raw_text="test text 1"),
            PageContent(page_num=2, raw_text="test text 2")
        ]
        metadata = DocumentMetadata(cite_key="test2024")
        
        result = self.processor.process_with_ai(pages, metadata)
        
        assert isinstance(result.metadata, DocumentMetadata)
        assert len(result.pages) == 2
        assert len(result.all_keywords) > 0
        assert "test" in result.all_keywords
        assert "keyword" in result.all_keywords
        
        # Check that AI methods were called
        self.processor.ai.extract_keywords_and_concepts.assert_called_once()
        assert self.processor.ai.fix_text_spacing.call_count == 2
        assert self.processor.ai.classify_content_type.call_count == 2


class TestIntegration:
    """Integration tests using test data."""
    
    def test_with_test_pdfs(self):
        """Test with actual test PDF files if available."""
        test_data_dir = Path(__file__).parent.parent / "test_data"
        
        if not test_data_dir.exists():
            pytest.skip("Test data directory not found")
        
        pdf_files = list(test_data_dir.glob("*.pdf"))
        if not pdf_files:
            pytest.skip("No test PDF files found")
        
        # Test that we can at least initialize the processor
        with patch('scixtract.extractor.OllamaAIProcessor') as mock_ai:
            mock_ai.return_value.available = False  # Skip AI processing in tests
            
            processor = AdvancedPDFProcessor("test-model")
            assert processor is not None
    
    def test_with_test_bibliography(self):
        """Test with test bibliography file if available."""
        test_data_dir = Path(__file__).parent.parent / "test_data"
        bib_file = test_data_dir / "references.bib"
        
        if not bib_file.exists():
            pytest.skip("Test bibliography file not found")
        
        with patch('scixtract.extractor.OllamaAIProcessor'):
            processor = AdvancedPDFProcessor("test-model", bib_file)
            
            # Should have loaded some bibliography data
            if processor.bib_data:
                # Test that we can extract metadata for known keys
                for cite_key in processor.bib_data.keys():
                    metadata = processor._get_metadata_from_bib(cite_key)
                    assert metadata.cite_key == cite_key
                    break  # Test at least one entry
