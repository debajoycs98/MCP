#!/bin/bash

echo "🚀 Starting WebSearch Crawler Service..."
echo ""
echo "This will start:"
echo "  • WebSearch Crawler API on http://localhost:3001"
echo "  • FlareSolverr (for bypassing Cloudflare)"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Start the services
docker-compose up -d

echo ""
echo "⏳ Waiting for services to start (this may take 30-60 seconds)..."
sleep 10

# Check if the services are up
if docker ps | grep -q websearch-api; then
    echo "✅ WebSearch Crawler API is running"
else
    echo "❌ WebSearch Crawler API failed to start"
    echo "Check logs with: docker-compose logs crawler"
    exit 1
fi

if docker ps | grep -q flaresolverr; then
    echo "✅ FlareSolverr is running"
else
    echo "❌ FlareSolverr failed to start"
    echo "Check logs with: docker-compose logs flaresolverr"
    exit 1
fi

echo ""
echo "🎉 All services are running!"
echo ""
echo "📋 Useful commands:"
echo "  • Check status: docker-compose ps"
echo "  • View logs: docker-compose logs -f"
echo "  • Stop services: docker-compose down"
echo "  • Test API: curl http://localhost:3001/health"
echo ""
