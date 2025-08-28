#!/bin/bash

# Where you stored your Google OAuth credentials
CRED_PATH="$HOME/credentials.json"
TOKEN_PATH="$HOME/token.json"

echo "🔑 Using credentials: $CRED_PATH"
echo "📂 Token will be saved to: $TOKEN_PATH"

if [ ! -f "$CRED_PATH" ]; then
  echo "❌ ERROR: credentials.json not found at $CRED_PATH"
  echo "➡️  Download it from Google Cloud Console (OAuth client ID, Desktop App)."
  exit 1
fi

echo "🌐 Starting Google Calendar MCP server..."
echo "👉 Please log in with your Google account when the browser opens."

# Run Calendar MCP server once to trigger login
npx @teamsparta/mcp-server-google-calendar \
  --credentials "$CRED_PATH" \
  --token "$TOKEN_PATH"

echo ""
echo "✅ Google token saved to $TOKEN_PATH"
echo "You can now set in your .env file:"
echo "GOOGLE_CREDENTIALS_PATH=\"$CRED_PATH\""
echo "GOOGLE_TOKEN_PATH=\"$TOKEN_PATH\""
