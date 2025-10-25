#!/usr/bin/env python3
"""
Main MCP Server - Personal AI Assistant
Combines all MCP tools for the personal AI assistant project
"""

import asyncio
import os
from typing import List, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import FastMCP
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    from mcp.server import Server
    from mcp.types import Tool, TextContent

# Import all the individual MCP servers
from mcp_servers.email_sender import send_email, send_simple_email
from mcp_servers.pdf_reader import read_pdf, read_multiple_pdfs, ask_question_about_pdf, list_loaded_documents
from mcp_servers.web_search import search_web, get_news, get_weather, get_stock_price
from mcp_servers.meeting_scheduler import schedule_meeting, list_meetings, cancel_meeting, check_availability
from mcp_servers.pizza_ordering import get_pizza_menu, get_restaurants, order_pizza, check_order_status, list_orders
from mcp_servers.ask_questions import (
    ask_clarifying_question, ask_personal_information, ask_preference_question, 
    ask_confirmation, get_user_response, list_pending_questions
)

# Initialize main MCP server
mcp = FastMCP("Personal AI Assistant")

# Register all tools from individual servers
@mcp.tool()
async def send_email_tool(
    to: List[str],
    subject: str,
    body: str,
    from_email: str = "onboarding@resend.dev"
) -> str:
    """Send an email to one or more recipients."""
    return await send_email(to, subject, body, from_email)

@mcp.tool()
async def send_simple_email_tool(
    to: str,
    subject: str,
    message: str
) -> str:
    """Send a simple text email to a single recipient."""
    return await send_simple_email(to, subject, message)

@mcp.tool()
async def read_pdf_tool(file_path: str) -> str:
    """Read and extract text from a PDF file."""
    return await read_pdf(file_path)

@mcp.tool()
async def read_multiple_pdfs_tool(file_paths: List[str]) -> str:
    """Read and extract text from multiple PDF files."""
    return await read_multiple_pdfs(file_paths)

@mcp.tool()
async def ask_question_about_pdf_tool(
    question: str, 
    file_path: Optional[str] = None
) -> str:
    """Ask a question about the content of a PDF file."""
    return await ask_question_about_pdf(question, file_path)

@mcp.tool()
async def list_loaded_documents_tool() -> str:
    """List all currently loaded PDF documents."""
    return await list_loaded_documents()

@mcp.tool()
async def search_web_tool(query: str, num_results: int = 5) -> str:
    """Search the web for real-time information."""
    return await search_web(query, num_results)

@mcp.tool()
async def get_news_tool(topic: str = "technology", num_articles: int = 3) -> str:
    """Get recent news articles about a specific topic."""
    return await get_news(topic, num_articles)

@mcp.tool()
async def get_weather_tool(location: str) -> str:
    """Get current weather information for a location."""
    return await get_weather(location)

@mcp.tool()
async def get_stock_price_tool(symbol: str) -> str:
    """Get current stock price for a given symbol."""
    return await get_stock_price(symbol)

@mcp.tool()
async def schedule_meeting_tool(
    title: str,
    date: str,
    time: str,
    duration_minutes: int = 60,
    attendees: Optional[List[str]] = None,
    location: Optional[str] = None,
    description: Optional[str] = None
) -> str:
    """Schedule a new meeting."""
    return await schedule_meeting(title, date, time, duration_minutes, attendees, location, description)

@mcp.tool()
async def list_meetings_tool(date: Optional[str] = None) -> str:
    """List scheduled meetings."""
    return await list_meetings(date)

@mcp.tool()
async def cancel_meeting_tool(meeting_id: int) -> str:
    """Cancel a scheduled meeting."""
    return await cancel_meeting(meeting_id)

@mcp.tool()
async def check_availability_tool(
    date: str, 
    time: str, 
    duration_minutes: int = 60
) -> str:
    """Check if a time slot is available for scheduling."""
    return await check_availability(date, time, duration_minutes)

@mcp.tool()
async def get_pizza_menu_tool() -> str:
    """Get the available pizza menu."""
    return await get_pizza_menu()

@mcp.tool()
async def get_restaurants_tool() -> str:
    """Get available pizza restaurants."""
    return await get_restaurants()

