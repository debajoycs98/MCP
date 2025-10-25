#!/usr/bin/env python3
"""
AI-Powered Personal Assistant Chat Interface
Uses Claude API for natural conversation and MCP tools for actions
"""

import asyncio
import os
import sys
import json
from typing import Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import Claude API
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    print("Warning: anthropic library not available. Install with 'uv add anthropic'")

# Import MCP tools
from mcp_servers.email_sender import send_email
from mcp_servers.web_search import search_web, get_news, get_weather, get_stock_price
from mcp_servers.meeting_scheduler import schedule_meeting, list_meetings, cancel_meeting, check_availability
from mcp_servers.pizza_ordering import get_pizza_menu, get_restaurants, order_pizza, check_order_status, list_orders
from mcp_servers.ask_questions import (
    ask_clarifying_question, ask_personal_information, ask_preference_question, 
    ask_confirmation, get_user_response, list_pending_questions
)
from mcp_servers.pdf_reader import (
    read_pdf_text, extract_pdf_images, read_pdf_with_ocr,
    get_pdf_info, analyze_pdf_structure, ask_question_about_pdf, list_loaded_documents
)

class AIPersonalAssistant:
    def __init__(self):
        self.name = "AI Personal Assistant"
        self.version = "2.0.0"
        self.session_start = datetime.now()
        self.conversation_history = []
        
        # Initialize Claude client
        if HAS_ANTHROPIC:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.claude_client = anthropic.Anthropic(api_key=api_key)
            else:
                print("Warning: ANTHROPIC_API_KEY not found in environment variables")
                self.claude_client = None
        else:
            self.claude_client = None
        
        # Available tools for Claude to use
        self.available_tools = {
            "send_email": self.send_email_tool,
            "search_web": self.search_web_tool,
            "get_news": self.get_news_tool,
            "get_weather": self.get_weather_tool,
            "get_stock_price": self.get_stock_price_tool,
            "schedule_meeting": self.schedule_meeting_tool,
            "list_meetings": self.list_meetings_tool,
            "cancel_meeting": self.cancel_meeting_tool,
            "check_availability": self.check_availability_tool,
            "get_pizza_menu": self.get_pizza_menu_tool,
            "get_restaurants": self.get_restaurants_tool,
            "order_pizza": self.order_pizza_tool,
            "check_order_status": self.check_order_status_tool,
            "list_orders": self.list_orders_tool,
            "ask_clarifying_question": self.ask_clarifying_question_tool,
            "ask_personal_information": self.ask_personal_information_tool,
            "ask_preference_question": self.ask_preference_question_tool,
            "ask_confirmation": self.ask_confirmation_tool,
            "list_pending_questions": self.list_pending_questions_tool,
        }
    
    def print_welcome(self):
        """Print welcome message"""
        print("🤖" + "="*60)
        print(f"   {self.name} v{self.version}")
        print("   Powered by Claude Sonnet 4")
        print("   Your intelligent personal assistant")
        print("="*62)
        print()
        print("📧 Email Management    📄 PDF Reading & Q&A    🌐 Web Search")
        print("📅 Meeting Scheduling  🍕 Pizza Ordering       ❓ Smart Questions")
        print()
        print("I can help you with emails, web search, meetings, pizza orders,")
        print("and much more! Just chat with me naturally.")
        print()
        print("Type 'quit' to exit")
        print("="*62)
        print()
    
    async def send_email_tool(self, to: str, subject: str, body: str) -> str:
        """Send an email (matches test_email payload behavior)"""
        try:
            # Mirror test_email by sending a single recipient string and adding text fallback
            html = body if ("<" in body and ">" in body) else f"<p>{body}</p>"
            return await send_email([to], subject, html, "onboarding@resend.dev", plain_text=body)
        except Exception as e:
            return f"Error sending email: {str(e)}"
    
    async def send_simple_email_tool(self, to: str, subject: str, message: str) -> str:
        """Send a simple email (matches test_email payload behavior)"""
        try:
            html = f"<p>{message}</p>"
            return await send_email([to], subject, html, "onboarding@resend.dev", plain_text=message)
        except Exception as e:
            return f"Error sending email: {str(e)}"
    
    async def search_web_tool(self, query: str) -> str:
        """Search the web"""
        try:
            return await search_web(query)
        except Exception as e:
            return f"Error searching web: {str(e)}"
    
    async def get_news_tool(self, topic: str) -> str:
        """Get news about a topic"""
        try:
            return await get_news(topic)
        except Exception as e:
            return f"Error getting news: {str(e)}"
    
    async def get_weather_tool(self, location: str) -> str:
        """Get weather for a location"""
        try:
            return await get_weather(location)
        except Exception as e:
            return f"Error getting weather: {str(e)}"
    
    async def get_stock_price_tool(self, symbol: str) -> str:
        """Get stock price"""
        try:
            return await get_stock_price(symbol)
        except Exception as e:
            return f"Error getting stock price: {str(e)}"
    
    async def schedule_meeting_tool(self, title: str, date: str, time: str, duration: int = 60) -> str:
        """Schedule a meeting"""
        try:
            return await schedule_meeting(title, date, time, duration)
        except Exception as e:
            return f"Error scheduling meeting: {str(e)}"
    
    async def list_meetings_tool(self, date: str = None) -> str:
        """List meetings"""
        try:
            return await list_meetings(date)
        except Exception as e:
            return f"Error listing meetings: {str(e)}"
    
    async def cancel_meeting_tool(self, meeting_id: int) -> str:
        """Cancel a meeting"""
        try:
            return await cancel_meeting(meeting_id)
        except Exception as e:
            return f"Error cancelling meeting: {str(e)}"
    
    async def check_availability_tool(self, date: str, time: str, duration: int = 60) -> str:
        """Check availability"""
        try:
            return await check_availability(date, time, duration)
        except Exception as e:
            return f"Error checking availability: {str(e)}"
    
    async def get_pizza_menu_tool(self) -> str:
        """Get pizza menu"""
        try:
            return await get_pizza_menu()
        except Exception as e:
            return f"Error getting pizza menu: {str(e)}"
    
    async def get_restaurants_tool(self) -> str:
        """Get restaurants"""
        try:
            return await get_restaurants()
        except Exception as e:
            return f"Error getting restaurants: {str(e)}"
    
    async def order_pizza_tool(self, pizza_type: str, size: str = "large", quantity: int = 1, restaurant: str = "dominos") -> str:
        """Order pizza"""
        try:
            return await order_pizza(pizza_type, size, quantity, restaurant)
        except Exception as e:
            return f"Error ordering pizza: {str(e)}"
    
    async def check_order_status_tool(self, order_id: int) -> str:
        """Check order status"""
        try:
            return await check_order_status(order_id)
        except Exception as e:
            return f"Error checking order status: {str(e)}"
    
    async def list_orders_tool(self) -> str:
        """List orders"""
        try:
            return await list_orders()
        except Exception as e:
            return f"Error listing orders: {str(e)}"
    
    async def ask_clarifying_question_tool(self, question: str) -> str:
        """Ask a clarifying question"""
        try:
            return await ask_clarifying_question(question)
        except Exception as e:
            return f"Error asking question: {str(e)}"
    
    async def ask_personal_information_tool(self, info_type: str, purpose: str = "") -> str:
        """Ask for personal information"""
        try:
            return await ask_personal_information(info_type, purpose)
        except Exception as e:
            return f"Error asking for personal information: {str(e)}"
    
    async def ask_preference_question_tool(self, preference_type: str, options: List[str]) -> str:
        """Ask a preference question"""
        try:
            return await ask_preference_question(preference_type, options)
        except Exception as e:
            return f"Error asking preference question: {str(e)}"
    
    async def ask_confirmation_tool(self, action: str) -> str:
        """Ask for confirmation"""
        try:
            return await ask_confirmation(action)
        except Exception as e:
            return f"Error asking for confirmation: {str(e)}"
    
    async def list_pending_questions_tool(self) -> str:
        """List pending questions"""
        try:
            return await list_pending_questions()
        except Exception as e:
            return f"Error listing pending questions: {str(e)}"
    
    async def process_with_claude(self, user_message: str) -> str:
        """Process user message with Claude API"""
        if not self.claude_client:
            return "Error: Claude API not available. Please set ANTHROPIC_API_KEY in your .env file"
        
        try:
            # Define tools for Claude API (using Anthropic's tool format)
            tools = [
                {
                    "name": "send_simple_email",
                    "description": "Send a simple email to a single recipient",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "to": {"type": "string", "description": "Recipient email address"},
                            "subject": {"type": "string", "description": "Email subject line"},
                            "message": {"type": "string", "description": "Plain text message"}
                        },
                        "required": ["to", "subject", "message"]
                    }
                },
                {
                    "name": "search_web",
                    "description": "Search the web for information",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"}
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "read_pdf_text",
                    "description": "Extract text content from a PDF file. Can specify page range.",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "Path to the PDF file"},
                            "page_start": {"type": "integer", "description": "Starting page number (1-indexed, optional)"},
                            "page_end": {"type": "integer", "description": "Ending page number (1-indexed, optional)"}
                        },
                        "required": ["file_path"]
                    }
                },
                {
                    "name": "read_pdf_with_ocr",
                    "description": "Extract text from PDF including OCR from images. Best for scanned documents or PDFs with embedded images containing text.",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "Path to the PDF file"},
                            "page_start": {"type": "integer", "description": "Starting page number (1-indexed, optional)"},
                            "page_end": {"type": "integer", "description": "Ending page number (1-indexed, optional)"},
                            "ocr_language": {"type": "string", "description": "OCR language code (default: 'eng', use 'eng+fra' for multiple)"}
                        },
                        "required": ["file_path"]
                    }
                },
                {
                    "name": "ask_question_about_pdf",
                    "description": "Ask a question about a loaded PDF's content. Must load PDF first using read_pdf_text or read_pdf_with_ocr.",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string", "description": "The question to ask about the PDF content"},
                            "file_path": {"type": "string", "description": "Path to specific PDF (optional, uses all loaded PDFs if not specified)"}
                        },
                        "required": ["question"]
                    }
                },
                {
                    "name": "get_pdf_info",
                    "description": "Get metadata and statistics about a PDF file (page count, file size, images, etc.)",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "Path to the PDF file"}
                        },
                        "required": ["file_path"]
                    }
                }
            ]
            
            # Create system prompt
            system_prompt = """You are a helpful personal AI assistant. Be friendly and conversational.
You have access to tools for:
- Sending emails (send_simple_email)
- Searching the web (search_web)
- Reading PDF files (read_pdf_text, read_pdf_with_ocr)
- Answering questions about PDFs (ask_question_about_pdf)
- Getting PDF information (get_pdf_info)

When the user asks you to perform these tasks, use the appropriate tool.
For simple greetings and conversation, just respond naturally without using tools."""

            # Add conversation history to context
            messages = []
            for entry in self.conversation_history[-10:]:  # Keep last 10 messages for context
                messages.append({"role": "user", "content": entry["user"]})
                if entry["assistant"]:
                    messages.append({"role": "assistant", "content": entry["assistant"]})
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Call Claude API with tools
            response = self.claude_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                system=system_prompt,
                messages=messages,
                tools=tools
            )
            
            # Check if Claude wants to use a tool
            if response.stop_reason == "tool_use":
                # Execute the tool
                tool_results = []
                assistant_text = ""
                
                for content_block in response.content:
                    if content_block.type == "text":
                        assistant_text += content_block.text
                    elif content_block.type == "tool_use":
                        tool_name = content_block.name
                        tool_input = content_block.input
                        tool_id = content_block.id
                        
                        # Execute the tool
                        if tool_name == "send_simple_email":
                            result = await self.send_simple_email_tool(
                                tool_input["to"],
                                tool_input["subject"],
                                tool_input["message"]
                            )
                        elif tool_name == "search_web":
                            result = await self.search_web_tool(tool_input["query"])
                        elif tool_name == "read_pdf_text":
                            result = await read_pdf_text(
                                tool_input["file_path"],
                                tool_input.get("page_start"),
                                tool_input.get("page_end")
                            )
                        elif tool_name == "read_pdf_with_ocr":
                            result = await read_pdf_with_ocr(
                                tool_input["file_path"],
                                tool_input.get("page_start"),
                                tool_input.get("page_end"),
                                tool_input.get("ocr_language", "eng")
                            )
                        elif tool_name == "ask_question_about_pdf":
                            result = await ask_question_about_pdf(
                                tool_input["question"],
                                tool_input.get("file_path")
                            )
                        elif tool_name == "get_pdf_info":
                            result = await get_pdf_info(tool_input["file_path"])
                        else:
                            result = f"Unknown tool: {tool_name}"
                        
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": result
                        })
                
                # If tools were used, call Claude again with the results
                if tool_results:
                    messages.append({"role": "assistant", "content": response.content})
                    messages.append({"role": "user", "content": tool_results})
                    
                    final_response = self.claude_client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=2000,
                        system=system_prompt,
                        messages=messages,
                        tools=tools
                    )
                    
                    return final_response.content[0].text
                
                return assistant_text
            else:
                # No tool use, just return the text
                return response.content[0].text
            
        except Exception as e:
            return f"Error processing with Claude: {str(e)}"
    
    async def run(self):
        """Run the AI chat assistant"""
        self.print_welcome()
        
        if not self.claude_client:
            print("❌ Claude API not available. Please set ANTHROPIC_API_KEY in your .env file")
            return
        
        while True:
            try:
                # Get user input
                user_input = input("🤖 You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle quit
                if user_input.lower() in ["quit", "exit", "bye"]:
                    print("👋 Goodbye! Thanks for using the AI Personal Assistant!")
                    break
                
                # Add to conversation history
                self.conversation_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "user": user_input,
                    "assistant": ""
                })
                
                # Process with Claude
                print("🤖 Assistant: ", end="", flush=True)
                response = await self.process_with_claude(user_input)
                print(response)
                print()
                
                # Update conversation history
                if self.conversation_history:
                    self.conversation_history[-1]["assistant"] = response
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye! Thanks for using the AI Personal Assistant!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")

async def main():
    """Main function"""
    assistant = AIPersonalAssistant()
    await assistant.run()

if __name__ == "__main__":
    asyncio.run(main())
