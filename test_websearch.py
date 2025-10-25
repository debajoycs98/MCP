#!/usr/bin/env python3
"""
Test script for WebSearch MCP server
"""

import asyncio
import sys
sys.path.append('mcp_servers')

from web_search import search_web, get_news, get_weather

async def main():
    print("🔍 Testing WebSearch MCP Server\n")
    print("=" * 60)
    
    # Test 1: Basic web search
    print("\n1️⃣  Testing basic web search...")
    print("-" * 60)
    result = await search_web("Python programming best practices", num_results=3)
    print(result)
    
    # Test 2: News search
    print("\n2️⃣  Testing news search...")
    print("-" * 60)
    result = await get_news("artificial intelligence", num_articles=2)
    print(result)
    
    # Test 3: Weather search
    print("\n3️⃣  Testing weather search...")
    print("-" * 60)
    result = await get_weather("San Francisco")
    print(result)
    
    print("\n" + "=" * 60)
    print("✅ WebSearch MCP Server tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
