# MCP Integration API with Tool Chaining

This document describes the new FastAPI server that implements automatic tool chaining between Gmail and web access tools, with enhanced security for URL processing.

## 🚀 Features

### Automatic Tool Chaining
- **Gmail → URL Extraction → Web Processing**: Automatically extracts URLs from Gmail messages and processes them using appropriate MCP tools
- **Smart Content Routing**: Wikipedia URLs are processed with `wikipedia.get_page`, other URLs with `web_access.get_content`
- **Configurable Chain Length**: Limit the number of URLs processed per request

### Injection-Safe URL Handling
- **Domain Whitelisting**: Only allows known safe domains
- **Malicious Pattern Detection**: Blocks URLs with suspicious file extensions, protocols, and patterns
- **URL Sanitization**: Removes dangerous content like script tags and JavaScript protocols
- **Local Network Protection**: Blocks localhost and internal IP addresses

### Enhanced Security
- **Regex-based URL Extraction**: Robust pattern matching with cleanup
- **Content Type Validation**: Ensures URLs point to safe content types
- **Processing Time Monitoring**: Tracks how long each URL takes to process
- **Error Handling**: Graceful fallback for failed URL processing

## 🏗️ Architecture

```
User Request → FastAPI Server → MCP Client → Tool Execution
                    ↓
            URL Extraction & Validation
                    ↓
            Safe URL Processing
                    ↓
            Content Retrieval & Return
```

## 📡 API Endpoints

### POST `/api/chat`
Main endpoint for processing chat requests with automatic tool chaining.

**Request Body:**
```json
{
  "message": "Check my Gmail inbox",
  "max_urls": 3,
  "enable_tool_chaining": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Processed your request successfully. Found and processed 2 URLs. Executed 3 tools.",
  "tool_results": [
    {
      "tool": "gmail.get_messages",
      "result": {...},
      "success": true
    },
    {
      "tool": "url_processing.wikipedia",
      "result": {
        "url": "https://en.wikipedia.org/wiki/Python",
        "domain": "en.wikipedia.org",
        "content": {...},
        "processing_time": 1.23
      },
      "success": true
    }
  ],
  "processed_urls": [...]
}
```

### GET `/health`
Health check endpoint to verify API and MCP client status.

### GET `/`
API information and available endpoints.

## 🔧 Tool Chaining Workflow

### 1. Gmail Message Processing
```python
# User requests Gmail messages
POST /api/chat
{
  "message": "Check my Gmail inbox",
  "enable_tool_chaining": true
}

# System automatically:
# 1. Calls gmail.get_messages
# 2. Extracts URLs from message bodies
# 3. Validates and sanitizes URLs
# 4. Processes each URL with appropriate tool
# 5. Returns combined results
```

### 2. URL Processing Logic
```python
for url in extracted_urls:
    if is_safe_url(url):
        sanitized_url = sanitize_url(url)
        if "wikipedia.org" in url:
            content = await wikipedia.get_page(title, url)
        else:
            content = await web_access.get_content(url)
        results.append(content)
```

### 3. Security Validation
```python
def is_safe_url(url):
    # Check blocked domains
    # Check safe domain whitelist
    # Check suspicious patterns
    # Check local network access
    # Validate file extensions
    return safety_score
```

## 🛡️ Security Features

### Domain Whitelist
- **Wikipedia**: All wikipedia.org domains
- **Development**: GitHub, Stack Overflow, Python.org
- **Documentation**: MDN, W3Schools, GeeksforGeeks
- **Learning**: RealPython, TutorialsPoint

### Blocked Patterns
- **Executable Files**: .exe, .bat, .cmd, .com, .scr, .pif, .vbs, .js, .jar, .msi, .dmg, .app
- **Dark Web**: .onion, .bit, .tor
- **IP Addresses**: Direct IP access
- **Admin Panels**: wp-admin, phpmyadmin, cpanel
- **Suspicious TLDs**: .ru, .cn, .tk, .ml, .ga, .cf, .gq

### URL Sanitization
- **Script Removal**: Strips `<script>` tags
- **Protocol Filtering**: Blocks javascript:, data:, vbscript:
- **Whitespace Cleanup**: Removes leading/trailing spaces
- **Protocol Enforcement**: Ensures http/https prefix

## 🚀 Getting Started

### 1. Start the API Server
```bash
python api_server.py
```

The server will start on `http://localhost:8000`

### 2. Test the API
```bash
python test_api.py
```

### 3. Make API Calls
```bash
# Check Gmail with tool chaining
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Check my Gmail inbox",
    "max_urls": 2,
    "enable_tool_chaining": true
  }'

# Process specific URLs
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Check this: https://en.wikipedia.org/wiki/Python",
    "max_urls": 1,
    "enable_tool_chaining": true
  }'
```

## 📊 Configuration Options

### Request Parameters
- **message**: User input to process
- **max_urls**: Maximum URLs to process (default: 3)
- **enable_tool_chaining**: Enable automatic chaining (default: true)

### Environment Variables
- **GOOGLE_ACCESS_TOKEN**: For Gmail API access
- **SLACK_BOT_TOKEN**: For Slack integration
- **GOOGLE_API_KEY**: For Google services

## 🔍 Monitoring & Debugging

### Logging
The API provides detailed logging for:
- Tool execution status
- URL processing results
- Security validation decisions
- Processing time metrics

### Health Checks
- MCP client connection status
- Server uptime
- Tool availability

## 🧪 Testing

### Unit Tests
```bash
python -m pytest test_api.py
```

### Integration Tests
```bash
# Start server in background
python api_server.py &

# Run tests
python test_api.py

# Stop server
pkill -f api_server.py
```

### Manual Testing
1. Start the API server
2. Use the test script
3. Check logs for detailed information
4. Verify URL processing results

## 🔒 Security Considerations

### URL Validation
- All URLs are validated before processing
- Suspicious patterns are blocked
- Local network access is prevented

### Content Processing
- HTML content is sanitized
- Script execution is prevented
- File downloads are restricted

### Rate Limiting
- Consider implementing rate limiting for production
- Monitor for abuse patterns
- Log suspicious requests

## 🚧 Future Enhancements

### Planned Features
- **Rate Limiting**: Prevent API abuse
- **Caching**: Cache frequently accessed content
- **Metrics**: Detailed performance analytics
- **Webhooks**: Real-time notifications
- **Authentication**: API key management

### Integration Opportunities
- **Slack Bots**: Automatic URL processing in Slack
- **Discord Bots**: Similar functionality for Discord
- **Browser Extensions**: Direct URL processing
- **Mobile Apps**: Native mobile integration

## 📝 Troubleshooting

### Common Issues
1. **MCP Client Connection Failed**
   - Check environment variables
   - Verify MCP server status
   - Review connection logs

2. **URL Processing Errors**
   - Check URL format
   - Verify domain accessibility
   - Review security logs

3. **Tool Execution Failures**
   - Check MCP tool availability
   - Verify API credentials
   - Review error logs

### Debug Mode
Enable detailed logging by setting log level to DEBUG in the server configuration.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
