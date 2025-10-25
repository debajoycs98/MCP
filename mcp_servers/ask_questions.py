#!/usr/bin/env python3
"""
MCP Server for Asking Questions
Allows AI assistants to ask clarifying questions when uncertain or when private information is needed
"""

import asyncio
import os
from typing import List, Optional, Dict
from datetime import datetime
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
mcp = FastMCP("Ask Questions")

# Store for user responses and preferences
user_responses = {}
user_preferences = {}

@mcp.tool()
async def ask_clarifying_question(
    question: str,
    context: str = "",
    question_type: str = "general",
    required: bool = False
) -> str:
    """
    Ask a clarifying question to the user.
    
    Args:
        question: The question to ask the user
        context: Additional context for the question
        question_type: Type of question (general, personal, technical, preference)
        required: Whether the question is required to proceed
    
    Returns:
        Formatted question with context
    """
    try:
        question_id = f"q_{len(user_responses) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Store the question
        user_responses[question_id] = {
            "question": question,
            "context": context,
            "question_type": question_type,
            "required": required,
            "timestamp": datetime.now().isoformat(),
            "answered": False,
            "response": None
        }
        
        # Format the question
        formatted_question = f"❓ Question: {question}\n"
        
        if context:
            formatted_question += f"📝 Context: {context}\n"
        
        formatted_question += f"🏷️ Type: {question_type}\n"
        
        if required:
            formatted_question += f"⚠️ This question is required to proceed.\n"
        
        formatted_question += f"\nPlease provide your answer:"
        
        return formatted_question
        
    except Exception as e:
        return f"Error asking question: {str(e)}"

@mcp.tool()
async def ask_personal_information(
    info_type: str,
    purpose: str = "",
    required: bool = True
) -> str:
    """
    Ask for personal information from the user.
    
    Args:
        info_type: Type of personal information needed (name, email, phone, address, etc.)
        purpose: Why this information is needed
        required: Whether this information is required
    
    Returns:
        Formatted question for personal information
    """
    try:
        question_id = f"personal_{len(user_responses) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create appropriate question based on info type
        questions = {
            "name": "What is your full name?",
            "email": "What is your email address?",
            "phone": "What is your phone number?",
            "address": "What is your address?",
            "birthday": "What is your date of birth?",
            "preferences": "What are your preferences for this task?",
            "confirmation": "Please confirm this information is correct"
        }
        
        question = questions.get(info_type, f"Please provide your {info_type}")
        
        if purpose:
            question += f" (needed for: {purpose})"
        
        # Store the question
        user_responses[question_id] = {
            "question": question,
            "context": f"Personal information request: {info_type}",
            "question_type": "personal",
            "required": required,
            "info_type": info_type,
            "purpose": purpose,
            "timestamp": datetime.now().isoformat(),
            "answered": False,
            "response": None
        }
        
        # Format the question
        formatted_question = f"🔒 Personal Information Request\n\n"
        formatted_question += f"Information needed: {info_type}\n"
        formatted_question += f"Question: {question}\n"
        
        if purpose:
            formatted_question += f"Purpose: {purpose}\n"
        
        if required:
            formatted_question += f"⚠️ This information is required to proceed.\n"
        else:
            formatted_question += f"ℹ️ This information is optional.\n"
        
        formatted_question += f"\nPlease provide your answer:"
        
        return formatted_question
        
    except Exception as e:
        return f"Error asking for personal information: {str(e)}"

@mcp.tool()
async def ask_preference_question(
    preference_type: str,
    options: List[str],
    context: str = ""
) -> str:
    """
    Ask a preference question with multiple options.
    
    Args:
        preference_type: Type of preference being asked
        options: List of available options
        context: Additional context for the question
    
    Returns:
        Formatted preference question with options
    """
    try:
        question_id = f"preference_{len(user_responses) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        question = f"What is your preference for {preference_type}?"
        
        # Store the question
        user_responses[question_id] = {
            "question": question,
            "context": context,
            "question_type": "preference",
            "preference_type": preference_type,
            "options": options,
            "timestamp": datetime.now().isoformat(),
            "answered": False,
            "response": None
        }
        
        # Format the question
        formatted_question = f"🎯 Preference Question\n\n"
        formatted_question += f"Question: {question}\n"
        
        if context:
            formatted_question += f"Context: {context}\n"
        
        formatted_question += f"\nAvailable options:\n"
        for i, option in enumerate(options, 1):
            formatted_question += f"{i}. {option}\n"
        
        formatted_question += f"\nPlease select your preference (enter the number or option name):"
        
        return formatted_question
        
    except Exception as e:
        return f"Error asking preference question: {str(e)}"

@mcp.tool()
async def ask_confirmation(
    action: str,
    details: str = "",
    consequences: str = ""
) -> str:
    """
    Ask for confirmation before performing an action.
    
    Args:
        action: The action that needs confirmation
        details: Additional details about the action
        consequences: What will happen if confirmed
    
    Returns:
        Formatted confirmation request
    """
    try:
        question_id = f"confirmation_{len(user_responses) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        question = f"Please confirm: {action}"
        
        # Store the question
        user_responses[question_id] = {
            "question": question,
            "context": details,
            "question_type": "confirmation",
            "action": action,
            "consequences": consequences,
            "timestamp": datetime.now().isoformat(),
            "answered": False,
            "response": None
        }
        
        # Format the confirmation
        formatted_question = f"✅ Confirmation Required\n\n"
        formatted_question += f"Action: {action}\n"
        
        if details:
            formatted_question += f"Details: {details}\n"
        
        if consequences:
            formatted_question += f"Consequences: {consequences}\n"
        
        formatted_question += f"\nDo you want to proceed? (yes/no)"
        
        return formatted_question
        
    except Exception as e:
        return f"Error asking for confirmation: {str(e)}"

@mcp.tool()
async def get_user_response(question_id: str, response: str) -> str:
    """
    Record a user's response to a question.
    
    Args:
        question_id: ID of the question being answered
        response: User's response
    
    Returns:
        Confirmation of the response
    """
    try:
        if question_id not in user_responses:
            return f"Error: Question ID {question_id} not found."
        
        # Update the response
        user_responses[question_id]["response"] = response
        user_responses[question_id]["answered"] = True
        user_responses[question_id]["response_time"] = datetime.now().isoformat()
        
        # Store in preferences if it's a preference question
        if user_responses[question_id]["question_type"] == "preference":
            preference_type = user_responses[question_id]["preference_type"]
            user_preferences[preference_type] = response
        
        return f"✅ Response recorded: {response}"
        
    except Exception as e:
        return f"Error recording response: {str(e)}"

@mcp.tool()
async def list_pending_questions() -> str:
    """
    List all pending (unanswered) questions.
    
    Returns:
        List of pending questions
    """
    try:
        pending_questions = [q for q in user_responses.values() if not q["answered"]]
        
        if not pending_questions:
            return "No pending questions."
        
        result = f"📋 Pending Questions ({len(pending_questions)} total):\n\n"
        
        for i, question in enumerate(pending_questions, 1):
            result += f"{i}. {question['question']}\n"
            result += f"   Type: {question['question_type']}\n"
            result += f"   Required: {'Yes' if question['required'] else 'No'}\n"
            result += f"   Time: {question['timestamp']}\n\n"
        
        return result
        
    except Exception as e:
        return f"Error listing pending questions: {str(e)}"

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
