"""
Tests for knowledge tracking functionality.
"""

import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from scixtract.knowledge import KnowledgeTracker


class TestKnowledgeTracker:
    """Test KnowledgeTracker class."""

    def setup_method(self):
        """Set up test fixtures with temporary database."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db_path = Path(self.temp_db.name)
        self.tracker = KnowledgeTracker(self.db_path)

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.db_path.exists():
            self.db_path.unlink()

    def test_init_database(self):
        """Test database initialization."""
        # Check that tables were created
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check documents table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='documents'"
        )
        assert cursor.fetchone() is not None

        # Check pages table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='pages'"
        )
        assert cursor.fetchone() is not None

        # Check keywords table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='keywords'"
        )
        assert cursor.fetchone() is not None

        # Check concept_network table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='concept_network'"
        )
        assert cursor.fetchone() is not None

        conn.close()

    def test_add_extraction_result(self):
        """Test adding extraction result to database."""
        result_data = {
            "metadata": {
                "cite_key": "test2024",
                "title": "Test Paper",
                "authors": ["Smith, J.", "Doe, A."],
                "year": "2024",
                "keywords": ["test", "keyword"],
                "page_count": 2,
                "extraction_date": "2024-01-01",
                "processing_time": 1.5,
            },
            "pages": [
                {
                    "page_num": 1,
                    "content_type": "abstract",
                    "keywords": ["test", "abstract"],
                    "processed_text": "This is a test abstract with test keywords.",
                    "figures": [],
                    "tables": [],
                    "equations": [],
                },
                {
                    "page_num": 2,
                    "content_type": "main",
                    "keywords": ["keyword", "main"],
                    "processed_text": "This is the main content with keyword mentions.",
                    "figures": ["Figure 1"],
                    "tables": [],
                    "equations": [],
                },
            ],
            "key_concepts": ["concept1", "concept2"],
        }

        self.tracker.add_extraction_result(result_data, "/path/to/test.pdf")

        # Verify document was added
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM documents WHERE cite_key = ?", ("test2024",))
        doc_row = cursor.fetchone()
        assert doc_row is not None
        assert doc_row[1] == "Test Paper"  # title

        # Verify pages were added
        cursor.execute("SELECT COUNT(*) FROM pages WHERE cite_key = ?", ("test2024",))
        page_count = cursor.fetchone()[0]
        assert page_count == 2

        # Verify keywords were added
        cursor.execute(
            "SELECT COUNT(*) FROM keywords WHERE cite_key = ?", ("test2024",)
        )
        keyword_count = cursor.fetchone()[0]
        assert keyword_count > 0

        conn.close()

    def test_extract_keyword_context(self):
        """Test keyword context extraction."""
        text = "This is a test sentence with the keyword catalysis in the middle. This is another sentence."
        context = self.tracker._extract_keyword_context("catalysis", text, 50)

        assert "catalysis" in context
        assert len(context) <= 100  # Should be around context_length

    def test_search_keywords_empty_db(self):
        """Test keyword search on empty database."""
        results = self.tracker.search_keywords("test")
        assert results == []

    def test_search_keywords_with_data(self):
        """Test keyword search with data."""
        # Add test data first
        result_data = {
            "metadata": {
                "cite_key": "test2024",
                "title": "Test Paper",
                "authors": ["Smith, J."],
                "year": "2024",
                "keywords": ["catalysis", "ammonia"],
                "page_count": 1,
                "extraction_date": "2024-01-01",
                "processing_time": 1.0,
            },
            "pages": [
                {
                    "page_num": 1,
                    "content_type": "abstract",
                    "keywords": ["catalysis", "ammonia"],
                    "processed_text": "This paper discusses catalysis and ammonia synthesis.",
                    "figures": [],
                    "tables": [],
                    "equations": [],
                }
            ],
            "key_concepts": ["synthesis"],
        }

        self.tracker.add_extraction_result(result_data, "/path/to/test.pdf")

        # Search for keywords
        results = self.tracker.search_keywords("catalysis")

        assert len(results) > 0
        assert results[0]["cite_key"] == "test2024"
        assert results[0]["keyword"] == "catalysis"
        assert "catalysis" in results[0]["context"]

    def test_get_document_stats_empty(self):
        """Test statistics on empty database."""
        stats = self.tracker.get_document_stats()

        assert stats["document_count"] == 0
        assert stats["page_count"] == 0
        assert stats["unique_keywords"] == 0
        assert stats["total_keyword_instances"] == 0
        assert stats["top_keywords"] == []
        assert stats["top_authors"] == []
        assert stats["year_distribution"] == []

    def test_get_document_stats_with_data(self):
        """Test statistics with data."""
        # Add test data
        result_data = {
            "metadata": {
                "cite_key": "test2024",
                "title": "Test Paper",
                "authors": ["Smith, J.", "Doe, A."],
                "year": "2024",
                "keywords": ["catalysis", "ammonia"],
                "page_count": 2,
                "extraction_date": "2024-01-01",
                "processing_time": 1.0,
            },
            "pages": [
                {
                    "page_num": 1,
                    "content_type": "abstract",
                    "keywords": ["catalysis"],
                    "processed_text": "Test content with catalysis.",
                    "figures": [],
                    "tables": [],
                    "equations": [],
                },
                {
                    "page_num": 2,
                    "content_type": "main",
                    "keywords": ["ammonia"],
                    "processed_text": "More content about ammonia.",
                    "figures": [],
                    "tables": [],
                    "equations": [],
                },
            ],
            "key_concepts": ["synthesis"],
        }

        self.tracker.add_extraction_result(result_data, "/path/to/test.pdf")

        stats = self.tracker.get_document_stats()

        assert stats["document_count"] == 1
        assert stats["page_count"] == 2
        assert stats["unique_keywords"] >= 2
        assert stats["total_keyword_instances"] >= 2
        assert len(stats["top_authors"]) >= 2
        assert ("Smith, J.", 1) in stats["top_authors"]
        assert ("Doe, A.", 1) in stats["top_authors"]

    def test_get_related_concepts_empty(self):
        """Test related concepts on empty database."""
        results = self.tracker.get_related_concepts("test")
        assert results == []

    def test_export_knowledge_graph(self):
        """Test knowledge graph export."""
        # Add some test data first
        result_data = {
            "metadata": {
                "cite_key": "test2024",
                "title": "Test Paper",
                "authors": ["Smith, J."],
                "year": "2024",
                "keywords": ["catalysis", "ammonia", "synthesis"],
                "page_count": 1,
                "extraction_date": "2024-01-01",
                "processing_time": 1.0,
            },
            "pages": [
                {
                    "page_num": 1,
                    "content_type": "abstract",
                    "keywords": ["catalysis", "ammonia", "synthesis"],
                    "processed_text": "Test content about catalysis, ammonia, and synthesis.",
                    "figures": [],
                    "tables": [],
                    "equations": [],
                }
            ],
            "key_concepts": ["conversion"],
        }

        self.tracker.add_extraction_result(result_data, "/path/to/test.pdf")

        # Export to temporary file
        temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        temp_output.close()
        output_path = Path(temp_output.name)

        try:
            self.tracker.export_knowledge_graph(output_path)

            # Verify file was created and has content
            assert output_path.exists()
            assert output_path.stat().st_size > 0

            # Verify it's valid JSON
            import json

            with open(output_path, "r") as f:
                graph_data = json.load(f)

            assert "nodes" in graph_data
            assert "edges" in graph_data
            assert "metadata" in graph_data
            assert isinstance(graph_data["nodes"], list)
            assert isinstance(graph_data["edges"], list)

        finally:
            if output_path.exists():
                output_path.unlink()


class TestKnowledgeTrackerCLI:
    """Test command-line interface functionality."""

    @patch("scixtract.knowledge.KnowledgeTracker")
    def test_main_search(self, mock_tracker_class):
        """Test CLI search functionality."""
        mock_tracker = Mock()
        mock_tracker.search_keywords.return_value = [
            {
                "cite_key": "test2024",
                "title": "Test Paper",
                "authors": ["Smith, J."],
                "keyword": "catalysis",
                "context": "This paper discusses catalysis...",
                "page_num": 1,
            }
        ]
        mock_tracker_class.return_value = mock_tracker

        # Import and test main function
        from scixtract.knowledge import main

        with patch("sys.argv", ["knowledge", "--search", "catalysis"]):
            main()

        mock_tracker.search_keywords.assert_called_once_with("catalysis")

    @patch("scixtract.knowledge.KnowledgeTracker")
    def test_main_stats(self, mock_tracker_class):
        """Test CLI stats functionality."""
        mock_tracker = Mock()
        mock_tracker.get_document_stats.return_value = {
            "document_count": 1,
            "page_count": 5,
            "unique_keywords": 10,
            "total_keyword_instances": 25,
            "top_keywords": [("catalysis", 5), ("ammonia", 3)],
            "top_authors": [("Smith, J.", 1)],
        }
        mock_tracker_class.return_value = mock_tracker

        from scixtract.knowledge import main

        with patch("sys.argv", ["knowledge", "--stats"]):
            main()

        mock_tracker.get_document_stats.assert_called_once()


class TestIntegration:
    """Integration tests with test data."""

    def test_with_test_data(self):
        """Test knowledge tracker with test extraction data."""
        # This would test with actual extraction results if available
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_db.close()
        db_path = Path(temp_db.name)

        try:
            tracker = KnowledgeTracker(db_path)

            # Test that we can create and use the tracker
            stats = tracker.get_document_stats()
            assert stats["document_count"] == 0

            # The tracker is ready to receive real extraction data
            assert tracker is not None

        finally:
            if db_path.exists():
                db_path.unlink()
