#!/usr/bin/env python3
# """
# MCP Server for Email Sending
# Allows AI assistants to send emails using Resend API
# """

import asyncio
import os
from typing import List
from dotenv import load_dotenv
import resend

# Load environment variables
load_dotenv()

# Initialize Resend with API key
resend.api_key = os.getenv("RESEND_API_KEY")

# Import FastMCP
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    # Fallback for older MCP versions
    from mcp.server import Server
    from mcp.types import Tool, TextContent

# Initialize MCP server
mcp = FastMCP("Email Sender")

@mcp.tool()
async def send_email(
    to: List[str],
    subject: str,
    body: str,
    from_email: str = "onboarding@resend.dev",
    plain_text: str | None = None,
) -> str:
    """
    Send an email to one or more recipients.
    
    Args:
        to: List of recipient email addresses
        subject: Email subject line
        body: Email body content (HTML supported)
        from_email: Sender email address (optional, defaults to onboarding@resend.dev)
    
    Returns:
        Success message with email ID or error message
    """
    try:
        # Validate inputs
        if not to or not subject or not body:
            return "Error: Missing required fields (to, subject, body)"
        
        if not resend.api_key:
            return "Error: RESEND_API_KEY not found in environment variables"
        
        # Build a simple text fallback if not provided
        text_fallback = plain_text if plain_text is not None else (
            body.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n").replace("</p>", "\n").replace("<p>", "")
        )

        # If only one recipient, pass a string like test_email does
        to_field = to[0] if isinstance(to, list) and len(to) == 1 else to

        # Send email using Resend (mirror test_email structure)
        response = resend.Emails.send({
            "from": from_email,
            "to": to_field,
            "subject": subject,
            "html": body,
            "text": text_fallback,
        })

        return f"Email sent successfully! id={response.get('id', 'Unknown')} to={to_field} subject={subject}"
        
    except Exception as e:
        return f"Error sending email: {str(e)}"


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
