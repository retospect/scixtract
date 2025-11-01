"""
Tests for data models.
"""

import pytest
from datetime import datetime
from scixtract.models import (
    DocumentMetadata, PageContent, ExtractionResult, 
    DocumentIndex, PageIndex, ConceptNetwork
)


class TestDocumentMetadata:
    """Test DocumentMetadata model."""
    
    def test_init_with_defaults(self):
        """Test initialization with default values."""
        metadata = DocumentMetadata(cite_key="test2024")
        
        assert metadata.cite_key == "test2024"
        assert metadata.title == ""
        assert metadata.authors == []
        assert metadata.keywords == []
        assert metadata.extraction_date != ""
        
    def test_init_with_values(self):
        """Test initialization with provided values."""
        authors = ["Smith, J.", "Doe, A."]
        keywords = ["catalysis", "ammonia"]
        
        metadata = DocumentMetadata(
            cite_key="smith2024",
            title="Test Paper",
            authors=authors,
            keywords=keywords,
            year="2024"
        )
        
        assert metadata.cite_key == "smith2024"
        assert metadata.title == "Test Paper"
        assert metadata.authors == authors
        assert metadata.keywords == keywords
        assert metadata.year == "2024"
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        metadata = DocumentMetadata(
            cite_key="test2024",
            title="Test Paper",
            year="2024"
        )
        
        result = metadata.to_dict()
        
        assert isinstance(result, dict)
        assert result["cite_key"] == "test2024"
        assert result["title"] == "Test Paper"
        assert result["year"] == "2024"
        assert "extraction_date" in result


class TestPageContent:
    """Test PageContent model."""
    
    def test_init_with_defaults(self):
        """Test initialization with default values."""
        page = PageContent(page_num=1, raw_text="Test text")
        
        assert page.page_num == 1
        assert page.raw_text == "Test text"
        assert page.processed_text == ""
        assert page.content_type == "main"
        assert page.keywords == []
        assert page.figures == []
        assert page.tables == []
        assert page.equations == []
    
    def test_init_with_values(self):
        """Test initialization with provided values."""
        keywords = ["test", "keyword"]
        figures = ["Figure 1"]
        
        page = PageContent(
            page_num=2,
            raw_text="Raw text",
            processed_text="Processed text",
            content_type="abstract",
            keywords=keywords,
            figures=figures
        )
        
        assert page.page_num == 2
        assert page.raw_text == "Raw text"
        assert page.processed_text == "Processed text"
        assert page.content_type == "abstract"
        assert page.keywords == keywords
        assert page.figures == figures
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        page = PageContent(
            page_num=1,
            raw_text="Test text",
            content_type="methods"
        )
        
        result = page.to_dict()
        
        assert isinstance(result, dict)
        assert result["page_num"] == 1
        assert result["raw_text"] == "Test text"
        assert result["content_type"] == "methods"


class TestExtractionResult:
    """Test ExtractionResult model."""
    
    def test_init(self):
        """Test initialization."""
        metadata = DocumentMetadata(cite_key="test2024")
        pages = [PageContent(page_num=1, raw_text="Test")]
        sections = {"abstract": []}
        keywords = ["test", "keyword"]
        concepts = ["concept1"]
        
        result = ExtractionResult(
            metadata=metadata,
            pages=pages,
            sections=sections,
            all_keywords=keywords,
            key_concepts=concepts
        )
        
        assert result.metadata == metadata
        assert result.pages == pages
        assert result.sections == sections
        assert result.all_keywords == keywords
        assert result.key_concepts == concepts
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        metadata = DocumentMetadata(cite_key="test2024")
        pages = [PageContent(page_num=1, raw_text="Test")]
        
        result = ExtractionResult(
            metadata=metadata,
            pages=pages,
            sections={},
            all_keywords=["test"],
            key_concepts=["concept"]
        )
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert "metadata" in result_dict
        assert "pages" in result_dict
        assert "sections" in result_dict
        assert "all_keywords" in result_dict
        assert "key_concepts" in result_dict
        
        # Check nested conversions
        assert isinstance(result_dict["metadata"], dict)
        assert isinstance(result_dict["pages"], list)
        assert isinstance(result_dict["pages"][0], dict)


class TestDocumentIndex:
    """Test DocumentIndex model."""
    
    def test_init(self):
        """Test initialization."""
        authors = ["Smith, J."]
        keywords = ["test"]
        concepts = ["concept"]
        
        index = DocumentIndex(
            cite_key="test2024",
            title="Test Paper",
            authors=authors,
            year="2024",
            keywords=keywords,
            key_concepts=concepts,
            page_count=10,
            extraction_date="2024-01-01",
            file_path="/path/to/file"
        )
        
        assert index.cite_key == "test2024"
        assert index.title == "Test Paper"
        assert index.authors == authors
        assert index.year == "2024"
        assert index.keywords == keywords
        assert index.key_concepts == concepts
        assert index.page_count == 10
        assert index.extraction_date == "2024-01-01"
        assert index.file_path == "/path/to/file"
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        index = DocumentIndex(
            cite_key="test2024",
            title="Test Paper",
            authors=["Smith, J."],
            year="2024",
            keywords=["test"],
            key_concepts=["concept"],
            page_count=10,
            extraction_date="2024-01-01",
            file_path="/path/to/file"
        )
        
        result = index.to_dict()
        
        assert isinstance(result, dict)
        assert result["cite_key"] == "test2024"
        assert result["title"] == "Test Paper"
        assert result["authors"] == ["Smith, J."]


class TestPageIndex:
    """Test PageIndex model."""
    
    def test_init(self):
        """Test initialization."""
        keywords = ["test", "keyword"]
        
        index = PageIndex(
            cite_key="test2024",
            page_num=1,
            content_type="abstract",
            keywords=keywords,
            word_count=100,
            has_figures=True,
            has_tables=False,
            has_equations=True
        )
        
        assert index.cite_key == "test2024"
        assert index.page_num == 1
        assert index.content_type == "abstract"
        assert index.keywords == keywords
        assert index.word_count == 100
        assert index.has_figures is True
        assert index.has_tables is False
        assert index.has_equations is True


class TestConceptNetwork:
    """Test ConceptNetwork model."""
    
    def test_init(self):
        """Test initialization."""
        related = ["concept2", "concept3"]
        documents = ["doc1", "doc2"]
        
        network = ConceptNetwork(
            concept="concept1",
            related_concepts=related,
            documents=documents,
            frequency=5,
            co_occurrence_score=0.8
        )
        
        assert network.concept == "concept1"
        assert network.related_concepts == related
        assert network.documents == documents
        assert network.frequency == 5
        assert network.co_occurrence_score == 0.8
