#!/usr/bin/env python3
"""
Setup script for AI Personal Assistant
Helps configure API keys and test the setup
"""

import os
import sys
from pathlib import Path

def setup_environment():
    """Setup environment variables"""
    print("🔧 Setting up AI Personal Assistant...")
    print()
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("Creating .env file...")
        with open(".env", "w") as f:
            f.write("# AI Personal Assistant Environment Variables\n")
            f.write("RESEND_API_KEY=your_resend_api_key_here\n")
            f.write("ANTHROPIC_API_KEY=your_anthropic_api_key_here\n")
        print("✅ .env file created")
    else:
        print("✅ .env file already exists")
    
    print()
    print("📋 Next steps:")
    print("1. Get your Resend API key from: https://resend.com/api-keys")
    print("2. Get your Anthropic API key from: https://console.anthropic.com/")
    print("3. Update the .env file with your actual API keys")
    print("4. Run: uv run python ai_chat_assistant.py")
    print()
    print("🔑 Current .env file contents:")
    print("-" * 40)
    with open(".env", "r") as f:
        print(f.read())
    print("-" * 40)

def test_setup():
    """Test the setup"""
    print("🧪 Testing setup...")
    
    # Check if dependencies are installed
    try:
        import anthropic
        print("✅ Anthropic library available")
    except ImportError:
        print("❌ Anthropic library not found. Run: uv sync")
        return False
    
    try:
        import resend
        print("✅ Resend library available")
    except ImportError:
        print("❌ Resend library not found. Run: uv sync")
        return False
    
    # Check environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    resend_key = os.getenv("RESEND_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if resend_key and resend_key != "your_resend_api_key_here":
        print("✅ Resend API key configured")
    else:
        print("⚠️  Resend API key not configured")
    
    if anthropic_key and anthropic_key != "your_anthropic_api_key_here":
        print("✅ Anthropic API key configured")
    else:
        print("⚠️  Anthropic API key not configured")
    
    print()
    if resend_key and anthropic_key and resend_key != "your_resend_api_key_here" and anthropic_key != "your_anthropic_api_key_here":
        print("🎉 Setup complete! You can now run the AI assistant.")
        print("Run: uv run python ai_chat_assistant.py")
    else:
        print("⚠️  Please configure your API keys in the .env file")
    
    return True

def main():
    """Main setup function"""
    print("🤖 AI Personal Assistant Setup")
    print("=" * 40)
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_setup()
    else:
        setup_environment()
        print("Run 'python setup.py test' to test your configuration")

if __name__ == "__main__":
    main()

