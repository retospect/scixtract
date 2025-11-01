#!/usr/bin/env python3
"""
Batch processing example for multiple PDFs.

This example shows how to process multiple PDF files and build
a comprehensive knowledge base from academic papers.
"""

from pathlib import Path
import time
from scixtract import AdvancedPDFProcessor, KnowledgeTracker


def process_pdf_batch(pdf_directory: Path, bib_file: Path = None, model: str = "qwen2.5:7b"):
    """Process all PDFs in a directory and build knowledge base."""
    
    # Find all PDF files
    pdf_files = list(pdf_directory.glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ No PDF files found in {pdf_directory}")
        return
    
    print(f"📚 Found {len(pdf_files)} PDF files to process")
    
    # Initialize processor and knowledge tracker
    processor = AdvancedPDFProcessor(model=model, bib_file=bib_file)
    tracker = KnowledgeTracker()
    
    if not processor.ai.available:
        print(f"❌ Ollama not available with model {model}")
        print("Please install Ollama and run:")
        print(f"   ollama pull {model}")
        return
    
    # Process each PDF
    results = []
    total_start_time = time.time()
    
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"\n📄 Processing {i}/{len(pdf_files)}: {pdf_path.name}")
        
        try:
            # Process PDF
            result = processor.process_pdf(pdf_path, bib_file)
            results.append(result)
            
            # Add to knowledge base
            tracker.add_extraction_result(result.to_dict(), str(pdf_path))
            
            # Show progress
            print(f"   ✅ Completed in {result.metadata.processing_time:.1f}s")
            print(f"   🔑 Keywords: {len(result.all_keywords)}")
            print(f"   📊 Pages: {len(result.pages)}")
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            continue
    
    total_time = time.time() - total_start_time
    
    # Generate batch summary
    print(f"\n🎉 Batch processing completed!")
    print(f"⏱️  Total time: {total_time:.1f} seconds")
    print(f"📚 Successfully processed: {len(results)}/{len(pdf_files)} files")
    
    if results:
        avg_time = sum(r.metadata.processing_time for r in results) / len(results)
        total_keywords = sum(len(r.all_keywords) for r in results)
        total_pages = sum(len(r.pages) for r in results)
        
        print(f"📊 Statistics:")
        print(f"   Average processing time: {avg_time:.1f}s per document")
        print(f"   Total keywords extracted: {total_keywords}")
        print(f"   Total pages processed: {total_pages}")
        
        # Knowledge base statistics
        stats = tracker.get_document_stats()
        print(f"\n🧠 Knowledge Base:")
        print(f"   Documents indexed: {stats['document_count']}")
        print(f"   Unique keywords: {stats['unique_keywords']}")
        print(f"   Total keyword instances: {stats['total_keyword_instances']}")
        
        # Show top keywords across all documents
        if stats['top_keywords']:
            print(f"\n🔥 Top Keywords Across All Documents:")
            for keyword, freq in stats['top_keywords'][:10]:
                print(f"   {keyword}: {freq} occurrences")
        
        # Show top authors
        if stats['top_authors']:
            print(f"\n👥 Most Frequent Authors:")
            for author, count in stats['top_authors'][:5]:
                print(f"   {author}: {count} papers")
    
    return results, tracker


def demonstrate_knowledge_search(tracker: KnowledgeTracker):
    """Demonstrate knowledge base search capabilities."""
    
    print(f"\n🔍 Knowledge Base Search Demo")
    print(f"=" * 40)
    
    # Example searches
    search_terms = ["catalysis", "ammonia", "electrochemical", "NOx", "synthesis"]
    
    for term in search_terms:
        results = tracker.search_keywords(term, limit=3)
        
        if results:
            print(f"\n🔎 Search: '{term}' ({len(results)} results)")
            for result in results[:2]:  # Show top 2 results
                authors = ", ".join(result["authors"][:2])
                if len(result["authors"]) > 2:
                    authors += " et al."
                
                print(f"   📄 {result['cite_key']} - {result['title'][:50]}...")
                print(f"   👥 {authors}")
                print(f"   📝 {result['context'][:100]}...")
        else:
            print(f"\n🔎 Search: '{term}' (no results)")
    
    # Demonstrate concept relationships
    print(f"\n🔗 Related Concepts Demo")
    print(f"=" * 30)
    
    for concept in ["catalysis", "ammonia"]:
        related = tracker.get_related_concepts(concept, limit=5)
        if related:
            print(f"\n💡 Concepts related to '{concept}':")
            for related_concept, count in related:
                print(f"   {related_concept}: {count} co-occurrences")


def main():
    """Main batch processing example."""
    
    # Configuration
    pdf_directory = Path("../test_data")
    bib_file = pdf_directory / "references.bib"
    model = "qwen2.5:7b"  # Change to "qwen2.5:32b-instruct-q4_K_M" for better results
    
    print("🚀 AI PDF Extractor - Batch Processing Example")
    print("=" * 50)
    
    # Check if test data exists
    if not pdf_directory.exists():
        print(f"❌ Test data directory not found: {pdf_directory}")
        print("Please ensure you have test PDFs in the test_data directory")
        return
    
    # Check bibliography file
    if not bib_file.exists():
        print(f"⚠️  Bibliography file not found: {bib_file}")
        print("Processing without bibliography integration")
        bib_file = None
    
    # Process all PDFs
    results, tracker = process_pdf_batch(pdf_directory, bib_file, model)
    
    if results:
        # Demonstrate search capabilities
        demonstrate_knowledge_search(tracker)
        
        # Export knowledge graph
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        graph_file = output_dir / "knowledge_graph.json"
        tracker.export_knowledge_graph(graph_file)
        print(f"\n📊 Knowledge graph exported to: {graph_file}")
        
        print(f"\n✨ Batch processing complete! You now have:")
        print(f"   📚 A searchable knowledge base of {len(results)} documents")
        print(f"   🔍 Fast keyword and concept search capabilities")
        print(f"   🕸️  Knowledge graph for visualization")
        print(f"   📊 Cross-document analysis and relationships")


if __name__ == "__main__":
    main()
