#!/usr/bin/env python3
"""
MCP Server for Meeting Scheduling with Google Calendar API
Allows AI assistants to schedule meetings and manage real calendar events
"""

import asyncio
import os
from typing import List, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Google Calendar API imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    HAS_GOOGLE_API = True
except ImportError:
    HAS_GOOGLE_API = False
    print("Warning: Google Calendar API not available. Install with 'uv add google-api-python-client google-auth-httplib2 google-auth-oauthlib'")

# Import FastMCP
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    from mcp.server import Server
    from mcp.types import Tool, TextContent

# Initialize MCP server
mcp = FastMCP("Meeting Scheduler")

# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """Get authenticated Google Calendar service"""
    if not HAS_GOOGLE_API:
        return None
    
    creds = None
    token_path = 'token.json'
    credentials_path = 'credentials.json'
    
    # Check if token.json exists
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # If there are no (valid) credentials available
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save the refreshed token
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        else:
            # Need to authenticate
            return None
    
    try:
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"Error creating calendar service: {e}")
        return None

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
    Schedule a new meeting in Google Calendar.
    
    Args:
        title: Meeting title
        date: Meeting date (YYYY-MM-DD format)
        time: Meeting time (HH:MM format, 24-hour)
        duration_minutes: Meeting duration in minutes (default: 60)
        attendees: List of attendee email addresses (optional)
        location: Meeting location (optional)
        description: Meeting description (optional)
    
    Returns:
        Success message with meeting details or error message
    """
    try:
        service = get_calendar_service()
        if not service:
            return "❌ Error: Google Calendar not authenticated. Run 'uv run python authenticate_google.py' first."
        
        # Parse date and time
        try:
            start_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            end_datetime = start_datetime + timedelta(minutes=duration_minutes)
        except ValueError as e:
            return f"❌ Error: Invalid date/time format. Use YYYY-MM-DD for date and HH:MM for time. Error: {e}"
        
        # Create event
        event = {
            'summary': title,
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'America/Chicago',  # You can make this configurable
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'America/Chicago',
            },
        }
        
        if location:
            event['location'] = location
        
        if description:
            event['description'] = description
        
        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]
        
        # Insert the event
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        
        result = f"✅ Meeting scheduled successfully!\n\n"
        result += f"📅 Title: {title}\n"
        result += f"🕐 When: {start_datetime.strftime('%A, %B %d, %Y at %I:%M %p')}\n"
        result += f"⏱️  Duration: {duration_minutes} minutes\n"
        if location:
            result += f"📍 Location: {location}\n"
        if attendees:
            result += f"👥 Attendees: {', '.join(attendees)}\n"
        result += f"\n🔗 Calendar link: {created_event.get('htmlLink', 'N/A')}"
        
        return result
        
    except HttpError as error:
        return f"❌ Google Calendar API error: {error}"
    except Exception as e:
        return f"❌ Error scheduling meeting: {str(e)}"

@mcp.tool()
async def list_meetings(
    date: Optional[str] = None,
    max_results: int = 10
) -> str:
    """
    List meetings from Google Calendar.
    
    Args:
        date: Optional date to filter meetings (YYYY-MM-DD format). If not provided, shows upcoming meetings.
        max_results: Maximum number of meetings to return (default: 10)
    
    Returns:
        List of meetings with details
    """
    try:
        service = get_calendar_service()
        if not service:
            return "❌ Error: Google Calendar not authenticated. Run 'uv run python authenticate_google.py' first."
        
        # Determine time range
        if date:
            try:
                start_date = datetime.strptime(date, "%Y-%m-%d")
                time_min = start_date.replace(hour=0, minute=0, second=0).isoformat() + 'Z'
                time_max = start_date.replace(hour=23, minute=59, second=59).isoformat() + 'Z'
            except ValueError:
                return f"❌ Error: Invalid date format. Use YYYY-MM-DD."
        else:
            # Get upcoming meetings
            time_min = datetime.utcnow().isoformat() + 'Z'
            time_max = None
        
        # Fetch events
        if time_max:
            events_result = service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
        else:
            events_result = service.events().list(
                calendarId='primary',
                timeMin=time_min,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            if date:
                return f"📭 No meetings found on {date}"
            else:
                return "📭 No upcoming meetings found"
        
        result = f"📅 Found {len(events)} meeting(s):\n\n"
        
        for i, event in enumerate(events, 1):
            start = event['start'].get('dateTime', event['start'].get('date'))
            
            # Parse the start time
            if 'T' in start:
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                time_str = start_dt.strftime('%A, %B %d, %Y at %I:%M %p')
            else:
                time_str = start
            
            result += f"{i}. {event.get('summary', 'Untitled')}\n"
            result += f"   🕐 {time_str}\n"
            
            if event.get('location'):
                result += f"   📍 {event['location']}\n"
            
            if event.get('attendees'):
                attendee_emails = [a['email'] for a in event['attendees']]
                result += f"   👥 {', '.join(attendee_emails)}\n"
            
            result += f"   🆔 ID: {event['id']}\n"
            result += "\n"
        
        return result
        
    except HttpError as error:
        return f"❌ Google Calendar API error: {error}"
    except Exception as e:
        return f"❌ Error listing meetings: {str(e)}"

@mcp.tool()
async def cancel_meeting(event_id: str) -> str:
    """
    Cancel a meeting in Google Calendar.
    
    Args:
        event_id: The Google Calendar event ID
    
    Returns:
        Success message or error
    """
    try:
        service = get_calendar_service()
        if not service:
            return "❌ Error: Google Calendar not authenticated. Run 'uv run python authenticate_google.py' first."
        
        # Delete the event
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        
        return f"✅ Meeting cancelled successfully (ID: {event_id})"
        
    except HttpError as error:
        if error.resp.status == 404:
            return f"❌ Error: Meeting not found (ID: {event_id})"
        return f"❌ Google Calendar API error: {error}"
    except Exception as e:
        return f"❌ Error cancelling meeting: {str(e)}"

@mcp.tool()
async def check_availability(
    date: str,
    start_time: str,
    end_time: Optional[str] = None,
    duration_minutes: int = 60
) -> str:
    """
    Check if a time slot is available in Google Calendar.
    
    Args:
        date: Date to check (YYYY-MM-DD format)
        start_time: Start time (HH:MM format)
        end_time: End time (HH:MM format, optional). If not provided, uses duration_minutes.
        duration_minutes: Duration in minutes if end_time not provided (default: 60)
    
    Returns:
        Availability status with any conflicts
    """
    try:
        service = get_calendar_service()
        if not service:
            return "❌ Error: Google Calendar not authenticated. Run 'uv run python authenticate_google.py' first."
        
        # Parse date and time
        try:
            start_datetime = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
            
            if end_time:
                end_datetime = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")
            else:
                end_datetime = start_datetime + timedelta(minutes=duration_minutes)
        except ValueError as e:
            return f"❌ Error: Invalid date/time format. Error: {e}"
        
        # Get events in the time range
        time_min = start_datetime.isoformat() + 'Z'
        time_max = end_datetime.isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return f"✅ Time slot is available!\n\n📅 {start_datetime.strftime('%A, %B %d, %Y')}\n🕐 {start_time} - {end_datetime.strftime('%H:%M')}"
        else:
            result = f"❌ Time slot has conflicts:\n\n"
            result += f"📅 {start_datetime.strftime('%A, %B %d, %Y')}\n"
            result += f"🕐 Requested: {start_time} - {end_datetime.strftime('%H:%M')}\n\n"
            result += "Conflicting meetings:\n"
            
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                if 'T' in start:
                    start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                    time_range = f"{start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')}"
                else:
                    time_range = "All day"
                
                result += f"  • {event.get('summary', 'Untitled')} ({time_range})\n"
            
            return result
        
    except HttpError as error:
        return f"❌ Google Calendar API error: {error}"
    except Exception as e:
        return f"❌ Error checking availability: {str(e)}"

@mcp.tool()
async def update_meeting(
    event_id: str,
    title: Optional[str] = None,
    date: Optional[str] = None,
    time: Optional[str] = None,
    duration_minutes: Optional[int] = None,
    location: Optional[str] = None,
    description: Optional[str] = None
) -> str:
    """
    Update an existing meeting in Google Calendar.
    
    Args:
        event_id: The Google Calendar event ID
        title: New meeting title (optional)
        date: New meeting date YYYY-MM-DD (optional)
        time: New meeting time HH:MM (optional)
        duration_minutes: New duration in minutes (optional)
        location: New location (optional)
        description: New description (optional)
    
    Returns:
        Success message with updated details or error
    """
    try:
        service = get_calendar_service()
        if not service:
            return "❌ Error: Google Calendar not authenticated. Run 'uv run python authenticate_google.py' first."
        
        # Get the existing event
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
        
        # Update fields if provided
        if title:
            event['summary'] = title
        
        if date and time:
            start_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            
            if duration_minutes:
                end_datetime = start_datetime + timedelta(minutes=duration_minutes)
            else:
                # Keep the same duration
                old_start = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
                old_end = datetime.fromisoformat(event['end']['dateTime'].replace('Z', '+00:00'))
                duration = (old_end - old_start).total_seconds() / 60
                end_datetime = start_datetime + timedelta(minutes=duration)
            
            event['start'] = {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'America/Chicago',
            }
            event['end'] = {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'America/Chicago',
            }
        
        if location is not None:  # Allow empty string to remove location
            event['location'] = location
        
        if description is not None:  # Allow empty string to remove description
            event['description'] = description
        
        # Update the event
        updated_event = service.events().update(
            calendarId='primary',
            eventId=event_id,
            body=event
        ).execute()
        
        return f"✅ Meeting updated successfully!\n\n🆔 ID: {event_id}\n🔗 Link: {updated_event.get('htmlLink', 'N/A')}"
        
    except HttpError as error:
        if error.resp.status == 404:
            return f"❌ Error: Meeting not found (ID: {event_id})"
        return f"❌ Google Calendar API error: {error}"
    except Exception as e:
        return f"❌ Error updating meeting: {str(e)}"

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
