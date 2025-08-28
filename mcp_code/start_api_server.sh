#!/bin/bash

# MCP Integration API Server Startup Script
# This script starts the FastAPI server with proper environment setup

echo "🚀 Starting MCP Integration API Server..."
echo "========================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3 and try again"
    exit 1
fi

# Check if required packages are installed
echo "🔍 Checking dependencies..."
python3 -c "import fastapi, uvicorn, httpx" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Some required packages are missing"
    echo "Installing required packages..."
    pip3 install fastapi uvicorn httpx
fi

# Check if .env file exists
if [ -f ".env" ]; then
    echo "✅ Found .env file, loading environment variables"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  No .env file found, using default environment"
fi

# Check if MCP client can connect
echo "🔗 Testing MCP client connection..."
python3 -c "
import asyncio
from mcp_client import MCPClient

async def test_connection():
    try:
        client = MCPClient()
        await client.connect_to_servers()
        print('✅ MCP client connection test successful')
        await client.disconnect()
    except Exception as e:
        print(f'⚠️  MCP client connection test failed: {e}')

asyncio.run(test_connection())
"

# Start the API server
echo "🌐 Starting FastAPI server on http://localhost:8000"
echo "📖 API documentation will be available at http://localhost:8000/docs"
echo "🔍 Health check available at http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"

# Start the server
python3 api_server.py
