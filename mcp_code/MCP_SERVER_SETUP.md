# MCP Server Setup Guide

## 🚀 **Install Required MCP Server Packages**

To use the real MCP servers for Calendar and Gmail, you need to install the official MCP server packages.

### **1. Install Node.js and npm (if not already installed)**

```bash
# Check if Node.js is installed
node --version
npm --version

# If not installed, install on Ubuntu/Debian
sudo apt update
sudo apt install nodejs npm

# Or on macOS with Homebrew
brew install node
```

### **2. Install MCP Server Packages**

```bash
# Install Google MCP server
npm install -g @modelcontextprotocol/server-google

# Install Slack MCP server  
npm install -g @modelcontextprotocol/server-slack

# Install Maps MCP server
npm install -g @modelcontextprotocol/server-maps

# Install Google Calendar MCP server
npm install -g @modelcontextprotocol/server-google-calendar

# Install Gmail MCP server
npm install -g @modelcontextprotocol/server-gmail
```

### **3. Alternative: Use npx (no global installation)**

The system is configured to use `npx` which downloads and runs packages on-demand:

```bash
# Test if npx works
npx --version

# Test individual MCP servers
npx @modelcontextprotocol/server-google --help
npx @modelcontextprotocol/server-google-calendar --help
npx @modelcontextprotocol/server-gmail --help
```

### **4. Verify Installation**

```bash
# Check if packages are available
npm list -g | grep modelcontextprotocol

# Or test with npx
npx @modelcontextprotocol/server-google --version
```

## 🔧 **Environment Variables Required**

Make sure your `.env` file has:

```env
# For Google services
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_custom_search_engine_id_here

# For Calendar and Gmail (OAuth)
GOOGLE_ACCESS_TOKEN=your_oauth_token_here

# For Slack
SLACK_BOT_TOKEN=your_slack_bot_token_here
SLACK_APP_TOKEN=your_slack_app_token_here
SLACK_SIGNING_SECRET=your_slack_signing_secret_here
```

## 🧪 **Test MCP Server Connection**

1. **Start the server:**
   ```bash
   python3 main.py
   ```

2. **Look for these messages:**
   ```
   ✅ Connected to Google MCP server
   ✅ Connected to Calendar MCP server
   ✅ Connected to Gmail MCP server
   ✅ Connected to Maps MCP server
   ✅ Connected to Slack MCP server
   ```

3. **Test the endpoints:**
   ```bash
   curl "http://localhost:3000/api/calendar/events"
   curl "http://localhost:3000/api/gmail/messages"
   ```

## ⚠️ **Troubleshooting**

### **"npx not found"**
```bash
# Install Node.js and npm
sudo apt install nodejs npm
```

### **"MCP server package not found"**
```bash
# Install the specific package
npm install -g @modelcontextprotocol/server-google-calendar
npm install -g @modelcontextprotocol/server-gmail
```

### **"Server failed to start"**
- Check if the package is installed
- Verify environment variables are set
- Check the server logs for errors

### **"Permission denied"**
```bash
# Use npx instead of global npm install
npx @modelcontextprotocol/server-google-calendar
```

## 🎯 **Expected Behavior**

- **With MCP servers**: Real-time access to Google services
- **Without MCP servers**: Fallback to direct API calls
- **Mixed mode**: Some servers connected, others using direct APIs

## 🔗 **Official MCP Documentation**

- **MCP Protocol**: https://modelcontextprotocol.io/
- **Cursor MCP Servers**: https://cursor.directory/mcp
- **GitHub**: https://github.com/modelcontextprotocol
