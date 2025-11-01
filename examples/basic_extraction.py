#!/usr/bin/env python3
"""
Basic PDF extraction example using AI PDF Extractor.

This example demonstrates the simplest way to extract text from a PDF
using AI-powered processing with Ollama.
"""

from pathlib import Path
from scixtract import AdvancedPDFProcessor


def main():
    """Extract text from a PDF file with AI processing."""
    
    # Path to your PDF file
    pdf_path = Path("../test_data/ngoipala2025.pdf")
    
    if not pdf_path.exists():
        print(f"❌ PDF file not found: {pdf_path}")
        print("Please ensure you have test PDFs in the test_data directory")
        return
    
    print(f"🚀 Processing PDF: {pdf_path.name}")
    
    # Initialize the processor with default model (qwen2.5:7b)
    processor = AdvancedPDFProcessor()
    
    # Check if AI is available
    if not processor.ai.available:
        print("❌ Ollama not available. Please install Ollama and run:")
        print("   ollama pull qwen2.5:7b")
        return
    
    try:
        # Process the PDF
        print("🤖 Starting AI processing...")
        result = processor.process_pdf(pdf_path)
        
        # Display results
        print(f"\n✅ Processing completed in {result.metadata.processing_time:.1f} seconds")
        print(f"📄 Document: {result.metadata.title or pdf_path.stem}")
        print(f"👥 Authors: {', '.join(result.metadata.authors) if result.metadata.authors else 'Unknown'}")
        print(f"📅 Year: {result.metadata.year or 'Unknown'}")
        print(f"📊 Pages processed: {len(result.pages)}")
        print(f"🔑 Keywords extracted: {len(result.all_keywords)}")
        
        # Show top keywords
        if result.all_keywords:
            print(f"\n🔥 Top Keywords:")
            for i, keyword in enumerate(result.all_keywords[:10], 1):
                print(f"   {i}. {keyword}")
        
        # Show key concepts
        if result.key_concepts:
            print(f"\n💡 Key Concepts:")
            for i, concept in enumerate(result.key_concepts[:5], 1):
                print(f"   {i}. {concept}")
        
        # Show content types found
        content_types = set(page.content_type for page in result.pages)
        print(f"\n📋 Content Types Found: {', '.join(sorted(content_types))}")
        
        # Save results to files
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        base_name = pdf_path.stem
        
        # Save JSON data
        json_file = output_dir / f"{base_name}_extraction.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            import json
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        
        # Save simple text summary
        summary_file = output_dir / f"{base_name}_summary.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"PDF Extraction Summary\n")
            f.write(f"====================\n\n")
            f.write(f"File: {pdf_path.name}\n")
            f.write(f"Title: {result.metadata.title or 'Unknown'}\n")
            f.write(f"Authors: {', '.join(result.metadata.authors) if result.metadata.authors else 'Unknown'}\n")
            f.write(f"Year: {result.metadata.year or 'Unknown'}\n")
            f.write(f"Pages: {len(result.pages)}\n")
            f.write(f"Processing time: {result.metadata.processing_time:.1f}s\n\n")
            
            f.write(f"Keywords ({len(result.all_keywords)}):\n")
            for keyword in result.all_keywords:
                f.write(f"  - {keyword}\n")
            
            f.write(f"\nKey Concepts ({len(result.key_concepts)}):\n")
            for concept in result.key_concepts:
                f.write(f"  - {concept}\n")
            
            f.write(f"\nContent Types: {', '.join(sorted(content_types))}\n")
        
        print(f"\n💾 Results saved:")
        print(f"   📄 JSON data: {json_file}")
        print(f"   📝 Summary: {summary_file}")
        
    except Exception as e:
        print(f"❌ Processing failed: {e}")
        return


if __name__ == "__main__":
    main()
