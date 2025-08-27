# Enhanced MCP Integration with Intelligent Email Highlighting

This enhanced version of the MCP Integration Project now includes powerful **intelligent email highlighting** capabilities that process full email content and extract meaningful highlights as readable paragraphs.

## 🚀 New Features

### 📧 Intelligent Email Highlighting
- **Full Content Processing**: Reads complete email body content, not just snippets
- **Smart Highlight Extraction**: Identifies action items, deadlines, meetings, and key topics
- **Paragraph Formatting**: Presents highlights as coherent, readable paragraphs
- **Content Cleaning**: Removes HTML tags, signatures, and unnecessary formatting
- **Intelligent Fallbacks**: Provides meaningful summaries even for complex content

### 🔍 What Gets Highlighted
- **Action Items**: "please review", "need approval", "urgent request"
- **Timelines**: "tomorrow", "next week", "2 PM today", "by Friday"
- **Key Topics**: "project", "meeting", "budget", "client", "team update"
- **Business Context**: "approval required", "feedback needed", "status update"

### 📧 Enhanced Email Summarization
- **Automatic Email Processing**: Fetches recent emails from your Gmail inbox
- **Smart Summarization**: Creates concise summaries with intelligent highlights
- **Direct Delivery**: Sends enhanced summaries directly to any email address
- **MCP Integration**: Uses MCP tools for seamless Gmail interaction

### 🤖 Enhanced LLM Interface
- **Interactive Chat Mode**: Command-line interface for direct LLM interaction
- **Smart Response Generation**: Intelligent responses for general questions
- **MCP Tool Integration**: Automatically uses appropriate MCP tools based on user input

## 🎯 How to Use Enhanced Email Highlighting

### 1. Web API Interface
```bash
# Start the web server
python main.py

# Use the API endpoint
curl -X POST "http://localhost:3000/api/gmail/summarize" \
  -H "Content-Type: application/json" \
  -d '{"target_email": "user@gmail.com", "max_emails": 10}'
```

### 2. Chat Interface
```bash
# Start interactive chat mode
python main.py --chat

# Then type:
"Summarize my emails and send to user@gmail.com"
```

### 3. Test the Highlighting
```bash
# Test the new highlighting functionality
python test_email_highlights.py
```

### 4. Direct API Call
```python
from main import MCPClient

async def summarize_emails():
    mcp_client = MCPClient()
    await mcp_client.connect_to_servers()
    
    result = await mcp_client.call_tool("gmail", "summarize_and_send", {
        "target_email": "user@gmail.com",
        "max_emails": 10
    })
    
    print(result)
```

## 🔧 Setup Requirements

### Environment Variables
Create a `.env` file with:
```bash
GOOGLE_ACCESS_TOKEN=your_google_access_token_here
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_custom_search_engine_id_here
```

### Google API Setup
1. **Enable Gmail API** in Google Cloud Console
2. **Create OAuth 2.0 credentials** with Gmail scope
3. **Get access token** with Gmail permissions
4. **Set GOOGLE_ACCESS_TOKEN** in your environment

## 📱 Usage Examples

### Enhanced Email Summarization Prompts
```
"Summarize my emails and send to john@company.com"
"Create a summary of my inbox and email it to me@example.com"
"Summarize my recent emails and send to user@gmail.com"
```

### What You'll Get Now
**Before (Old System):**
```
1. SUBJECT: Project Update Meeting
   FROM: manager@company.com
   SNIPPET: Project update and meeting scheduling...
```

**After (Enhanced System):**
```
1. SUBJECT: Project Update Meeting
   FROM: manager@company.com
   
   📝 HIGHLIGHTS: Action required: review the quarterly report by tomorrow. Timeline: next week. Topic: Meeting. Topic: Budget. Action required: client approval required by Friday.
```

### Other LLM Interactions
```
"Search for artificial intelligence news"
"Find the location of Times Square"
"Show my calendar events"
"Check my Gmail inbox"
"What is your name?"
"What is today's date?"
```

## 🏗️ Architecture

### MCP Tools Available
- **Gmail**: `get_messages`, `send_message`, `summarize_and_send` (Enhanced)
- **Google Search**: `search`
- **Google Calendar**: `get_events`
- **Google Maps**: `geocode`
- **Slack**: `send_message` (temporarily disabled)

### Core Components
- **MCPClient**: Manages connections to MCP servers
- **Enhanced Email Processing**: Fetches and processes full Gmail message content
- **Intelligent Highlight Extraction**: Identifies key information using pattern matching
- **Smart Summary Generation**: Creates structured summaries with highlights as paragraphs
- **LLM Interface**: Provides intelligent responses and tool selection

## 🧪 Testing

### Test Enhanced Email Highlighting
```bash
python test_email_highlights.py
```

### Test Web Server
```bash
python main.py
# Then visit http://localhost:3000/api/health
```

### Test Interactive Chat
```bash
python main.py --chat
```

## 🔍 API Endpoints

- `GET /api/health` - Health check
- `POST /api/chat` - LLM chat interface
- `POST /api/gmail/summarize` - Enhanced email summarization with highlights
- `GET /api/gmail/messages` - Get Gmail messages
- `POST /api/gmail/send` - Send Gmail message
- `GET /api/calendar/events` - Get calendar events
- `POST /api/search` - Google search

## 🚨 Troubleshooting

### Common Issues
1. **Gmail API Errors**: Check your access token and permissions
2. **MCP Server Issues**: Ensure Node.js/npm is installed for MCP servers
3. **Environment Variables**: Verify all required variables are set

### Debug Mode
The system provides detailed logging for troubleshooting:
- Server connection status
- MCP tool execution results
- Error messages with context
- Highlight extraction results

## 🔮 Future Enhancements

- **AI-Powered Highlights**: Use LLM models for even better content analysis
- **Custom Highlight Patterns**: Configurable patterns for different business contexts
- **Sentiment Analysis**: Identify urgent vs. informational emails
- **Priority Scoring**: Rank emails by importance based on content analysis
- **Multi-Provider Support**: Support for Outlook, Yahoo Mail, etc.

## 📞 Support

For issues or questions:
1. Check the error logs
2. Verify environment variables
3. Test with the provided test scripts
4. Review Google API documentation

---

**Happy Intelligent Email Highlighting! 📧✨🔍** 