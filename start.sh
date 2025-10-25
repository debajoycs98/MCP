#!/bin/bash
# AI-Powered Personal Assistant Launcher Script

echo "🤖 AI-Powered Personal Assistant"
echo "================================="
echo "Starting your intelligent personal assistant..."
echo "Powered by Claude Sonnet 4"
echo ""

# Check if uv is available
if command -v uv &> /dev/null; then
    echo "Using uv to run the assistant..."
    uv run python ai_chat_assistant.py
else
    echo "Using python to run the assistant..."
    python3 ai_chat_assistant.py
fi
