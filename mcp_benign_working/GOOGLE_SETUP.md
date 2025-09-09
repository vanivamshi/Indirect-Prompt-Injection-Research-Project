# Google Calendar & Gmail Setup Guide

## 🔑 **Required API Keys & Tokens**

### 1. **Google API Key** (for Custom Search & Maps) ✅ **REQUIRED**
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Create a new project or select existing one
- Enable **Custom Search API**
- Create credentials → API Key
- Add to `.env`: `GOOGLE_API_KEY=your_api_key_here`

### 2. **Google Custom Search Engine ID** ✅ **REQUIRED**
- Go to [Google Custom Search](https://cse.google.com/cse/)
- Create a new search engine
- Copy the **Search Engine ID**
- Add to `.env`: `GOOGLE_CSE_ID=your_cse_id_here`

### 3. **Google OAuth Access Token** (for Calendar & Gmail) ✅ **REQUIRED**
- **Required for**: Real Gmail and Calendar access through MCP
- **Setup**: OAuth 2.0 flow with user consent
- **What it enables**: Access to your personal Gmail and Calendar data
- **Scopes needed**: Gmail and Calendar read/write permissions

## 📅 **Google Calendar Features**

### **Get Events**
```bash
# API Endpoint
GET /api/calendar/events?max_results=10

# Chat Commands
"Show my calendar events"
"Check my schedule"
"What meetings do I have today?"
```

### **Parameters**
- `time_min`: Start time (ISO format)
- `time_max`: End time (ISO format)  
- `max_results`: Number of events to return

## 📧 **Gmail Features**

### **Get Messages**
```bash
# API Endpoint
GET /api/gmail/messages?query=important&max_results=5

# Chat Commands
"Check my inbox"
"Show important emails"
"Find emails about meetings"
```

### **Send Message**
```bash
# API Endpoint
POST /api/gmail/send
{
  "to": "recipient@email.com",
  "subject": "Meeting Reminder",
  "body": "Don't forget our meeting tomorrow!"
}

# Chat Commands
"Send an email about the meeting"
"Compose an email to john@company.com"
```

## 🚀 **Quick Test**

1. **Start the server:**
   ```bash
   python3 main.py
   ```

2. **Test Calendar (Real API):**
   ```bash
   curl "http://localhost:3000/api/calendar/events?max_results=5"
   # Returns your actual calendar events (requires OAuth token)
   ```

3. **Test Gmail (Real API):**
   ```bash
   curl "http://localhost:3000/api/gmail/messages?max_results=3"
   # Returns your actual emails (requires OAuth token)
   ```

4. **Test Chat:**
   ```bash
   python3 llm_chat.py
   # Then type: "Show my calendar events" or "Check my Gmail inbox"
   ```

## 🎯 **Current Status: Full MCP Integration**

### **What Works with API Key:**
- ✅ **Google Custom Search** - Real web search results
- ✅ **Google Maps** - Real location/geocoding

### **What Works with OAuth Token:**
- ✅ **Google Calendar** - Real calendar events and scheduling
- ✅ **Gmail** - Real email reading and sending
- 🔐 **Full MCP Access** - Complete integration with your Google services

## ⚠️ **Important Notes**

- **Access Token Expiry**: Google OAuth tokens expire. You'll need to refresh them periodically.
- **Scopes**: Ensure your OAuth app has the necessary scopes:
  - `https://www.googleapis.com/auth/calendar.readonly`
  - `https://www.googleapis.com/auth/gmail.readonly`
  - `https://www.googleapis.com/auth/gmail.send`
- **Rate Limits**: Google APIs have rate limits. Be mindful of usage.

## 🔧 **Troubleshooting**

### **"Access token not configured"**
- Check your `.env` file has `GOOGLE_ACCESS_TOKEN`
- Verify the token is valid and not expired

### **"API not enabled"**
- Enable Google Calendar API and Gmail API in Google Cloud Console
- Check your project has billing enabled

### **"Insufficient permissions"**
- Verify OAuth scopes include calendar and gmail access
- Check if the user has granted necessary permissions
