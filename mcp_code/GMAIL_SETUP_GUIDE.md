# 🔐 Gmail API Setup Guide

This guide will help you set up Gmail API access for the email summarization feature.

## 📋 Prerequisites

- Google account with Gmail
- Python 3.7+ installed
- Basic knowledge of Google Cloud Console

## 🚀 Step-by-Step Setup

### **Step 1: Enable Gmail API**

1. **Go to Google Cloud Console**
   - Visit [console.cloud.google.com](https://console.cloud.google.com/)
   - Sign in with your Google account

2. **Create/Select Project**
   - Click on the project dropdown at the top
   - Click "New Project" or select existing project
   - Give it a name (e.g., "MCP Gmail Integration")

3. **Enable Gmail API**
   - Go to **APIs & Services** > **Library**
   - Search for "Gmail API"
   - Click on "Gmail API"
   - Click **Enable**

### **Step 2: Create OAuth 2.0 Credentials**

1. **Go to Credentials**
   - Navigate to **APIs & Services** > **Credentials**

2. **Create OAuth 2.0 Client ID**
   - Click **Create Credentials** > **OAuth 2.0 Client IDs**
   - Choose **Desktop application**
   - Give it a name: "MCP Gmail Integration"
   - Click **Create**

3. **Download Credentials**
   - Click **Download JSON**
   - Rename the file to `client_secret.json`
   - Place it in your project directory

### **Step 3: Get Access Token**

#### **Option A: Using the Python Script (Recommended)**

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Token Generator**
   ```bash
   python get_gmail_token.py
   ```

3. **Follow the Instructions**
   - A browser window will open
   - Sign in with your Google account
   - Grant permissions to the app
   - Copy the access token

#### **Option B: Using Google OAuth Playground**

1. **Visit OAuth Playground**
   - Go to [developers.google.com/oauthplayground](https://developers.google.com/oauthplayground/)

2. **Configure OAuth**
   - Click the settings icon (⚙️) in the top right
   - Check "Use your own OAuth credentials"
   - Enter your Client ID and Client Secret

3. **Select Scopes**
   - Find **Gmail API v1** in the left panel
   - Select these scopes:
     - `https://www.googleapis.com/auth/gmail.readonly`
     - `https://www.googleapis.com/auth/gmail.send`
     - `https://www.googleapis.com/auth/gmail.modify`

4. **Get Token**
   - Click **Authorize APIs**
   - Sign in and grant permissions
   - Click **Exchange authorization code for tokens**
   - Copy the **Access token**

### **Step 4: Configure Environment Variables**

1. **Create/Update .env File**
   ```bash
   # Gmail API
   GOOGLE_ACCESS_TOKEN=your_access_token_here
   
   # Optional: Other Google APIs
   GOOGLE_API_KEY=your_api_key_here
   GOOGLE_CSE_ID=your_custom_search_engine_id_here
   ```

2. **Replace Placeholders**
   - Replace `your_access_token_here` with the actual token
   - Keep the token secure and don't share it

## 🧪 Testing the Setup

### **Test 1: Verify Token**
```bash
python get_gmail_token.py
```
Should show: "✅ Successfully obtained Gmail access token!"

### **Test 2: Test Email Summarization**
```bash
python test_email_summarize.py
```

### **Test 3: Interactive Chat**
```bash
python main.py --chat
```
Then type: "Summarize my emails and send to user@gmail.com"

## 🔍 Troubleshooting

### **Common Issues & Solutions**

#### **"Server gmail not connected"**
- ✅ Check if `GOOGLE_ACCESS_TOKEN` is set in `.env`
- ✅ Verify the token is valid and not expired
- ✅ Ensure Gmail API is enabled in Google Cloud Console

#### **"Invalid Credentials"**
- ✅ Re-run `python get_gmail_token.py` to get a fresh token
- ✅ Check if the token has the correct scopes
- ✅ Verify the client_secret.json file is correct

#### **"Gmail API not enabled"**
- ✅ Go to Google Cloud Console > APIs & Services > Library
- ✅ Search for "Gmail API" and enable it
- ✅ Wait a few minutes for changes to propagate

#### **"Insufficient permissions"**
- ✅ Make sure you granted all requested permissions during OAuth
- ✅ Check if your Google account has Gmail access
- ✅ Try revoking and re-granting permissions

### **Debug Mode**

The system provides detailed logging. Look for:
- Connection status messages
- Error details with context
- MCP tool execution results

## 🔒 Security Notes

- **Never commit** your `.env` file to version control
- **Keep your access token** secure and private
- **Tokens expire** - you may need to refresh them periodically
- **Revoke access** in Google Account settings if needed

## 📚 Additional Resources

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Google Cloud Console](https://console.cloud.google.com/)
- [OAuth 2.0 Playground](https://developers.google.com/oauthplayground/)

## 🎯 Next Steps

After successful setup:
1. Test the email summarization feature
2. Explore other MCP tools (Google Search, Calendar, Maps)
3. Customize the summary format if needed
4. Set up automated email summaries

---

**Need Help?** Check the error logs and ensure all steps are completed correctly. 