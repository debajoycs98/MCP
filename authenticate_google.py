#!/usr/bin/env python3
"""
Google Calendar API Authentication
Run this once to authenticate and generate token.json
"""

import os
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate():
    """Authenticate and return credentials"""
    creds = None
    token_path = 'token.json'
    credentials_path = 'credentials.json'
    
    # Check if credentials.json exists
    if not os.path.exists(credentials_path):
        print("❌ Error: credentials.json not found!")
        print()
        print("Please download credentials.json from Google Cloud Console")
        print("and place it in this directory.")
        return None
    
    print("📄 Found credentials.json")
    
    # The file token.json stores the user's access and refresh tokens
    if os.path.exists(token_path):
        print("📄 Loading existing token...")
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("🔐 Starting OAuth flow...")
            print("A browser window will open for you to authorize the app.")
            print()
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        print("✅ Token saved to token.json")
    else:
        print("✅ Token is valid")
    
    return creds

def test_connection(creds):
    """Test the connection by listing upcoming events"""
    try:
        print()
        print("🔍 Testing connection to Google Calendar...")
        service = build('calendar', 'v3', credentials=creds)
        
        # Call the Calendar API
        print("📅 Fetching your next 10 events...")
        from datetime import datetime
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            print("📭 No upcoming events found.")
        else:
            print(f"✅ Found {len(events)} upcoming events:")
            print()
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                print(f"  • {start}: {event['summary']}")
        
        print()
        print("=" * 70)
        print("✅ SUCCESS! Google Calendar API is working!")
        print("=" * 70)
        print()
        print("You can now use the AI assistant to manage your calendar:")
        print("  • 'Schedule a meeting tomorrow at 2pm'")
        print("  • 'What meetings do I have today?'")
        print("  • 'Cancel my 3pm meeting'")
        print()
        
        return True
        
    except HttpError as error:
        print(f"❌ An error occurred: {error}")
        return False

def main():
    print("=" * 70)
    print("📅 Google Calendar API Authentication")
    print("=" * 70)
    print()
    
    creds = authenticate()
    if creds:
        test_connection(creds)
    else:
        print()
        print("❌ Authentication failed.")
        sys.exit(1)

if __name__ == '__main__':
    main()

