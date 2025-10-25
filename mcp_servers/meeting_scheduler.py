#!/usr/bin/env python3
"""
MCP Server for Meeting Scheduling
Allows AI assistants to schedule meetings and manage calendar events
"""

import asyncio
import os
from typing import List, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv
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
mcp = FastMCP("Meeting Scheduler")

# Simple in-memory storage for meetings (in production, use a database)
meetings_db = []

@mcp.tool()
async def schedule_meeting(
    title: str,
    date: str,
    time: str,
    duration_minutes: int = 60,
    attendees: Optional[List[str]] = None,
    location: Optional[str] = None,
    description: Optional[str] = None
) -> str:
    """
    Schedule a new meeting.
    
    Args:
        title: Meeting title
        date: Meeting date (YYYY-MM-DD format)
        time: Meeting time (HH:MM format)
        duration_minutes: Meeting duration in minutes (default: 60)
        attendees: List of attendee email addresses (optional)
        location: Meeting location (optional)
        description: Meeting description (optional)
    
    Returns:
        Confirmation message with meeting details
    """
    try:
        # Parse date and time
        meeting_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        end_time = meeting_datetime + timedelta(minutes=duration_minutes)
        
        # Check for conflicts
        for meeting in meetings_db:
            existing_start = datetime.strptime(f"{meeting['date']} {meeting['time']}", "%Y-%m-%d %H:%M")
            existing_end = existing_start + timedelta(minutes=meeting['duration_minutes'])
            
            if (meeting_datetime < existing_end and end_time > existing_start):
                return f"Conflict detected! Meeting '{meeting['title']}' is already scheduled at {meeting['date']} {meeting['time']}"
        
        # Create meeting object
        meeting = {
            'id': len(meetings_db) + 1,
            'title': title,
            'date': date,
            'time': time,
            'duration_minutes': duration_minutes,
            'attendees': attendees or [],
            'location': location,
            'description': description,
            'created_at': datetime.now().isoformat()
        }
        
        meetings_db.append(meeting)
        
        # Create confirmation message
        confirmation = f"Meeting scheduled successfully!\n\n"
        confirmation += f"Title: {title}\n"
        confirmation += f"Date: {date}\n"
        confirmation += f"Time: {time}\n"
        confirmation += f"Duration: {duration_minutes} minutes\n"
        confirmation += f"End Time: {end_time.strftime('%H:%M')}\n"
        
        if attendees:
            confirmation += f"Attendees: {', '.join(attendees)}\n"
        if location:
            confirmation += f"Location: {location}\n"
        if description:
            confirmation += f"Description: {description}\n"
        
        return confirmation
        
    except ValueError as e:
        return f"Error parsing date/time: {str(e)}. Please use YYYY-MM-DD format for date and HH:MM format for time."
    except Exception as e:
        return f"Error scheduling meeting: {str(e)}"

@mcp.tool()
async def list_meetings(date: Optional[str] = None) -> str:
    """
    List scheduled meetings.
    
    Args:
        date: Filter by specific date (YYYY-MM-DD format, optional)
    
    Returns:
        List of scheduled meetings
    """
    try:
        if not meetings_db:
            return "No meetings scheduled."
        
        filtered_meetings = meetings_db
        if date:
            filtered_meetings = [m for m in meetings_db if m['date'] == date]
        
        if not filtered_meetings:
            return f"No meetings scheduled for {date if date else 'any date'}."
        
        result = f"Found {len(filtered_meetings)} meeting(s):\n\n"
        
        for meeting in sorted(filtered_meetings, key=lambda x: (x['date'], x['time'])):
            result += f"ID: {meeting['id']}\n"
            result += f"Title: {meeting['title']}\n"
            result += f"Date: {meeting['date']}\n"
            result += f"Time: {meeting['time']}\n"
            result += f"Duration: {meeting['duration_minutes']} minutes\n"
            
            if meeting['attendees']:
                result += f"Attendees: {', '.join(meeting['attendees'])}\n"
            if meeting['location']:
                result += f"Location: {meeting['location']}\n"
            if meeting['description']:
                result += f"Description: {meeting['description']}\n"
            
            result += "\n"
        
        return result
        
    except Exception as e:
        return f"Error listing meetings: {str(e)}"

@mcp.tool()
async def cancel_meeting(meeting_id: int) -> str:
    """
    Cancel a scheduled meeting.
    
    Args:
        meeting_id: ID of the meeting to cancel
    
    Returns:
        Confirmation message
    """
    try:
        meeting_found = False
        for i, meeting in enumerate(meetings_db):
            if meeting['id'] == meeting_id:
                cancelled_meeting = meetings_db.pop(i)
                meeting_found = True
                break
        
        if meeting_found:
            return f"Meeting '{cancelled_meeting['title']}' scheduled for {cancelled_meeting['date']} {cancelled_meeting['time']} has been cancelled."
        else:
            return f"Meeting with ID {meeting_id} not found."
            
    except Exception as e:
        return f"Error cancelling meeting: {str(e)}"

@mcp.tool()
async def check_availability(date: str, time: str, duration_minutes: int = 60) -> str:
    """
    Check if a time slot is available for scheduling.
    
    Args:
        date: Date to check (YYYY-MM-DD format)
        time: Time to check (HH:MM format)
        duration_minutes: Duration to check (default: 60 minutes)
    
    Returns:
        Availability status
    """
    try:
        check_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        end_time = check_datetime + timedelta(minutes=duration_minutes)
        
        for meeting in meetings_db:
            if meeting['date'] == date:
                existing_start = datetime.strptime(f"{meeting['date']} {meeting['time']}", "%Y-%m-%d %H:%M")
                existing_end = existing_start + timedelta(minutes=meeting['duration_minutes'])
                
                if (check_datetime < existing_end and end_time > existing_start):
                    return f"Time slot is NOT available. Conflicts with meeting '{meeting['title']}' at {meeting['time']}"
        
        return f"Time slot is available on {date} at {time} for {duration_minutes} minutes."
        
    except ValueError as e:
        return f"Error parsing date/time: {str(e)}. Please use YYYY-MM-DD format for date and HH:MM format for time."
    except Exception as e:
        return f"Error checking availability: {str(e)}"

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
