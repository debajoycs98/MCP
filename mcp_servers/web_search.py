#!/usr/bin/env python3
"""
MCP Server for Web Search
Allows AI assistants to search the internet for real-time information
Uses WebSearch-MCP crawler service from https://mcpservers.org/servers/mnhlt/WebSearch-MCP
"""

import asyncio
import os
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
import requests
import json

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

# WebSearch Crawler API configuration
CRAWLER_API_URL = os.getenv("WEBSEARCH_API_URL", "http://localhost:3001")

def check_crawler_health() -> bool:
    """Check if the WebSearch crawler API is available."""
    try:
        response = requests.get(f"{CRAWLER_API_URL}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False

async def _search_with_duckduckgo(query: str, num_results: int = 5) -> str:
    """
    Fallback search using DuckDuckGo Instant Answer API (no API key needed).
    """
    try:
        from urllib.parse import quote_plus
        
        # Try DuckDuckGo Instant Answer API first
        api_url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&no_html=1"
        
        response = requests.get(api_url, timeout=10)
        data = response.json()
        
        results = []
        
        # Get abstract/summary
        if data.get('Abstract'):
            results.append({
                'title': data.get('Heading', 'Summary'),
                'snippet': data.get('Abstract', ''),
                'url': data.get('AbstractURL', '')
            })
        
        # Get related topics
        for topic in data.get('RelatedTopics', [])[:num_results-1]:
            if isinstance(topic, dict) and topic.get('Text'):
                results.append({
                    'title': topic.get('Text', '').split(' - ')[0][:100],
                    'snippet': topic.get('Text', '')[:200],
                    'url': topic.get('FirstURL', '')
                })
        
        if results:
            result_text = f"🔍 Search results for '{query}' ({len(results)} found):\n\n"
            for i, result in enumerate(results, 1):
                result_text += f"{i}. {result['title']}\n"
                result_text += f"   📝 {result['snippet']}\n"
                if result['url']:
                    result_text += f"   🔗 {result['url']}\n"
                result_text += "\n"
            return result_text
        
        # If no results from API, provide a helpful response
        return (
            f"🔍 Search: '{query}'\n\n"
            f"💡 I can help you search for this information. Here are some suggestions:\n\n"
            f"1. Try searching on:\n"
            f"   • Google: https://www.google.com/search?q={quote_plus(query)}\n"
            f"   • DuckDuckGo: https://duckduckgo.com/?q={quote_plus(query)}\n\n"
            f"2. For better results, try:\n"
            f"   • Be more specific with your query\n"
            f"   • Use keywords instead of full sentences\n"
            f"   • Add context (e.g., 'Python tutorial 2025' instead of 'Python')\n\n"
            f"💡 Tip: Start Docker Desktop and run './start_websearch.sh' for\n"
            f"   more comprehensive web search results!"
        )
            
    except ImportError:
        return (
            f"📝 Search query: '{query}'\n\n"
            f"⚠️  Basic web search is available, but for best results:\n"
            f"• Install with: uv add beautifulsoup4\n"
            f"• Or start Docker: ./start_websearch.sh"
        )
    except Exception as e:
        return (
            f"🔍 Search: '{query}'\n\n"
            f"⚠️  Unable to fetch live results at the moment.\n\n"
            f"You can search manually at:\n"
            f"• https://www.google.com/search?q={quote_plus(query)}\n"
            f"• https://duckduckgo.com/?q={quote_plus(query)}\n\n"
            f"Error: {str(e)}"
        )

@mcp.tool()
async def search_web(
    query: str, 
    num_results: int = 5,
    language: str = "en",
    region: str = "us",
    result_type: str = "all"
) -> str:
    """
    Search the web for real-time information.
    
    Tries WebSearch-MCP crawler first (if Docker is running),
    then falls back to DuckDuckGo HTML search.
    
    Args:
        query: Search query string
        num_results: Number of results to return (default: 5)
        language: Language code for search results (default: "en")
        region: Region code for search results (default: "us")
        result_type: Type of results - 'all', 'news', or 'blogs' (default: "all")
    
    Returns:
        Search results with titles, URLs, snippets, and metadata
    """
    # Try WebSearch-MCP crawler first (if available)
    try:
        payload = {
            "query": query,
            "numResults": num_results,
            "language": language,
            "filters": {
                "resultType": result_type
            }
        }
        
        response = requests.post(
            f"{CRAWLER_API_URL}/crawl",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=5  # Short timeout for quick fallback
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            if results:
                result_text = f"🔍 Search results for '{query}' ({len(results)} found):\n\n"
                
                for i, result in enumerate(results, 1):
                    title = result.get("title", "No title")
                    snippet = result.get("snippet", "No description available")
                    url = result.get("url", "")
                    site_name = result.get("siteName", "")
                    byline = result.get("byline", "")
                    
                    result_text += f"{i}. {title}\n"
                    if site_name:
                        result_text += f"   📰 Source: {site_name}\n"
                    if byline:
                        result_text += f"   ✍️  By: {byline}\n"
                    result_text += f"   📝 {snippet}\n"
                    result_text += f"   🔗 {url}\n\n"
                
                return result_text
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        # WebSearch-MCP not available, fall back to DuckDuckGo
        pass
    except Exception:
        # Any other error with WebSearch-MCP, fall back
        pass
    
    # Fallback to DuckDuckGo search
    return await _search_with_duckduckgo(query, num_results)

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
        # Use the news filter for better results
        return await search_web(topic, num_articles, result_type="news")
        
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
