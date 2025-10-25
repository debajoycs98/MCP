#!/usr/bin/env python3
"""
MCP Server for PDF Reading and Q&A
Allows AI assistants to read PDF files and answer questions about their content
"""

import asyncio
import os
from typing import List, Optional
from pathlib import Path
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import PDF processing libraries
try:
    import pypdf
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False
    print("Warning: pypdf not available. PDF reading will be limited.")

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.embeddings import HuggingFaceEmbeddings
    from langchain.vectorstores import FAISS
    from langchain.chains import RetrievalQA
    from langchain.llms import OpenAI
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False
    print("Warning: LangChain not available. Using simple text processing.")

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

# Initialize text splitter if available
if HAS_LANGCHAIN:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
else:
    text_splitter = None

@mcp.tool()
async def read_pdf(file_path: str) -> str:
    """
    Read and extract text from a PDF file.
    
    Args:
        file_path: Path to the PDF file
    
    Returns:
        Extracted text content from the PDF
    """
    try:
        if not HAS_PYPDF:
            return "Error: pypdf library not available. Please install it with 'uv add pypdf'"
        
        if not os.path.exists(file_path):
            return f"Error: File not found at {file_path}"
        
        # Read PDF file
        with open(file_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            text = ""
            
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                text += f"\n--- Page {page_num + 1} ---\n"
                text += page_text
            
            # Store the document for Q&A
            document_store[file_path] = text
            
            return f"Successfully read PDF: {file_path}\n\nExtracted text:\n{text[:1000]}{'...' if len(text) > 1000 else ''}"
            
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

@mcp.tool()
async def read_multiple_pdfs(file_paths: List[str]) -> str:
    """
    Read and extract text from multiple PDF files.
    
    Args:
        file_paths: List of paths to PDF files
    
    Returns:
        Combined extracted text from all PDFs
    """
    try:
        if not HAS_PYPDF:
            return "Error: pypdf library not available. Please install it with 'uv add pypdf'"
        
        combined_text = ""
        successful_files = []
        
        for file_path in file_paths:
            if not os.path.exists(file_path):
                combined_text += f"\nError: File not found at {file_path}\n"
                continue
            
            with open(file_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                file_text = f"\n=== {file_path} ===\n"
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    file_text += f"\n--- Page {page_num + 1} ---\n"
                    file_text += page_text
                
                combined_text += file_text
                document_store[file_path] = file_text
                successful_files.append(file_path)
        
        return f"Successfully read {len(successful_files)} PDF files:\n{', '.join(successful_files)}\n\nCombined text:\n{combined_text[:2000]}{'...' if len(combined_text) > 2000 else ''}"
        
    except Exception as e:
        return f"Error reading PDFs: {str(e)}"

@mcp.tool()
async def ask_question_about_pdf(question: str, file_path: Optional[str] = None) -> str:
    """
    Ask a question about the content of a PDF file.
    
    Args:
        question: The question to ask about the PDF content
        file_path: Path to specific PDF file (optional, uses all loaded PDFs if not specified)
    
    Returns:
        Answer to the question based on PDF content
    """
    try:
        if not document_store:
            return "Error: No PDF files have been loaded. Please use read_pdf or read_multiple_pdfs first."
        
        # Get relevant text
        if file_path and file_path in document_store:
            text = document_store[file_path]
        else:
            # Use all loaded documents
            text = "\n\n".join(document_store.values())
        
        if not text.strip():
            return "Error: No text content found in the PDF(s)."
        
        # Simple keyword-based search for now
        # In a production system, you'd use embeddings and vector search
        question_lower = question.lower()
        text_lower = text.lower()
        
        # Find sentences that contain keywords from the question
        sentences = text.split('.')
        relevant_sentences = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            # Check if sentence contains any words from the question
            question_words = [word for word in question_lower.split() if len(word) > 3]
            if any(word in sentence_lower for word in question_words):
                relevant_sentences.append(sentence.strip())
        
        if relevant_sentences:
            answer = f"Based on the PDF content, here's what I found:\n\n"
            answer += "\n".join(relevant_sentences[:5])  # Limit to 5 most relevant sentences
            return answer
        else:
            return f"I couldn't find specific information about '{question}' in the PDF content. The document contains {len(text)} characters of text."
            
    except Exception as e:
        return f"Error processing question: {str(e)}"

@mcp.tool()
async def list_loaded_documents() -> str:
    """
    List all currently loaded PDF documents.
    
    Returns:
        List of loaded document paths and their sizes
    """
    if not document_store:
        return "No PDF documents are currently loaded."
    
    result = "Loaded PDF documents:\n"
    for file_path, content in document_store.items():
        result += f"- {file_path} ({len(content)} characters)\n"
    
    return result

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
