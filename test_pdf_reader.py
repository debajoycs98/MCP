#!/usr/bin/env python3
"""
Test script for PDF Reader MCP server
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp_servers.pdf_reader import read_pdf_text, get_pdf_info, read_pdf_with_ocr

async def main():
    print("🔍 Testing PDF Reader MCP Server")
    print("=" * 60)
    
    # Test with the PDF files in the workspace
    pdf_files = [
        "/Users/debajoymukherjee/Desktop/Programming_llms/2503.14476v2.pdf",
        "/Users/debajoymukherjee/Desktop/Programming_llms/Fundamentals.pdf",
        "/Users/debajoymukherjee/Desktop/Programming_llms/HW-1.pdf",
        "/Users/debajoymukherjee/Desktop/Programming_llms/HW1.pdf",
        "/Users/debajoymukherjee/Desktop/Programming_llms/Programming.pdf"
    ]
    
    # Find the first existing PDF
    test_pdf = None
    for pdf_path in pdf_files:
        if os.path.exists(pdf_path):
            test_pdf = pdf_path
            break
    
    if not test_pdf:
        print("❌ No PDF files found in the workspace")
        return
    
    print(f"\n📄 Testing with: {os.path.basename(test_pdf)}")
    print()
    
    # Test 1: Get PDF Info
    print("Test 1: Getting PDF info...")
    print("-" * 60)
    info_result = await get_pdf_info(test_pdf)
    print(info_result)
    print()
    
    # Test 2: Read PDF Text (first 2 pages)
    print("Test 2: Reading PDF text (first 2 pages)...")
    print("-" * 60)
    text_result = await read_pdf_text(test_pdf, page_start=1, page_end=2)
    print(text_result[:1000] + "..." if len(text_result) > 1000 else text_result)
    print()
    
    # Test 3: Read PDF with OCR (if needed)
    print("Test 3: Reading PDF with OCR (first page)...")
    print("-" * 60)
    print("Note: This may take a while if the PDF has images...")
    ocr_result = await read_pdf_with_ocr(test_pdf, page_start=1, page_end=1)
    print(ocr_result[:800] + "..." if len(ocr_result) > 800 else ocr_result)
    print()
    
    print("=" * 60)
    print("✅ PDF Reader tests completed!")
    print()
    print("You can now use the PDF reader tools in your AI assistant:")
    print("  - read_pdf_text(): Extract text from PDFs")
    print("  - read_pdf_with_ocr(): Extract text including OCR from images")
    print("  - get_pdf_info(): Get PDF metadata")
    print("  - ask_question_about_pdf(): Ask questions about loaded PDFs")

if __name__ == "__main__":
    asyncio.run(main())