@mcp.tool()
async def order_pizza_tool(
    pizza_type: str,
    size: str = "large",
    quantity: int = 1,
    restaurant: str = "dominos",
    customer_name: str = "Customer",
    customer_phone: str = "",
    delivery_address: str = "",
    special_instructions: str = ""
) -> str:
    """Place a pizza order."""
    return await order_pizza(
        pizza_type, size, quantity, restaurant, 
        customer_name, customer_phone, delivery_address, special_instructions
    )

@mcp.tool()
async def check_order_status_tool(order_id: int) -> str:
    """Check the status of a pizza order."""
    return await check_order_status(order_id)

@mcp.tool()
async def list_orders_tool() -> str:
    """List all pizza orders."""
    return await list_orders()

@mcp.tool()
async def ask_clarifying_question_tool(
    question: str,
    context: str = "",
    question_type: str = "general",
    required: bool = False
) -> str:
    """Ask a clarifying question to the user."""
    return await ask_clarifying_question(question, context, question_type, required)

@mcp.tool()
async def ask_personal_information_tool(
    info_type: str,
    purpose: str = "",
    required: bool = True
) -> str:
    """Ask for personal information from the user."""
    return await ask_personal_information(info_type, purpose, required)

@mcp.tool()
async def ask_preference_question_tool(
    preference_type: str,
    options: List[str],
    context: str = ""
) -> str:
    """Ask a preference question with multiple options."""
    return await ask_preference_question(preference_type, options, context)

@mcp.tool()
async def ask_confirmation_tool(
    action: str,
    details: str = "",
    consequences: str = ""
) -> str:
    """Ask for confirmation before performing an action."""
    return await ask_confirmation(action, details, consequences)

@mcp.tool()
async def get_user_response_tool(question_id: str, response: str) -> str:
    """Record a user's response to a question."""
    return await get_user_response(question_id, response)

@mcp.tool()
async def list_pending_questions_tool() -> str:
    """List all pending (unanswered) questions."""
    return await list_pending_questions()

@mcp.tool()
async def get_available_tools() -> str:
    """
    Get a list of all available tools in the Personal AI Assistant.
    
    Returns:
        List of all available tools with descriptions
    """
    tools_info = """
🤖 Personal AI Assistant - Available Tools

📧 EMAIL TOOLS (1pt):
• send_email_tool - Send emails to multiple recipients
• send_simple_email_tool - Send simple text emails

📄 PDF TOOLS (1pt):
• read_pdf_tool - Read and extract text from PDF files
• read_multiple_pdfs_tool - Read multiple PDF files
• ask_question_about_pdf_tool - Ask questions about PDF content
• list_loaded_documents_tool - List loaded PDF documents

🌐 WEB SEARCH TOOLS (1pt):
• search_web_tool - Search the internet for information
• get_news_tool - Get recent news articles
• get_weather_tool - Get weather information
• get_stock_price_tool - Get stock prices

📅 MEETING TOOLS (1pt):
• schedule_meeting_tool - Schedule meetings
• list_meetings_tool - List scheduled meetings
• cancel_meeting_tool - Cancel meetings
• check_availability_tool - Check time availability

🍕 PIZZA TOOLS (2pt):
• get_pizza_menu_tool - Get pizza menu
• get_restaurants_tool - Get available restaurants
• order_pizza_tool - Place pizza orders
• check_order_status_tool - Check order status
• list_orders_tool - List all orders

❓ QUESTION TOOLS (2pt):
• ask_clarifying_question_tool - Ask clarifying questions
• ask_personal_information_tool - Ask for personal info
• ask_preference_question_tool - Ask preference questions
• ask_confirmation_tool - Ask for confirmation
• get_user_response_tool - Record user responses
• list_pending_questions_tool - List pending questions

🔧 UTILITY TOOLS:
• get_available_tools - List all available tools
"""
    return tools_info

if __name__ == "__main__":
    print("🚀 Starting Personal AI Assistant MCP Server...")
    print("📧 Email sending capabilities")
    print("📄 PDF reading and Q&A")
    print("🌐 Web search capabilities")
    print("📅 Meeting scheduling")
    print("🍕 Pizza ordering")
    print("❓ Question asking and user interaction")
    print("\nServer is running...")
    
    # Run the MCP server
    mcp.run()
