#!/usr/bin/env python3
"""
MCP Server for PDF Reading with OCR support
Based on https://mcpservers.org/servers/labeveryday/mcp_pdf_reader
Extract text, images, and perform OCR on PDF documents using PyMuPDF and Tesseract OCR
"""

import asyncio
import os
import json
from typing import List, Optional, Dict, Any
from pathlib import Path
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import PDF processing libraries
try:
    import fitz  # PyMuPDF
    HAS_FITZ = True
except ImportError:
    HAS_FITZ = False
    print("Warning: PyMuPDF not available. Install with 'uv add pymupdf'")

try:
    import pytesseract
    from PIL import Image
    HAS_OCR = True
except ImportError:
    HAS_OCR = False
    print("Warning: pytesseract/Pillow not available. OCR features disabled.")
    print("Install with: 'uv add pytesseract pillow' and 'brew install tesseract' (macOS)")

# Import FastMCP
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    from mcp.server import Server
    from mcp.types import Tool, TextContent

# Initialize MCP server
mcp = FastMCP("PDF Reader")

# Global variables for document storage
document_store = {}


@mcp.tool()
async def read_pdf_text(
    file_path: str,
    page_start: Optional[int] = None,
    page_end: Optional[int] = None
) -> str:
    """
    Extract text content from PDF pages.
    
    Args:
        file_path: Path to the PDF file
        page_start: Starting page number (1-indexed, optional)
        page_end: Ending page number (1-indexed, optional)
    
    Returns:
        Extracted text content with page information and statistics
    """
    try:
        if not HAS_FITZ:
            return "Error: PyMuPDF library not available. Install with 'uv add pymupdf'"
        
        if not os.path.exists(file_path):
            return f"Error: File not found at {file_path}"
        
        # Open PDF
        doc = fitz.open(file_path)
        total_pages = len(doc)
        
        # Set page range
        start = (page_start - 1) if page_start else 0
        end = page_end if page_end else total_pages
        start = max(0, min(start, total_pages - 1))
        end = max(start + 1, min(end, total_pages))
        
        # Extract text
        pages_text = []
        total_words = 0
        total_chars = 0
        
        for page_num in range(start, end):
            page = doc[page_num]
            text = page.get_text()
            word_count = len(text.split())
            char_count = len(text)
            
            pages_text.append({
                "page_number": page_num + 1,
                "text": text,
                "word_count": word_count
            })
            
            total_words += word_count
            total_chars += char_count
        
        doc.close()
        
        # Store in document store
        document_store[file_path] = {
            "pages": pages_text,
            "total_pages": total_pages
        }
        
        # Format response
        result = {
            "success": True,
            "file_path": file_path,
            "pages_processed": f"{start + 1}-{end}",
            "total_pages": total_pages,
            "pages_text": pages_text,
            "total_word_count": total_words,
            "total_character_count": total_chars
        }
        
        # Create readable output
        output = f"✅ Successfully read PDF: {file_path}\n\n"
        output += f"📊 Pages processed: {start + 1}-{end} of {total_pages}\n"
        output += f"📝 Total words: {total_words}, Characters: {total_chars}\n\n"
        
        for page_data in pages_text[:3]:  # Show first 3 pages
            output += f"--- Page {page_data['page_number']} ({page_data['word_count']} words) ---\n"
            output += page_data['text'][:500] + ("..." if len(page_data['text']) > 500 else "")
            output += "\n\n"
        
        if len(pages_text) > 3:
            output += f"... and {len(pages_text) - 3} more pages\n"
        
        return output
        
    except Exception as e:
        return f"Error reading PDF: {str(e)}"


