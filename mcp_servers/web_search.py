#!/usr/bin/env python3
"""
MCP Server for Web Search
Allows AI assistants to search the internet for real-time information
"""

import asyncio
import os
from typing import List, Optional
from dotenv import load_dotenv
import requests
from urllib.parse import quote_plus

# Load environment variables
load_dotenv()

# Import FastMCP
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    from mcp.server import Server
    from mcp.types import Tool, TextContent

# Initialize MCP server
mcp = FastMCP("Web Search")

@mcp.tool()
async def search_web(query: str, num_results: int = 5) -> str:
    """
    Search the web for real-time information.
    
    Args:
        query: Search query string
        num_results: Number of results to return (default: 5)
    
    Returns:
        Search results with titles, URLs, and snippets
    """
    try:
        # Use DuckDuckGo for search (no API key required)
        search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Simple text extraction (in production, use proper HTML parsing)
        content = response.text
        
        # Extract basic information
        results = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if 'result__title' in line and i < len(lines) - 1:
                # Extract title and URL
                title_line = lines[i + 1] if i + 1 < len(lines) else ""
                snippet_line = lines[i + 2] if i + 2 < len(lines) else ""
                
                if len(results) < num_results:
                    results.append({
                        'title': title_line.strip()[:100],
                        'snippet': snippet_line.strip()[:200],
                        'url': 'https://duckduckgo.com'  # Simplified for demo
                    })
        
        if results:
            result_text = f"Search results for '{query}':\n\n"
            for i, result in enumerate(results, 1):
                result_text += f"{i}. {result['title']}\n"
                result_text += f"   {result['snippet']}\n"
                result_text += f"   URL: {result['url']}\n\n"
            
            return result_text
        else:
            return f"No results found for '{query}'. Try a different search term."
            
    except Exception as e:
        return f"Error searching the web: {str(e)}"

@mcp.tool()
async def get_news(topic: str = "technology", num_articles: int = 3) -> str:
    """
    Get recent news articles about a specific topic.
    
    Args:
        topic: News topic to search for (default: "technology")
        num_articles: Number of articles to return (default: 3)
    
    Returns:
        Recent news articles about the topic
    """
    try:
        # Use a simple news search
        query = f"{topic} news"
        return await search_web(query, num_articles)
        
    except Exception as e:
        return f"Error getting news: {str(e)}"

@mcp.tool()
async def get_weather(location: str) -> str:
    """
    Get current weather information for a location.
    
    Args:
        location: City name or location
    
    Returns:
        Current weather information
    """
    try:
        query = f"weather {location}"
        return await search_web(query, 3)
        
    except Exception as e:
        return f"Error getting weather: {str(e)}"

@mcp.tool()
async def get_stock_price(symbol: str) -> str:
    """
    Get current stock price for a given symbol.
    
    Args:
        symbol: Stock symbol (e.g., AAPL, GOOGL)
    
    Returns:
        Current stock price information
    """
    try:
        query = f"{symbol} stock price"
        return await search_web(query, 3)
        
    except Exception as e:
        return f"Error getting stock price: {str(e)}"

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
