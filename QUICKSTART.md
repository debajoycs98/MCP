# 🚀 Quick Start Guide

Get your Personal AI Assistant up and running in 5 minutes!

## 📋 Prerequisites Check

Before you start, make sure you have:

- [ ] Python 3.11+ installed
- [ ] Docker Desktop installed
- [ ] `uv` package manager installed
- [ ] Resend API key (get at [resend.com](https://resend.com))
- [ ] Anthropic API key (get at [console.anthropic.com](https://console.anthropic.com))

## ⚡ 5-Minute Setup

### Step 1: Clone & Install (1 min)

```bash
git clone https://github.com/debajoycs98/MCP.git
cd MCP
uv sync
```

### Step 2: Configure API Keys (1 min)

Create a `.env` file:

```bash
cat > .env << 'ENVEOF'
RESEND_API_KEY=your_resend_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
WEBSEARCH_API_URL=http://localhost:3001
ENVEOF
```

Replace `your_resend_api_key_here` and `your_anthropic_api_key_here` with your actual API keys.

### Step 3: Start WebSearch Services (2 min)

```bash
# Open Docker Desktop first!

# Start the web search crawler
./start_websearch.sh

# Wait 30 seconds for services to initialize...
```

### Step 4: Test Your Setup (1 min)

```bash
# Test email
uv run python test_email.py

# Test web search
uv run python test_websearch.py

# Test PDF reader
uv run python test_pdf_reader.py
```

### Step 5: Launch Your AI Assistant! 🎉

```bash
uv run python ai_chat_assistant.py
```

## 💬 Try These Commands

Once your assistant is running, try:

### 📧 Email
```
Send an email to test@example.com with subject "Hello" and message "This is a test"
```

### 🔍 Web Search
```
Search the web for latest AI developments
What's the news about SpaceX?
```

### 📄 PDF Reading
```
Read the PDF at /path/to/your/document.pdf
Ask about the pdf: What is the main topic?
```

### 📅 Meetings (requires Google Calendar setup)
```
Schedule a meeting tomorrow at 2pm about project review
List my upcoming meetings
```

## 🆘 Troubleshooting

### "Docker not running"
- Open Docker Desktop application
- Wait for Docker icon in menu bar to be active

### "Connection refused" for web search
- Make sure Docker Desktop is running
- Wait 30-60 seconds after starting services
- Check status: `docker-compose ps`

### Email not sending
- Verify your Resend API key in `.env`
- Check you're using a valid "from" address
- Test with: `uv run python test_email.py`

### Claude API errors
- Verify your Anthropic API key in `.env`
- Check your API usage at console.anthropic.com

## 📚 Next Steps

- **Full Documentation**: Read [ReadMe.md](ReadMe.md)
- **WebSearch Setup**: See [WEBSEARCH_SETUP.md](WEBSEARCH_SETUP.md)
- **Google Calendar**: Follow authentication steps for meeting scheduling

## 🎯 What You Can Do

Your Personal AI Assistant can:

✅ Send emails to anyone
✅ Search the web in real-time
✅ Read and analyze PDFs
✅ Schedule meetings (with Google Calendar)
✅ Answer questions naturally
✅ Order pizza (simulation)
✅ Ask clarifying questions

## 🌟 Advanced Usage

### Stop Services When Done
```bash
docker-compose down
```

### Update Dependencies
```bash
uv sync --upgrade
```

### View Logs
```bash
# Web search logs
docker-compose logs -f crawler

# AI assistant with verbose output
uv run python ai_chat_assistant.py --verbose
```

## 🤝 Need Help?

- Check [ReadMe.md](ReadMe.md) for detailed documentation
- Review [WEBSEARCH_SETUP.md](WEBSEARCH_SETUP.md) for web search issues
- Ensure all environment variables are set in `.env`

---

**Ready to go?** Run `uv run python ai_chat_assistant.py` and start chatting! 🚀
