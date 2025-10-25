#!/usr/bin/env python3
"""
Test AI assistant's ability to schedule meetings
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_chat_assistant import AIPersonalAssistant

async def test_meeting_scheduling():
    print("=" * 70)
    print("🤖 Testing AI Assistant with Meeting Scheduling")
    print("=" * 70)
    print()
    
    assistant = AIPersonalAssistant()
    
    # Test 1: Schedule a meeting
    print("Test 1: Asking AI to schedule a meeting")
    print("-" * 70)
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%A")
    user_message = f"Schedule a meeting with debajoymukherjeecs@gmail.com {tomorrow} at 3pm called 'AI Test Meeting' for 45 minutes"
    print(f"User: {user_message}")
    print()
    
    response = await assistant.process_with_claude(user_message)
    print(f"Assistant: {response}")
    print()
    print("=" * 70)
    print()
    
    # Test 2: List meetings
    print("Test 2: Asking AI to list meetings")
    print("-" * 70)
    user_message2 = "What meetings do I have coming up?"
    print(f"User: {user_message2}")
    print()
    
    response2 = await assistant.process_with_claude(user_message2)
    print(f"Assistant: {response2}")
    print()
    print("=" * 70)
    print()
    
    print("✅ Test Complete!")
    print()
    print("Check your Google Calendar to see the new meeting!")
    print("https://calendar.google.com")

if __name__ == "__main__":
    asyncio.run(test_meeting_scheduling())

