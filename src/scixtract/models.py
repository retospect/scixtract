"""
Data models for AI PDF extraction and knowledge tracking.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class DocumentMetadata:
    """Comprehensive document metadata structure."""
    cite_key: str
    title: str = ""
    authors: List[str] = None
    year: str = ""
    journal: str = ""
    doi: str = ""
    url: str = ""
    keywords: List[str] = None
    abstract: str = ""
    page_count: int = 0
    extraction_date: str = ""
    processing_time: float = 0.0
    
    def __post_init__(self) -> None:
        if self.authors is None:
            self.authors = []
        if self.keywords is None:
            self.keywords = []
        if not self.extraction_date:
            self.extraction_date = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class PageContent:
    """Structure for individual page content."""
    page_num: int
    raw_text: str
    processed_text: str = ""
    content_type: str = "main"  # main, abstract, references, appendix
    keywords: List[str] = None
    figures: List[str] = None
    tables: List[str] = None
    equations: List[str] = None
    
    def __post_init__(self) -> None:
        if self.keywords is None:
            self.keywords = []
        if self.figures is None:
            self.figures = []
        if self.tables is None:
            self.tables = []
        if self.equations is None:
            self.equations = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class ExtractionResult:
    """Complete extraction result structure."""
    metadata: DocumentMetadata
    pages: List[PageContent]
    sections: Dict[str, Any]
    all_keywords: List[str]
    key_concepts: List[str]
    methodology: str = ""
    main_findings: str = ""
    conclusions: str = ""
    future_work: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "metadata": self.metadata.to_dict(),
            "pages": [page.to_dict() for page in self.pages],
            "sections": self.sections,
            "all_keywords": self.all_keywords,
            "key_concepts": self.key_concepts,
            "methodology": self.methodology,
            "main_findings": self.main_findings,
            "conclusions": self.conclusions,
            "future_work": self.future_work,
        }


@dataclass
class DocumentIndex:
    """Index entry for a processed document."""
    cite_key: str
    title: str
    authors: List[str]
    year: str
    keywords: List[str]
    key_concepts: List[str]
    page_count: int
    extraction_date: str
    file_path: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PageIndex:
    """Index entry for a page within a document."""
    cite_key: str
    page_num: int
    content_type: str
    keywords: List[str]
    word_count: int
    has_figures: bool
    has_tables: bool
    has_equations: bool


@dataclass
class ConceptNetwork:
    """Network of related concepts across documents."""
    concept: str
    related_concepts: List[str]
    documents: List[str]  # cite_keys
    frequency: int
    co_occurrence_score: float