@mcp.tool()
async def extract_pdf_images(
    file_path: str,
    output_dir: Optional[str] = None,
    page_start: Optional[int] = None,
    page_end: Optional[int] = None
) -> str:
    """
    Extract all images from a PDF file.
    
    Args:
        file_path: Path to the PDF file
        output_dir: Directory to save images (optional, uses temp dir if not specified)
        page_start: Starting page number (1-indexed, optional)
        page_end: Ending page number (1-indexed, optional)
    
    Returns:
        List of extracted image paths and metadata
    """
    try:
        if not HAS_FITZ:
            return "Error: PyMuPDF library not available. Install with 'uv add pymupdf'"
        
        if not os.path.exists(file_path):
            return f"Error: File not found at {file_path}"
        
        # Set output directory
        if not output_dir:
            output_dir = tempfile.mkdtemp(prefix="pdf_images_")
        else:
            os.makedirs(output_dir, exist_ok=True)
        
        # Open PDF
        doc = fitz.open(file_path)
        total_pages = len(doc)
        
        # Set page range
        start = (page_start - 1) if page_start else 0
        end = page_end if page_end else total_pages
        start = max(0, min(start, total_pages - 1))
        end = max(start + 1, min(end, total_pages))
        
        # Extract images
        image_list = []
        image_count = 0
        
        for page_num in range(start, end):
            page = doc[page_num]
            image_infos = page.get_images()
            
            for img_index, img_info in enumerate(image_infos):
                xref = img_info[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # Save image
                image_filename = f"page_{page_num + 1}_img_{img_index + 1}.{image_ext}"
                image_path = os.path.join(output_dir, image_filename)
                
                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)
                
                image_list.append({
                    "page": page_num + 1,
                    "index": img_index + 1,
                    "path": image_path,
                    "format": image_ext,
                    "size_bytes": len(image_bytes)
                })
                image_count += 1
        
        doc.close()
        
        # Format output
        output = f"✅ Extracted {image_count} images from {file_path}\n\n"
        output += f"📂 Output directory: {output_dir}\n"
        output += f"📊 Pages processed: {start + 1}-{end} of {total_pages}\n\n"
        
        if image_list:
            output += "Images extracted:\n"
            for img in image_list[:10]:  # Show first 10
                output += f"  • Page {img['page']}, Image {img['index']}: {img['path']} ({img['size_bytes']} bytes)\n"
            
            if len(image_list) > 10:
                output += f"  ... and {len(image_list) - 10} more images\n"
        else:
            output += "No images found in the specified page range.\n"
        
        return output
        
    except Exception as e:
        return f"Error extracting images: {str(e)}"


