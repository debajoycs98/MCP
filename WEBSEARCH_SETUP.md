# WebSearch MCP Setup Guide

This project uses the [WebSearch-MCP](https://mcpservers.org/servers/mnhlt/WebSearch-MCP) crawler service for real-time web searching with advanced features like Cloudflare bypass.

## Architecture

```
┌─────────────────┐
│   AI Assistant  │
│ (ai_chat_       │
│  assistant.py)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  web_search.py  │  (Python MCP Server)
│   (FastMCP)     │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│ WebSearch API   │  (Docker Container)
│  Port: 3001     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FlareSolverr   │  (Cloudflare Bypass)
│  Port: 8191     │
└─────────────────┘
```

## Prerequisites

- **Docker Desktop** installed and running
- Python 3.11+
- `uv` package manager

## Setup Instructions

### Step 1: Start the WebSearch Crawler Service

```bash
# Make sure Docker Desktop is running first!

# Start the services
./start_websearch.sh

# Or manually:
docker-compose up -d
```

This will start two Docker containers:
- `websearch-api`: The crawler service (port 3001)
- `flaresolverr`: Cloudflare bypass service (port 8191)

### Step 2: Verify the Service

```bash
# Check if services are running
docker-compose ps

# Test the API health endpoint
curl http://localhost:3001/health
```

Expected response:
```json
{
  "status": "ok",
  "details": {
    "status": "ok",
    "flaresolverr": true,
    "google": true,
    "message": null
  }
}
```

### Step 3: Test the Python MCP Server

```bash
# Run the test script
uv run python test_websearch.py
```

### Step 4: Use in AI Chat Assistant

The web search is automatically available in your AI assistant! Try:

```bash
uv run python ai_chat_assistant.py
```

Then ask:
- "Search the web for latest AI developments"
- "What's the news about climate change?"
- "Search for Python tutorials"

## Features

### 🔍 Advanced Web Search
- Real-time web crawling
- Bypasses Cloudflare protection
- Rich metadata (titles, snippets, URLs, bylines)
- Language and region filtering

### 📰 News Search
- Dedicated news results
- Recent articles
- Author information

### 🌐 Multiple Result Types
- `all` - General web results
- `news` - News articles
- `blogs` - Blog posts

## Available MCP Tools

### `search_web(query, num_results, language, region, result_type)`
Search the web for real-time information.

**Parameters:**
- `query` (str): Search query
- `num_results` (int): Number of results (default: 5)
- `language` (str): Language code, e.g., "en" (default: "en")
- `region` (str): Region code, e.g., "us" (default: "us")
- `result_type` (str): "all", "news", or "blogs" (default: "all")

### `get_news(topic, num_articles)`
Get recent news articles about a topic.

**Parameters:**
- `topic` (str): News topic (default: "technology")
- `num_articles` (int): Number of articles (default: 3)

### `get_weather(location)`
Get current weather information.

**Parameters:**
- `location` (str): City name or location

### `get_stock_price(symbol)`
Get current stock price.

**Parameters:**
- `symbol` (str): Stock symbol (e.g., AAPL, GOOGL)

## Configuration

Edit `.env` file:

```bash
# WebSearch Crawler API
WEBSEARCH_API_URL=http://localhost:3001
```

## Troubleshooting

### Service Not Starting

```bash
# Check if Docker is running
docker info

# View logs
docker-compose logs -f crawler
docker-compose logs -f flaresolverr

# Restart services
docker-compose restart
```

### Connection Refused Error

1. Make sure Docker Desktop is running
2. Wait 30-60 seconds after starting services
3. Check if port 3001 is available:
   ```bash
   lsof -i :3001
   ```

### Search Not Working

```bash
# Test the API directly
curl -X POST http://localhost:3001/crawl \
  -H "Content-Type: application/json" \
  -d '{
    "query": "test search",
    "numResults": 2
  }'
```

### Stop Services

```bash
# Stop and remove containers
docker-compose down

# Stop and remove everything including volumes
docker-compose down -v
```

## Docker Management Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View status
docker-compose ps

# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f crawler
docker-compose logs -f flaresolverr

# Restart a service
docker-compose restart crawler

# Rebuild and start
docker-compose up -d --build
```

## Performance Notes

- First search may take 10-20 seconds (containers warming up)
- Subsequent searches are faster (2-5 seconds)
- FlareSolverr adds ~2-3 seconds for Cloudflare-protected sites
- The service uses caching for better performance

## Credits

This implementation uses the [WebSearch-MCP](https://mcpservers.org/servers/mnhlt/WebSearch-MCP) crawler service by [@mnhlt](https://github.com/mnhlt).

## Related Resources

- [WebSearch-MCP on mcpservers.org](https://mcpservers.org/servers/mnhlt/WebSearch-MCP)
- [FlareSolverr Documentation](https://github.com/FlareSolverr/FlareSolverr)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
