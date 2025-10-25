#!/bin/bash
# Personal AI Assistant Launcher Script

echo "🤖 Personal AI Assistant"
echo "========================"
echo "Starting your personal AI assistant..."
echo ""

# Check if uv is available
if command -v uv &> /dev/null; then
    echo "Using uv to run the assistant..."
    uv run python chat_assistant.py
else
    echo "Using python to run the assistant..."
    python3 chat_assistant.py
fi