@mcp.tool()
async def read_pdf_with_ocr(
    file_path: str,
    page_start: Optional[int] = None,
    page_end: Optional[int] = None,
    ocr_language: str = "eng"
) -> str:
    """
    Extract text from both regular text and images using OCR.
    
    Args:
        file_path: Path to the PDF file
        page_start: Starting page number (1-indexed, optional)
        page_end: Ending page number (1-indexed, optional)
        ocr_language: OCR language code (default: "eng", can use "eng+fra" for multiple)
    
    Returns:
        Combined text from PDF text and OCR from images
    """
    try:
        if not HAS_FITZ:
            return "Error: PyMuPDF library not available. Install with 'uv add pymupdf'"
        
        if not HAS_OCR:
            return "Error: OCR libraries not available. Install with 'uv add pytesseract pillow' and 'brew install tesseract'"
        
        if not os.path.exists(file_path):
            return f"Error: File not found at {file_path}"
        
        # Open PDF
        doc = fitz.open(file_path)
        total_pages = len(doc)
        
        # Set page range
        start = (page_start - 1) if page_start else 0
        end = page_end if page_end else total_pages
        start = max(0, min(start, total_pages - 1))
        end = max(start + 1, min(end, total_pages))
        
        # Process pages
        pages_data = []
        total_text_words = 0
        total_ocr_words = 0
        total_images_processed = 0
        
        for page_num in range(start, end):
            page = doc[page_num]
            
            # Extract regular text
            page_text = page.get_text()
            text_word_count = len(page_text.split())
            total_text_words += text_word_count
            
            # Extract and OCR images
            image_infos = page.get_images()
            ocr_texts = []
            images_with_text = []
            
            for img_index, img_info in enumerate(image_infos):
                try:
                    xref = img_info[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    
                    # Convert to PIL Image
                    import io
                    pil_image = Image.open(io.BytesIO(image_bytes))
                    
                    # Skip very small images (likely decorative)
                    if pil_image.width < 50 or pil_image.height < 50:
                        continue
                    
                    # Perform OCR
                    ocr_text = pytesseract.image_to_string(pil_image, lang=ocr_language)
                    
                    if ocr_text.strip():
                        ocr_texts.append(ocr_text)
                        images_with_text.append({
                            "image_index": img_index + 1,
                            "ocr_text": ocr_text.strip(),
                            "word_count": len(ocr_text.split())
                        })
                        total_images_processed += 1
                
                except Exception as e:
                    print(f"Warning: Could not OCR image {img_index + 1} on page {page_num + 1}: {e}")
                    continue
            
            # Combine text and OCR
            combined_ocr = "\n\n".join(ocr_texts)
            ocr_word_count = len(combined_ocr.split())
            total_ocr_words += ocr_word_count
            
            combined_text = page_text
            if combined_ocr:
                combined_text += f"\n\n[OCR Text from Images]\n{combined_ocr}"
            
            pages_data.append({
                "page_number": page_num + 1,
                "text": page_text,
                "ocr_text": combined_ocr,
                "images_with_text": images_with_text,
                "combined_text": combined_text,
                "text_word_count": text_word_count,
                "ocr_word_count": ocr_word_count
            })
        
        doc.close()
        
        # Store in document store
        document_store[file_path] = {
            "pages": pages_data,
            "total_pages": total_pages,
            "has_ocr": True
        }
        
        # Format output
        output = f"✅ Successfully processed PDF with OCR: {file_path}\n\n"
        output += f"📊 Pages processed: {start + 1}-{end} of {total_pages}\n"
        output += f"🔤 OCR Language: {ocr_language}\n"
        output += f"📝 Total text words: {total_text_words}\n"
        output += f"🖼️  Total OCR words: {total_ocr_words} (from {total_images_processed} images)\n"
        output += f"📄 Combined words: {total_text_words + total_ocr_words}\n\n"
        
        for page_data in pages_data[:2]:  # Show first 2 pages
            output += f"--- Page {page_data['page_number']} ---\n"
            output += f"Text: {page_data['text'][:300]}...\n"
            
            if page_data['images_with_text']:
                output += f"\nOCR from {len(page_data['images_with_text'])} images:\n"
                for img_data in page_data['images_with_text'][:2]:
                    output += f"  Image {img_data['image_index']}: {img_data['ocr_text'][:200]}...\n"
            output += "\n"
        
        if len(pages_data) > 2:
            output += f"... and {len(pages_data) - 2} more pages\n"
        
        return output
        
    except Exception as e:
        return f"Error performing OCR: {str(e)}"


@mcp.tool()
async def get_pdf_info(file_path: str) -> str:
    """
    Get comprehensive metadata and statistics about a PDF.
    
    Args:
        file_path: Path to the PDF file
    
    Returns:
        PDF metadata, page count, and document properties
    """
    try:
        if not HAS_FITZ:
            return "Error: PyMuPDF library not available. Install with 'uv add pymupdf'"
        
        if not os.path.exists(file_path):
            return f"Error: File not found at {file_path}"
        
        # Open PDF
        doc = fitz.open(file_path)
        
        # Get metadata
        metadata = doc.metadata
        total_pages = len(doc)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Count images
        total_images = 0
        for page_num in range(total_pages):
            page = doc[page_num]
            total_images += len(page.get_images())
        
        doc.close()
        
        # Format output
        output = f"📄 PDF Information: {file_path}\n\n"
        output += f"📊 File size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)\n"
        output += f"📄 Total pages: {total_pages}\n"
        output += f"🖼️  Total images: {total_images}\n\n"
        
        output += "📝 Metadata:\n"
        for key, value in metadata.items():
            if value:
                output += f"  • {key}: {value}\n"
        
        return output
        
    except Exception as e:
        return f"Error getting PDF info: {str(e)}"


@mcp.tool()
async def analyze_pdf_structure(file_path: str) -> str:
    """
    Analyze the structure and content distribution of a PDF.
    
    Args:
        file_path: Path to the PDF file
    
    Returns:
        Detailed analysis of PDF structure, page sizes, and content types
    """
    try:
        if not HAS_FITZ:
            return "Error: PyMuPDF library not available. Install with 'uv add pymupdf'"
        
        if not os.path.exists(file_path):
            return f"Error: File not found at {file_path}"
        
        # Open PDF
        doc = fitz.open(file_path)
        total_pages = len(doc)
        
        # Analyze pages
        page_analysis = []
        total_text_chars = 0
        total_images = 0
        
        for page_num in range(min(total_pages, 10)):  # Analyze first 10 pages
            page = doc[page_num]
            text = page.get_text()
            images = page.get_images()
            
            page_analysis.append({
                "page": page_num + 1,
                "width": round(page.rect.width, 2),
                "height": round(page.rect.height, 2),
                "text_length": len(text),
                "word_count": len(text.split()),
                "image_count": len(images)
            })
            
            total_text_chars += len(text)
            total_images += len(images)
        
        doc.close()
        
        # Format output
        output = f"📊 PDF Structure Analysis: {file_path}\n\n"
        output += f"📄 Total pages: {total_pages}\n"
        output += f"📝 Total text characters (first 10 pages): {total_text_chars:,}\n"
        output += f"🖼️  Total images (first 10 pages): {total_images}\n\n"
        
        output += "Page Details (first 10 pages):\n"
        for page_data in page_analysis:
            output += f"  Page {page_data['page']}: "
            output += f"{page_data['width']}x{page_data['height']}pt, "
            output += f"{page_data['word_count']} words, "
            output += f"{page_data['image_count']} images\n"
        
        if total_pages > 10:
            output += f"\n... and {total_pages - 10} more pages\n"
        
        return output
        
    except Exception as e:
        return f"Error analyzing PDF structure: {str(e)}"


@mcp.tool()
async def list_loaded_documents() -> str:
    """
    List all currently loaded PDF documents.
    
    Returns:
        List of loaded document paths and their metadata
    """
    if not document_store:
        return "No PDF documents are currently loaded."
    
    output = "📚 Loaded PDF documents:\n\n"
    for file_path, doc_data in document_store.items():
        output += f"📄 {file_path}\n"
        output += f"   • Total pages: {doc_data.get('total_pages', 'unknown')}\n"
        output += f"   • Pages loaded: {len(doc_data.get('pages', []))}\n"
        output += f"   • Has OCR: {'Yes' if doc_data.get('has_ocr') else 'No'}\n\n"
    
    return output


@mcp.tool()
async def ask_question_about_pdf(question: str, file_path: Optional[str] = None) -> str:
    """
    Ask a question about the content of a loaded PDF file.
    
    Args:
        question: The question to ask about the PDF content
        file_path: Path to specific PDF file (optional, uses all loaded PDFs if not specified)
    
    Returns:
        Answer based on PDF content using keyword search
    """
    try:
        if not document_store:
            return "Error: No PDF files have been loaded. Please use read_pdf_text or read_pdf_with_ocr first."
        
        # Get relevant text
        all_text = ""
        sources = []
        
        if file_path and file_path in document_store:
            doc_data = document_store[file_path]
            for page_data in doc_data.get('pages', []):
                text_content = page_data.get('combined_text') or page_data.get('text', '')
                all_text += f"\n[Page {page_data.get('page_number')}]\n{text_content}\n"
            sources.append(file_path)
        else:
            # Use all loaded documents
            for fp, doc_data in document_store.items():
                for page_data in doc_data.get('pages', []):
                    text_content = page_data.get('combined_text') or page_data.get('text', '')
                    all_text += f"\n[{fp} - Page {page_data.get('page_number')}]\n{text_content}\n"
                sources.append(fp)
        
        if not all_text.strip():
            return "Error: No text content found in the loaded PDF(s)."
        
        # Simple keyword-based search
        question_lower = question.lower()
        sentences = all_text.split('.')
        relevant_sentences = []
        
        # Extract question keywords (words longer than 3 characters)
        question_words = [word for word in question_lower.split() if len(word) > 3]
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            # Count matching keywords
            matches = sum(1 for word in question_words if word in sentence_lower)
            
            if matches > 0:
                relevant_sentences.append((sentence.strip(), matches))
        
        # Sort by relevance (number of matches)
        relevant_sentences.sort(key=lambda x: x[1], reverse=True)
        
        if relevant_sentences:
            output = f"🔍 Answer based on {len(sources)} document(s):\n\n"
            output += f"Question: {question}\n\n"
            output += "Relevant excerpts:\n\n"
            
            for sentence, matches in relevant_sentences[:5]:
                if sentence:
                    output += f"• {sentence}\n\n"
            
            output += f"\n📚 Sources: {', '.join(sources)}"
            return output
        else:
            return f"❌ Could not find relevant information about '{question}' in the loaded PDF(s).\n\nTry:\n• Loading more content from the PDF\n• Using different keywords\n• Reading with OCR if the content is in images"
            
    except Exception as e:
        return f"Error answering question: {str(e)}"


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
