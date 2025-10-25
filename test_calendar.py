#!/usr/bin/env python3
"""
Quick test to schedule a meeting in Google Calendar
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp_servers.meeting_scheduler import schedule_meeting, list_meetings

async def main():
    print("=" * 70)
    print("📅 Testing Google Calendar Integration")
    print("=" * 70)
    print()
    
    # Calculate tomorrow's date and time
    tomorrow = datetime.now() + timedelta(days=1)
    date_str = tomorrow.strftime("%Y-%m-%d")
    time_str = "14:00"  # 2 PM
    
    print("🔄 Scheduling a test meeting...")
    print(f"   Date: {date_str}")
    print(f"   Time: {time_str}")
    print(f"   Attendee: debajoymukherjeecs@gmail.com")
    print()
    
    # Schedule the meeting
    result = await schedule_meeting(
        title="MCP Test Meeting",
        date=date_str,
        time=time_str,
        duration_minutes=30,
        attendees=["debajoymukherjeecs@gmail.com"],
        location="Virtual",
        description="This is a test meeting created by your MCP Personal Assistant!"
    )
    
    print(result)
    print()
    print("=" * 70)
    
    # List upcoming meetings
    print()
    print("📋 Checking your upcoming meetings...")
    print()
    
    meetings_result = await list_meetings(max_results=5)
    print(meetings_result)
    
    print()
    print("=" * 70)
    print("✅ Test Complete!")
    print()
    print("Check your Google Calendar at: https://calendar.google.com")
    print("You should see 'MCP Test Meeting' scheduled for tomorrow at 2 PM!")
    print()

if __name__ == "__main__":
    asyncio.run(main())

