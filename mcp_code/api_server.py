#!/usr/bin/env python3
"""
FastAPI Server for MCP Integration with Tool Chaining
This file provides the /api/chat endpoint with automatic URL processing.
"""

import re
import asyncio
import json
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse, urljoin
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from mcp_client import MCPClient

# Initialize FastAPI app
app = FastAPI(
    title="MCP Integration API",
    description="API for MCP tool integration with automatic URL processing",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MCP client
mcp_client = MCPClient()

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str = Field(..., description="User message to process")
    max_urls: int = Field(default=3, description="Maximum number of URLs to process from emails")
    enable_tool_chaining: bool = Field(default=True, description="Enable automatic tool chaining")

class ChatResponse(BaseModel):
    success: bool
    message: str
    tool_results: List[Dict[str, Any]]
    processed_urls: List[Dict[str, Any]]
    error: Optional[str] = None

class URLProcessingResult(BaseModel):
    url: str
    domain: str
    content_type: str
    content: Dict[str, Any]
    processing_time: float
    is_safe: bool

# Safe domain whitelist
SAFE_DOMAINS = {
    "wikipedia.org",
    "en.wikipedia.org",
    "wikimedia.org",
    "github.com",
    "stackoverflow.com",
    "python.org",
    "docs.python.org",
    "developer.mozilla.org",
    "w3schools.com",
    "geeksforgeeks.org",
    "tutorialspoint.com",
    "realpython.com",
    "pythonprogramming.net",
    "learnpython.org",
    "pythonforbeginners.com",
    "pythoncentral.io",
    "pythonbasics.org",
    "python-course.eu",
    "pythonprogramminglanguage.com",
    "pythonprogramming.net",
    "pythonforbeginners.com",
    "pythoncentral.io",
    "pythonbasics.org",
    "python-course.eu",
    "pythonprogramminglanguage.com"
}

# Blocked domains for security
BLOCKED_DOMAINS = {
    "malware.com",
    "phishing.com",
    "scam.com",
    "virus.com",
    "hack.com",
    "exploit.com",
    "crack.com",
    "warez.com",
    "torrent.com",
    "pirate.com"
}

def is_safe_url(url: str) -> bool:
    """Check if URL is safe to process"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Check if domain is blocked
        if domain in BLOCKED_DOMAINS:
            return False
            
        # Check if domain is in safe whitelist
        if domain in SAFE_DOMAINS:
            return True
            
        # Check if it's a Wikipedia domain
        if "wikipedia.org" in domain:
            return True
            
        # Check if it's a localhost or internal IP (block for security)
        if domain in ["localhost", "127.0.0.1", "0.0.0.0"]:
            return False
            
        # Check for suspicious patterns
        suspicious_patterns = [
            r'\.(exe|bat|cmd|com|scr|pif|vbs|js|jar|msi|dmg|app)$',
            r'\.(onion|bit|tor)$',
            r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}',
            r'(admin|login|wp-admin|phpmyadmin|cpanel|webmail)',
            r'(\.ru|\.cn|\.tk|\.ml|\.ga|\.cf|\.gq)$'
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
                
        return True
        
    except Exception:
        return False

def extract_urls_from_text(text: str) -> List[str]:
    """Extract URLs from text using regex"""
    if not text:
        return []
    
    # Enhanced URL regex pattern
    url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
    urls = re.findall(url_pattern, text)
    
    # Clean and validate URLs
    cleaned_urls = []
    for url in urls:
        # Remove trailing punctuation
        url = url.rstrip('.,;:!?')
        # Remove trailing quotes
        url = url.rstrip('"\'')
        # Remove trailing parentheses
        url = url.rstrip(')')
        
        if url and is_safe_url(url):
            cleaned_urls.append(url)
    
    return cleaned_urls

async def process_url_safely(url: str) -> URLProcessingResult:
    """Process URL safely and return content"""
    import time
    start_time = time.time()
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Determine content type and processing method
        if "wikipedia.org" in domain:
            # Extract page title from Wikipedia URL
            path_parts = parsed.path.strip('/').split('/')
            if len(path_parts) >= 2 and path_parts[0] == "wiki":
                page_title = path_parts[1].replace('_', ' ')
                content = await mcp_client.call_tool("wikipedia", "get_page", {
                    "title": page_title,
                    "url": url
                })
                content_type = "wikipedia"
            else:
                content = {"error": "Invalid Wikipedia URL format"}
                content_type = "error"
        else:
            # Use web access for other domains
            content = await mcp_client.call_tool("web_access", "get_content", {
                "url": url
            })
            content_type = "web_content"
        
        processing_time = time.time() - start_time
        
        return URLProcessingResult(
            url=url,
            domain=domain,
            content_type=content_type,
            content=content,
            processing_time=processing_time,
            is_safe=True
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        return URLProcessingResult(
            url=url,
            domain=parsed.netloc.lower() if 'parsed' in locals() else "unknown",
            content_type="error",
            content={"error": str(e)},
            processing_time=processing_time,
            is_safe=False
        )

async def process_gmail_with_url_chaining(messages: List[Dict[str, Any]], max_urls: int = 3) -> List[URLProcessingResult]:
    """Process Gmail messages and automatically chain URL processing"""
    all_urls = []
    
    # Extract URLs from all messages
    for msg in messages:
        body = msg.get("body", "") or msg.get("snippet", "")
        urls = extract_urls_from_text(body)
        all_urls.extend(urls)
    
    # Remove duplicates while preserving order
    unique_urls = list(dict.fromkeys(all_urls))
    
    # Limit to max_urls
    urls_to_process = unique_urls[:max_urls]
    
    # Process URLs safely
    results = []
    for url in urls_to_process:
        result = await process_url_safely(url)
        results.append(result)
    
    return results

@app.on_event("startup")
async def startup_event():
    """Initialize MCP client on startup"""
    try:
        await mcp_client.connect_to_servers()
        print("✅ MCP client initialized successfully")
    except Exception as e:
        print(f"⚠️ MCP client initialization warning: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        await mcp_client.disconnect()
        print("✅ MCP client disconnected")
    except Exception as e:
        print(f"⚠️ MCP client disconnect warning: {e}")

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint with automatic tool chaining"""
    try:
        tool_results = []
        processed_urls = []
        
        # Process the user message
        user_input = request.message.lower()
        
        # Check if this is a Gmail-related request
        if any(word in user_input for word in ["gmail", "email", "mail", "inbox", "emails", "messages"]):
            print(f"📧 Processing Gmail request: {request.message}")
            
            # Call Gmail tool
            if "get_messages" in user_input or "check" in user_input or "read" in user_input:
                gmail_result = await mcp_client.call_tool("gmail", "get_messages", {
                    "query": "",
                    "max_results": 5
                })
                tool_results.append({
                    "tool": "gmail.get_messages",
                    "result": gmail_result,
                    "success": True
                })
                
                # If tool chaining is enabled, automatically process URLs
                if request.enable_tool_chaining and gmail_result.get("messages"):
                    print(f"🔗 Tool chaining enabled - processing URLs from {len(gmail_result['messages'])} messages")
                    url_results = await process_gmail_with_url_chaining(
                        gmail_result["messages"], 
                        request.max_urls
                    )
                    processed_urls = url_results
                    
                    # Add URL processing results to tool results
                    for url_result in url_results:
                        tool_results.append({
                            "tool": f"url_processing.{url_result.content_type}",
                            "result": {
                                "url": url_result.url,
                                "domain": url_result.domain,
                                "content": url_result.content,
                                "processing_time": url_result.processing_time
                            },
                            "success": url_result.is_safe
                        })
            
            elif "get_message_content" in user_input or "read message" in user_input:
                # Extract message ID if provided
                message_id_match = re.search(r'[a-f0-9]{16,}', request.message)
                if message_id_match:
                    message_id = message_id_match.group(0)
                    gmail_result = await mcp_client.call_tool("gmail", "get_message_content", {
                        "message_id": message_id
                    })
                    tool_results.append({
                        "tool": "gmail.get_message_content",
                        "result": gmail_result,
                        "success": True
                    })
                    
                    # Process URLs from message content
                    if request.enable_tool_chaining and gmail_result.get("body"):
                        urls = extract_urls_from_text(gmail_result["body"])
                        if urls:
                            print(f"🔗 Processing {len(urls)} URLs from message content")
                            url_results = await process_gmail_with_url_chaining(
                                [{"body": gmail_result["body"]}], 
                                request.max_urls
                            )
                            processed_urls = url_results
                else:
                    tool_results.append({
                        "tool": "gmail.get_message_content",
                        "result": {"error": "No message ID provided"},
                        "success": False
                    })
        
        # Handle direct URL processing requests
        elif "http" in request.message:
            urls = extract_urls_from_text(request.message)
            if urls:
                print(f"🌐 Processing {len(urls)} URLs from message")
                url_results = await process_gmail_with_url_chaining(
                    [{"body": request.message}], 
                    request.max_urls
                )
                processed_urls = url_results
        
        # Handle other tool requests
        else:
            # Default to Google search if no specific tool detected
            search_result = await mcp_client.call_tool("google", "search", {
                "query": request.message
            })
            tool_results.append({
                "tool": "google.search",
                "result": search_result,
                "success": True
            })
        
        # Prepare response
        response_message = f"Processed your request successfully. "
        if processed_urls:
            response_message += f"Found and processed {len(processed_urls)} URLs. "
        if tool_results:
            response_message += f"Executed {len(tool_results)} tools."
        
        return ChatResponse(
            success=True,
            message=response_message,
            tool_results=tool_results,
            processed_urls=[url_result.dict() for url_result in processed_urls]
        )
        
    except Exception as e:
        print(f"❌ Error in chat endpoint: {e}")
        return ChatResponse(
            success=False,
            message="An error occurred while processing your request",
            tool_results=[],
            processed_urls=[],
            error=str(e)
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "mcp_client_connected": mcp_client.servers != {}}

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "MCP Integration API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/chat": "Main chat endpoint with tool chaining",
            "GET /health": "Health check",
            "GET /": "API information"
        },
        "features": [
            "Automatic URL extraction from Gmail messages",
            "Safe URL processing with domain validation",
            "Tool chaining between Gmail and web access tools",
            "Injection-safe URL handling"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
