"""
Command-line interface for AI PDF extractor.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from .config import ConfigManager, get_config
from .extractor import AdvancedPDFProcessor
from .knowledge import KnowledgeTracker
from .models import ExtractionResult


def parse_makefile_args(args_list: List[str]) -> Tuple[Dict[str, Any], List[str]]:
    """Parse Makefile-style KEY=VALUE arguments."""
    makefile_args: Dict[str, Any] = {}
    remaining_args: List[str] = []

    for arg in args_list:
        if "=" in arg and not arg.startswith("-"):
            key, value_str = arg.split("=", 1)
            # Convert to lowercase and handle boolean values
            key = key.lower()
            value: Union[str, bool] = value_str
            if value_str.lower() in ["true", "1", "yes", "on"]:
                value = True
            elif value_str.lower() in ["false", "0", "no", "off"]:
                value = False
            makefile_args[key] = value
        else:
            remaining_args.append(arg)

    return makefile_args, remaining_args


def save_results(result: ExtractionResult, output_dir: Path, pdf_path: Path) -> Dict[str, str]:
    """Save extraction results in multiple formats."""
    base_name = pdf_path.stem
    saved_files = {}

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save raw extraction data
    raw_file = output_dir / f"{base_name}_ai_extraction.json"
    with open(raw_file, "w", encoding="utf-8") as f:
        json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
    saved_files["extraction_data"] = raw_file

    # Save structured markdown
    md_file = output_dir / f"{base_name}_ai_processed.md"
    markdown_content = generate_markdown(result, pdf_path)
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    saved_files["markdown"] = md_file

    # Save keyword index
    keywords_file = output_dir / f"{base_name}_keywords.json"
    with open(keywords_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "cite_key": result.metadata.cite_key,
                "title": result.metadata.title,
                "keywords": result.all_keywords,
                "key_concepts": result.key_concepts,
                "extraction_date": result.metadata.extraction_date,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
    saved_files["keywords"] = keywords_file

    return saved_files


def generate_markdown(result: ExtractionResult, pdf_path: Path) -> str:
    """Generate structured markdown from extraction result."""
    lines = []
    metadata = result.metadata

    # Header with metadata
    lines.extend(
        [
            f"# {metadata.title or pdf_path.stem.replace('_', ' ').title()}",
            "",
            "## Document Information",
            "",
            f"**Citation Key:** `{metadata.cite_key}`  ",
            f"**Authors:** {', '.join(metadata.authors) if metadata.authors else 'Unknown'}  ",
            f"**Year:** {metadata.year or 'Unknown'}  ",
            f"**Journal:** {metadata.journal or 'Unknown'}  ",
            f"**DOI:** {metadata.doi or 'Not available'}  ",
            f"**Processed:** {metadata.extraction_date}  ",
            "",
            "## Keywords and Concepts",
            "",
            f"**Keywords:** {', '.join(result.all_keywords[:15])}  ",
            f"**Key Concepts:** {', '.join(result.key_concepts[:10])}  ",
            "",
            "---",
            "",
        ]
    )

    # Process sections
    section_order = [
        "abstract",
        "introduction",
        "methods",
        "results",
        "discussion",
        "conclusion",
        "main",
    ]

    for section_type in section_order:
        if section_type in result.sections:
            section_data = result.sections[section_type]
            lines.extend([f"## {section_type.title()}", ""])

            for item in section_data:
                lines.extend([f"### Page {item['page']}", "", item["content"], ""])

                # Add structured data if available
                if (
                    item.get("structured")
                    and "extraction_error" not in item["structured"]
                ):
                    lines.extend(
                        [
                            "**Structured Information:**",
                            "",
                            f"```json",
                            json.dumps(item["structured"], indent=2),
                            "```",
                            "",
                        ]
                    )

    # Add references section if exists
    if "references" in result.sections:
        lines.extend(["## References", ""])
        for item in result.sections["references"]:
            lines.extend([f"### Page {item['page']}", "", item["content"], ""])

    return "\n".join(lines)


def extract_command(args: argparse.Namespace) -> None:
    """Handle PDF extraction command."""
    # Parse Makefile-style arguments from remaining args
    makefile_args = {}
    if hasattr(args, "makefile_args"):
        makefile_args = args.makefile_args

    # Load configuration
    config_manager = ConfigManager(getattr(args, "config", None))
    config = config_manager.config

    pdf_path = Path(args.pdf_file)

    if not pdf_path.exists():
        print(f"❌ PDF file not found: {args.pdf_file}")
        sys.exit(1)

    # Setup output directory (Makefile args > command line > config)
    output_dir_path = (
        makefile_args.get("output_dir")
        or getattr(args, "output_dir", None)
        or config.extraction.output_dir
    )
    output_dir = Path(output_dir_path)

    # Setup bibliography file (Makefile args > command line)
    bib_file = None
    bib_file_path = makefile_args.get("bib_file") or getattr(args, "bib_file", None)
    if bib_file_path:
        bib_file = Path(bib_file_path)
        if not bib_file.exists():
            print(f"⚠ Bibliography file not found: {bib_file_path}")

    # Get model (Makefile args > command line > config > environment)
    model = (
        makefile_args.get("model")
        or getattr(args, "model", None)
        or os.getenv("OLLAMA_MODEL")
        or config.ollama.model
    )

    # Initialize processor with config
    processor = AdvancedPDFProcessor(model, bib_file)
    processor.ai.base_url = config.ollama.base_url

    if not processor.ai.available:
        print("❌ Ollama not available. Please install Ollama and run:")
        print(f"   ollama pull {args.model}")
        sys.exit(1)

    try:
        print(f"🚀 Processing PDF: {pdf_path.name}")
        print(f"📋 Citation key: {pdf_path.stem}")
        print(f"🤖 AI Model: {model}")

        # Process PDF
        result = processor.process_pdf(pdf_path, bib_file)

        # Save results
        print("💾 Saving results...")
        saved_files = save_results(result, output_dir, pdf_path)

        # Update knowledge tracker if requested (Makefile args > command line > config)
        update_knowledge = makefile_args.get("update_knowledge") or getattr(
            args, "update_knowledge", None
        )
        if update_knowledge is None:
            update_knowledge = config.extraction.update_knowledge

        if update_knowledge:
            print("🔄 Updating knowledge index...")
            # Use knowledge DB from config or command line
            knowledge_db = (
                getattr(args, "knowledge_db", None) or config.knowledge.db_path
            )
            tracker = KnowledgeTracker(Path(knowledge_db) if knowledge_db else None)

            # Load the saved extraction data
            with open(saved_files["extraction_data"], "r", encoding="utf-8") as f:
                extraction_data = json.load(f)

            tracker.add_extraction_result(extraction_data, str(pdf_path))
            print("✅ Knowledge index updated")

        # Print summary
        print(
            f"\n✅ Processing completed in {result.metadata.processing_time:.1f} seconds"
        )
        print(f"📝 Extracted {len(result.all_keywords)} keywords")
        print(f"📄 Processed {len(result.pages)} pages")
        print(f"📁 Saved files:")
        for file_type, file_path in saved_files.items():
            print(f"   {file_type}: {file_path}")

    except Exception as e:
        print(f"❌ Processing failed: {e}")
        sys.exit(1)


def knowledge_command(args: argparse.Namespace) -> None:
    """Handle knowledge management commands."""
    # Load configuration
    config_manager = ConfigManager(getattr(args, "config", None))
    config = config_manager.config

    # Use knowledge DB from config or command line
    knowledge_db = getattr(args, "knowledge_db", None) or config.knowledge.db_path
    tracker = KnowledgeTracker(Path(knowledge_db) if knowledge_db else None)

    if args.search:
        results = tracker.search_keywords(args.search)

        if results:
            print(f"\n🔍 Search results for '{args.search}':")
            for result in results:
                authors_str = ", ".join(result["authors"][:2])
                if len(result["authors"]) > 2:
                    authors_str += " et al."

                print(f"\n📄 {result['cite_key']} - {result['title']}")
                print(f"   👥 {authors_str}")
                print(f"   🔑 Keyword: {result['keyword']} (Page {result['page_num']})")
                print(f"   📝 Context: {result['context'][:200]}...")
        else:
            print(f"❌ No results found for '{args.search}'")

    elif args.related:
        related = tracker.get_related_concepts(args.related)

        if related:
            print(f"\n🔗 Concepts related to '{args.related}':")
            for concept, count in related:
                print(f"   • {concept}: {count} co-occurrences")
        else:
            print(f"❌ No related concepts found for '{args.related}'")

    elif args.export_graph:
        output_file = Path(args.export_graph)
        tracker.export_knowledge_graph(output_file)
        print(f"📊 Knowledge graph exported to: {output_file}")

    elif args.stats:
        stats = tracker.get_document_stats()

        print("\n📊 Knowledge Base Summary:")
        print(f"   📚 Documents: {stats['document_count']}")
        print(f"   📄 Pages: {stats['page_count']}")
        print(f"   🔑 Unique keywords: {stats['unique_keywords']}")
        print(f"   📝 Total keyword instances: {stats['total_keyword_instances']}")

        if stats["top_keywords"]:
            print(f"\n🔥 Top Keywords:")
            for keyword, freq in stats["top_keywords"][:5]:
                print(f"   • {keyword}: {freq}")

        if stats["top_authors"]:
            print(f"\n👥 Top Authors:")
            for author, count in stats["top_authors"][:5]:
                print(f"   • {author}: {count} papers")


def config_command(args: argparse.Namespace) -> None:
    """Handle configuration management commands."""
    config_manager = ConfigManager(getattr(args, "config", None))

    if args.create_example:
        example_config = config_manager.create_example_config(args.create_example)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(example_config)
            print(f"✅ Example configuration saved to: {args.output}")
        else:
            print("📋 Example Configuration:")
            print("=" * 30)
            print(example_config)

    elif args.show:
        config_manager.print_config()

    elif args.save:
        config_manager.save_config(args.save)

    else:
        print("📋 Configuration Management")
        print("Use --help for available options")


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI-powered PDF text extraction and knowledge indexing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  # Extract PDF with AI processing
  scixtract extract paper.pdf --model qwen2.5:32b-instruct-q4_K_M
  
  # Extract with bibliography integration (Makefile-friendly)
  scixtract extract paper.pdf BIB_FILE=references.bib UPDATE_KNOWLEDGE=true
  
  # Using environment variables (Makefile-friendly)
  OLLAMA_MODEL=qwen2.5:32b-instruct-q4_K_M scixtract extract paper.pdf
  
  # Search knowledge base
  scixtract knowledge --search "catalysis"
  
  # Configuration management
  scixtract config --create-example json
  scixtract config --show
        """,
    )

    # Global options
    parser.add_argument("--config", "-c", help="Path to configuration file")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract text from PDF")
    extract_parser.add_argument("pdf_file", help="PDF file to process")
    extract_parser.add_argument(
        "--model",
        default="qwen2.5:7b",
        help="Ollama model to use (default: qwen2.5:7b)",
    )
    extract_parser.add_argument(
        "--output-dir",
        default="ai_extractions",
        help="Output directory (default: ai_extractions)",
    )
    extract_parser.add_argument(
        "--bib-file", help="Bibliography file for metadata extraction"
    )
    extract_parser.add_argument(
        "--update-knowledge",
        action="store_true",
        help="Update knowledge index after extraction",
    )
    extract_parser.add_argument(
        "--knowledge-db", help="Path to knowledge database file"
    )

    # Knowledge command
    knowledge_parser = subparsers.add_parser("knowledge", help="Manage knowledge base")
    knowledge_parser.add_argument(
        "--search", help="Search for keywords in the knowledge base"
    )
    knowledge_parser.add_argument(
        "--stats", action="store_true", help="Show knowledge base statistics"
    )
    knowledge_parser.add_argument(
        "--related", help="Find concepts related to given concept"
    )
    knowledge_parser.add_argument(
        "--export-graph", help="Export knowledge graph to JSON file"
    )
    knowledge_parser.add_argument(
        "--knowledge-db", help="Path to knowledge database file"
    )

    # Config command
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_parser.add_argument(
        "--create-example",
        choices=["json", "yaml"],
        help="Create example configuration file",
    )
    config_parser.add_argument(
        "--output", "-o", help="Output file path for example config"
    )
    config_parser.add_argument(
        "--show", action="store_true", help="Show current configuration"
    )
    config_parser.add_argument("--save", help="Save current configuration to file")

    # Parse arguments, handling Makefile-style KEY=VALUE syntax
    import sys

    makefile_args, remaining_args = parse_makefile_args(sys.argv[1:])
    args = parser.parse_args(remaining_args)

    # Add makefile args to the args namespace
    args.makefile_args = makefile_args

    if args.command == "extract":
        extract_command(args)
    elif args.command == "knowledge":
        knowledge_command(args)
    elif args.command == "config":
        config_command(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
