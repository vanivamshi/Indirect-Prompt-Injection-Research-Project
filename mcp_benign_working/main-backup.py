#!/usr/bin/env python3
"""
MCP Integration Project - Interactive Chat Mode
This file provides the complete interactive chat functionality with MCP tools.
"""

import os
import asyncio
import signal
import sys
import re
import json
import argparse
import html
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the MCP client
from mcp_client import MCPClient

# Import the new image processing functionality
from image_processor import (
    ImageProcessingResult, 
    extract_images_from_text, 
    process_image_with_google_search,
    process_gmail_with_image_and_url_chaining
)

class IntelligentChatBot:
    def __init__(self):
        self.mcp_client = MCPClient()
    
    async def connect(self):
        """Connect to MCP servers"""
        await self.mcp_client.connect_to_servers()
        
        # Add Wikipedia and web access servers to the list
        if not hasattr(self.mcp_client, 'servers'):
            self.mcp_client.servers = {}
        
        # Initialize additional servers
        self.mcp_client.servers.update({
            "wikipedia": "api_only",
            "web_access": "api_only"
        })
    
    async def disconnect(self):
        """Disconnect from MCP servers"""
        await self.mcp_client.disconnect()
    
    def _generate_intelligent_response(self, user_input: str):
        """Generate intelligent responses for general questions"""
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ["name", "who are you", "what are you"]):
            return "Hello! I'm your AI assistant connected to external applications through MCP (Model Context Protocol) servers. I can help you search the web, send Slack messages, find locations, check your calendar, manage Gmail, and have general conversations. What would you like to do?"
        
        elif any(word in input_lower for word in ["date", "time", "today", "when"]):
            current_time = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
            return f"Today is {current_time}. How can I help you today?"
        
        elif any(word in input_lower for word in ["hello", "hi", "hey", "greetings"]):
            return "Hello! I'm here to help you with various tasks using MCP tools. You can ask me to search for information, send messages, find locations, check your calendar, manage emails, or just chat!"
        
        elif any(word in input_lower for word in ["help", "what can you do", "capabilities"]):
            return """I can help you with several things:

🔍 **Search & Information**: "Search for AI news", "Find information about Python"
💬 **Slack Messaging**: "Send a message to Slack about the weather"
🗺️ **Location Services**: "Find the location of Times Square"
📅 **Google Calendar**: "Show my calendar events", "Check my schedule"
📧 **Gmail**: "Check my inbox", "Send an email about the meeting"
📧 **Email Summarization**: "Summarize my emails and send to user@gmail.com"
🖼️ **Image Processing**: "Read my 1st email and process image", "Extract images from emails"
💾 **Google Drive**: "Search for files", "Retrieve a file"
📄 **File Content Reading**: "Read file content and process instructions"
🌐 **URL Processing**: "Check this website: https://example.com"
📚 **Wikipedia Access**: "Get Wikipedia page about Python"
🌍 **Web Scraping**: "Access content from any website"
💭 **General Chat**: Ask me questions, get the date/time, or just chat!

**🆕 NEW: Image Processing Features:**
• Automatically extract images (including QR codes) from emails
• Process images through Google search for analysis
• Visit websites found in email bodies
• Safe URL and image validation
• Tool chaining: Gmail → Images/URLs → Google Search → Web Access

**🆕 NEW: File Content & Instruction Processing:**
• Read content from Google Drive files (docx, pdf, txt, etc.)
• Extract instructions and actionable items from file content
• Automatically process instructions using available MCP tools
• Categorize instructions (file operations, communication, calendar, data processing)
• Execute instructions like sending emails, creating calendar events, searching

**Example Commands:**
• "Search for files in Google Drive and read content"
• "Find file named 'instructions.docx' and process instructions"
• "Read the content of my LoR Example.docx file"

What would you like to do?"""
        
        elif any(word in input_lower for word in ["capital", "country", "india"]):
            return "The capital of India is New Delhi. India is the world's largest democracy and has a rich cultural heritage spanning thousands of years."
        
        elif any(word in input_lower for word in ["weather", "temperature", "forecast"]):
            return "I can't check real-time weather, but I can help you search for weather information! Try saying 'Search for weather in New York'."
        
        elif any(word in input_lower for word in ["thank", "thanks", "appreciate"]):
            return "You're welcome! 😊 I'm happy to help. Is there anything else you'd like me to do?"
        
        elif any(word in input_lower for word in ["python", "programming", "code"]):
            return "Python is a high-level, interpreted programming language known for its simplicity and readability. It's great for beginners and widely used in data science, web development, AI, and automation. What would you like to know about Python?"
        
        elif any(word in input_lower for word in ["ai", "artificial intelligence", "machine learning"]):
            return "Artificial Intelligence (AI) is technology that enables computers to perform tasks that typically require human intelligence. This includes machine learning, natural language processing, computer vision, and more. AI is transforming industries from healthcare to transportation."
        
        else:
            return f"I understand you're asking about: '{user_input}'\n\nI'm an AI assistant that can help with general knowledge, answer questions, and provide information on various topics. I can also use MCP tools to interact with external services like Gmail, Google Calendar, and search engines.\n\n💡 **Tip**: If you'd like detailed, current information about this topic, I can search the web for you! Just ask me to search for more details about '{user_input}'."
    
    async def _extractAnd_access_urls_from_emails(self, messages, max_urls=3):
        """Extract URLs and images from Gmail messages and fetch their content safely using enhanced security"""
        from utils import extract_urls_from_text, process_urls_safely
        
        # Extract URLs and images from all messages
        all_urls = []
        all_images = []
        
        for msg in messages:
            body = msg.get("body", "") or msg.get("snippet", "")
            urls = extract_urls_from_text(body)
            all_urls.extend(urls)
            
            # Extract images using the new image processor
            images = extract_images_from_text(body)
            all_images.extend(images)
        
        # Remove duplicates while preserving order
        unique_urls = list(dict.fromkeys(all_urls))
        unique_images = list(dict.fromkeys(all_images))
        
        # Process URLs safely using the utility functions
        url_results = []
        if unique_urls:
            url_results = await process_urls_safely(unique_urls, self.mcp_client, max_urls)
        
        # Process images with Google search
        image_results = []
        if unique_images:
            print(f"🖼️ Found {len(unique_images)} images to process")
            for img_url in unique_images[:max_urls]:  # Limit to max_urls
                try:
                    result = await process_image_with_google_search(self.mcp_client, img_url, "gmail")
                    image_results.append(result)
                    print(f"✅ Processed image: {img_url}")
                except Exception as e:
                    print(f"❌ Failed to process image {img_url}: {e}")
                    image_results.append(ImageProcessingResult(
                        image_url=img_url,
                        source_email="gmail",
                        google_search_results=[],
                        web_content={"error": str(e)},
                        processing_time=0.0,
                        is_safe=False
                    ))
        
        # Return both URL and image results
        return {
            "urls": url_results,
            "images": image_results,
            "total_urls": len(unique_urls),
            "total_images": len(unique_images)
        }

    async def _wikipedia_get_page(self, title: str, url: str = None):
        """Get Wikipedia page content"""
        try:
            import httpx
            from bs4 import BeautifulSoup
            
            # If URL provided, use it directly
            if url:
                target_url = url
            else:
                # Construct Wikipedia URL from title
                formatted_title = title.replace(' ', '_')
                target_url = f"https://en.wikipedia.org/wiki/{formatted_title}"
            
            print(f"🔍 Accessing Wikipedia page: {target_url}")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(target_url)
                
                if response.status_code == 200:
                    # Parse HTML content
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract main content
                    content_div = soup.find('div', {'id': 'mw-content-text'})
                    if content_div:
                        # Remove unwanted elements
                        for element in content_div.find_all(['script', 'style', 'sup', 'table']):
                            element.decompose()
                        
                        # Get text content
                        content = content_div.get_text()
                        
                        # Clean up the content
                        content = re.sub(r'\n+', '\n', content)
                        content = re.sub(r'\s+', ' ', content)
                        
                        # Extract key sections
                        sections = {}
                        
                        # Get introduction (first few paragraphs)
                        paragraphs = content.split('\n')
                        intro = ' '.join([p.strip() for p in paragraphs[:5] if p.strip() and len(p.strip()) > 50])
                        sections['introduction'] = intro[:500] + "..." if len(intro) > 500 else intro
                        
                        return {
                            "success": True,
                            "title": title,
                            "url": target_url,
                            "content": sections,
                            "full_content_length": len(content)
                        }
                    else:
                        return {"success": False, "error": "Could not find main content"}
                else:
                    return {"success": False, "error": f"HTTP {response.status_code}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _web_access_get_content(self, url: str):
        """Get content from any website"""
        try:
            import httpx
            from bs4 import BeautifulSoup
            
            print(f"🔍 Accessing website: {url}")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    # Parse HTML content
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Remove unwanted elements
                    for element in soup.find_all(['script', 'style', 'nav', 'header', 'footer']):
                        element.decompose()
                    
                    # Get text content
                    content = soup.get_text()
                    
                    # Clean up the content
                    content = re.sub(r'\n+', '\n', content)
                    content = re.sub(r'\s+', ' ', content)
                    
                    # Extract key information
                    title = soup.find('title')
                    title_text = title.get_text() if title else "No title found"
                    
                    # Get main content (first 1000 characters)
                    main_content = content[:1000] + "..." if len(content) > 1000 else content
                    
                    return {
                        "success": True,
                        "url": url,
                        "title": title_text,
                        "content": main_content,
                        "full_content_length": len(content)
                    }
                else:
                    return {"success": False, "error": f"HTTP {response.status_code}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def process_message(self, user_input: str):
        """Process user message and determine appropriate MCP tools to use"""
        input_lower = user_input.lower()
        tools_to_use = []
        
        # Drive detection - improved logic (check this FIRST to avoid conflicts)
        if any(word in input_lower for word in ["drive", "file", "search", "retrieve"]) and not any(word in input_lower for word in ["web", "internet", "news", "weather"]):
            # Extract a more meaningful search query
            if "search for files" in input_lower:
                # If user says "search for files", search for common file types
                search_query = "document OR pdf OR image OR video"
            elif "search" in input_lower and "drive" in input_lower:
                # Extract the actual search term after "search"
                parts = user_input.lower().split("search")
                if len(parts) > 1:
                    search_term = parts[1].replace("in google drive", "").replace("drive", "").replace("for", "").replace("query:", "").strip()
                    if search_term:
                        search_query = search_term
                    else:
                        search_query = "document OR pdf OR image"
                else:
                    search_query = "document OR pdf OR image"
            elif any(word in input_lower for word in ["named", "called", "file named", "file called", "read", "access", "open", "view"]):
                # Extract file name from phrases like "file named X" or "file called Y" or "read X"
                if "file named" in input_lower:
                    search_query = user_input.lower().split("file named")[-1].strip()
                elif "file called" in input_lower:
                    search_query = user_input.lower().split("file called")[-1].strip()
                elif "named" in input_lower:
                    search_query = user_input.lower().split("named")[-1].strip()
                elif "called" in input_lower:
                    search_query = user_input.lower().split("called")[-1].strip()
                elif "read" in input_lower:
                    # Extract filename after "read"
                    parts = user_input.lower().split("read")
                    if len(parts) > 1:
                        search_query = parts[1].strip()
                    else:
                        search_query = "document OR pdf OR image"
                elif "access" in input_lower:
                    # Extract filename after "access"
                    parts = user_input.lower().split("access")
                    if len(parts) > 1:
                        search_query = parts[1].strip()
                    else:
                        search_query = "document OR pdf OR image"
                else:
                    search_query = "document OR pdf OR image"
                
                # Clean up the search query - remove common words and extra text
                search_query = search_query.replace("in drive", "").replace("in google drive", "").replace("query:", "").replace("and summarize", "").replace("and process", "").strip()
                # Remove quotes if present
                search_query = search_query.strip('"').strip("'")
                # Remove any remaining common words
                common_words = ["for", "file", "named", "called", "search", "find", "look", "get", "the", "content", "of", "my"]
                for word in common_words:
                    search_query = search_query.replace(word, "").strip()
                # If the query is too long or contains too many words, try to extract just the filename
                if len(search_query.split()) > 3:
                    # Try to find the most likely filename (usually the last meaningful word/phrase)
                    words = search_query.split()
                    # Look for common file extensions or patterns
                    for i, word in enumerate(words):
                        if any(ext in word.lower() for ext in ['.pdf', '.doc', '.docx', '.xlsx', '.pptx', '.txt']):
                            search_query = word
                            break
                    else:
                        # If no extension found, use the last few words
                        search_query = " ".join(words[-2:]) if len(words) > 1 else words[-1]
            else:
                # Use the original input but clean it up
                search_query = user_input.replace("search for files in google drive", "").replace("drive", "").strip()
                if not search_query:
                    search_query = "document OR pdf OR image"
            
            # Final cleanup and validation
            search_query = search_query.strip()
            if not search_query:
                search_query = "document OR pdf OR image"
            
            tools_to_use.append(("drive", "search", {"query": search_query}))
            print(f"🔍 Drive search query: {search_query}")
            print(f"🔍 Original input: {user_input}")
            
            # If searching for a specific filename, also try alternative search strategies
            if any(word in input_lower for word in ["named", "called", "file named", "file called"]) or "example" in search_query.lower():
                # Try searching with quotes for exact match
                if not search_query.startswith('"') and not search_query.endswith('"'):
                    tools_to_use.append(("drive", "search", {"query": f'"{search_query}"'}))
                    print(f"🔍 Alternative search (exact match): \"{search_query}\"")
                
                # Try searching for just the main part of the filename (without extension)
                if '.' in search_query:
                    base_name = search_query.split('.')[0]
                    tools_to_use.append(("drive", "search", {"query": base_name}))
                    print(f"🔍 Alternative search (base name): {base_name}")
                
                # Try searching for individual words
                words = search_query.split()
                if len(words) > 1:
                    for word in words:
                        if len(word) > 2:  # Only search for meaningful words
                            tools_to_use.append(("drive", "search", {"query": word}))
                            print(f"🔍 Alternative search (word): {word}")
                
                # Try searching for common variations
                variations = [
                    search_query.replace(" ", "_"),
                    search_query.replace(" ", "-"),
                    search_query.replace(" ", ""),
                    search_query.upper(),
                    search_query.lower()
                ]
                for variation in variations:
                    if variation != search_query:
                        tools_to_use.append(("drive", "search", {"query": variation}))
                        print(f"🔍 Alternative search (variation): {variation}")
            
            # Check if user wants to read file content and process instructions
            if any(word in input_lower for word in ["read", "content", "instructions", "process", "open", "view"]):
                print(f"📄 Detected file content reading request")
                # This will be handled after the search results are returned
        
        # Enhanced search detection - catch more types of queries (after drive check)
        elif any(word in input_lower for word in ["search", "find", "google", "look up", "what is", "how to", "weather", "news", "information about", "tell me about"]):
            tools_to_use.append(("google", "search", {"query": user_input}))
            print(f"🔍 Detected search query: {user_input}")
        
        elif any(word in input_lower for word in ["capital of", "population of", "temperature", "forecast", "definition of", "meaning of", "who is", "where is"]):
            tools_to_use.append(("google", "search", {"query": user_input}))
            print(f"🔍 Detected information query: {user_input}")
        
        elif "weather" in input_lower or "temperature" in input_lower or "forecast" in input_lower:
            tools_to_use.append(("google", "search", {"query": f"weather {user_input}"}))
            print(f"🔍 Detected weather query: {user_input}")
        
        # Slack detection - Only if explicitly mentioned, not for email commands
        if any(word in input_lower for word in ["slack", "slack message", "slack channel"]) and not any(word in input_lower for word in ["gmail", "email", "mail"]):
            tools_to_use.append(("slack", "send_message", {"channel": "#general", "text": user_input}))
            print(f"💬 Detected Slack command: {user_input}")
        
        # Location detection
        if any(word in input_lower for word in ["location", "map", "address", "where"]):
            tools_to_use.append(("maps", "geocode", {"address": user_input}))
        
        # Enhanced calendar detection
        if any(word in input_lower for word in ["calendar", "calender", "events", "schedule", "meeting", "event", "appointment"]):
            if any(word in input_lower for word in ["create", "add", "new", "make", "set up", "set up an", "setup"]):
                # Extract time information for event creation
                from datetime import datetime, timedelta
                now = datetime.now()
                
                # Parse time from the message
                start_time = now.replace(hour=15, minute=0, second=0, microsecond=0)  # Default 3 PM
                
                # Look for specific time patterns - improved regex
                #import re
                time_pattern = r'(\d{1,2}):?(\d{2})\s*(am|pm|AM|PM)?'
                time_match = re.search(time_pattern, input_lower)
                
                if time_match:
                    hour = int(time_match.group(1))
                    minute = int(time_match.group(2))
                    ampm = time_match.group(3) if time_match.group(3) else ""
                    
                    # Convert to 24-hour format
                    if ampm.lower() == "pm" and hour != 12:
                        hour += 12
                    elif ampm.lower() == "am" and hour == 12:
                        hour = 0
                    
                    start_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    print(f"🔍 Debug: Parsed time - {hour}:{minute} {ampm} -> {start_time}")
                
                # Look for duration
                duration_minutes = 10  # Default 10 minutes
                duration_match = re.search(r'(\d+)\s*(min|minute|minutes)', input_lower)
                if duration_match:
                    duration_minutes = int(duration_match.group(1))
                    print(f"🔍 Debug: Parsed duration - {duration_minutes} minutes")
                
                end_time = start_time + timedelta(minutes=duration_minutes)
                
                # Extract event name - improved extraction
                event_name = "Test Event"
                if "name it as" in input_lower:
                    event_name = input_lower.split("name it as")[-1].strip().strip('"').strip("'")
                elif "name it" in input_lower:
                    event_name = input_lower.split("name it")[-1].strip().strip('"').strip("'")
                elif "called" in input_lower:
                    event_name = input_lower.split("called")[-1].strip().strip('"').strip("'")
                
                print(f"🔍 Debug: Event name extracted: '{event_name}'")
                print(f"🔍 Debug: Start time: {start_time}")
                print(f"🔍 Debug: End time: {end_time}")
                
                # Format for Google Calendar API
                start_iso = start_time.isoformat() + "Z"
                end_iso = end_time.isoformat() + "Z"
                
                tools_to_use.append(("calendar", "create_event", {
                    "summary": event_name,
                    "start_time": start_iso,
                    "end_time": end_iso,
                    "description": f"Event created via MCP integration: {event_name}"
                }))
                print(f"🔍 Debug: Added calendar.create_event to tools_to_use")
            else:
                tools_to_use.append(("calendar", "get_events", {"max_results": 10}))
                print(f"🔍 Debug: Added calendar.get_events to tools_to_use")
        
        # Gmail detection - Enhanced with better pattern matching
        if any(word in input_lower for word in ["gmail", "email", "mail", "inbox", "emails", "messages"]):
            print(f"🔍 Detected email-related query: {user_input}")
            
            if any(word in input_lower for word in ["summarize", "summary", "summarise"]):
                # Extract email address if provided
                email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', user_input)
                if email_match:
                    target_email = email_match.group(0)
                    print(f"📧 Extracted target email: {target_email}")
                    tools_to_use.append(("gmail", "summarize_and_send", {"target_email": target_email, "max_emails": 10}))
                else:
                    print(f"📧 No email address found, using default")
                    tools_to_use.append(("gmail", "summarize_and_send", {"target_email": "user@example.com", "max_emails": 10}))
            
            elif any(word in input_lower for word in ["send", "compose", "write", "create"]):
                print(f"📧 Detected email send command")
                tools_to_use.append(("gmail", "send_message", {"to": "example@email.com", "subject": "Test Email", "body": user_input}))
            
            elif any(word in input_lower for word in ["check", "view", "read", "show", "get", "fetch", "list"]):
                print(f"📧 Detected email read command - using tool chaining")
                # Use the new tool chaining method for Gmail read operations
                return await self.process_message_with_tool_chaining(user_input, max_urls=5, enable_tool_chaining=True)
            
            else:
                # Default to reading emails if no specific action detected
                print(f"📧 Default email action: reading messages - using tool chaining")
                # Use the new tool chaining method for Gmail read operations
                return await self.process_message_with_tool_chaining(user_input, max_urls=5, enable_tool_chaining=True)
        
        # URL detection with enhanced security
        from utils import extract_urls_from_text, process_urls_safely
        url_matches = extract_urls_from_text(user_input)
        
        if url_matches:
            print(f"🔗 Found {len(url_matches)} URLs in user input")
            # URLs will be processed automatically in the tool execution loop
            for url in url_matches:
                if "wikipedia.org" in url.lower():
                    page_title = url.split('/')[-1].replace('_', ' ')
                    tools_to_use.append(("wikipedia", "get_page", {"title": page_title, "url": url}))
                else:
                    tools_to_use.append(("web_access", "get_content", {"url": url}))
        
        # Reference/website detection
        if any(word in input_lower for word in ["reference", "access", "website", "page", "article"]) and any(word in input_lower for word in ["wikipedia", "wiki", "site", "url"]):
            if not url_matches:
                tools_to_use.append(("google", "search", {"query": user_input}))
        
        # Execute MCP tools
        results = []
        print(f"🔍 Executing {len(tools_to_use)} tools: {[(s, t) for s, t, p in tools_to_use]}")
        
        # Track if we need to process file content and instructions
        should_process_file_content = any(word in input_lower for word in ["read", "content", "instructions", "process", "open", "view"])
        file_content_processed = False
        
        for server_name, tool_name, params in tools_to_use:
            try:
                print(f"🔧 Calling tool: {server_name}.{tool_name} with params: {params}")
                
                if server_name == "wikipedia":
                    result = await self._wikipedia_get_page(params.get("title", ""), params.get("url"))
                elif server_name == "web_access":
                    result = await self._web_access_get_content(params.get("url", ""))
                else:
                    result = await self.mcp_client.call_tool(server_name, tool_name, params)
                
                print(f"✅ Tool call successful: {server_name}.{tool_name}")
                
                if server_name == "google" and tool_name == "search":
                    formatted_result = self._format_google_search_results(result)
                    results.append(f"✅ {server_name}.{tool_name}: {formatted_result}")
                
                # Special handling for Gmail messages with URL extraction
                elif server_name == "gmail" and tool_name == "get_messages":
                    results.append(f"✅ gmail.get_messages: {result}")
                    # Note: URL extraction is now handled by process_message_with_tool_chaining
                    # This section is kept for backward compatibility
                
                # Special handling for Drive search with file content reading
                elif server_name == "drive" and tool_name == "search":
                    results.append(f"✅ {server_name}.{tool_name}: {result}")
                    
                    # If user wants to read file content and we found files
                    if should_process_file_content and not file_content_processed and result and isinstance(result, dict):
                        files = result.get("files", [])
                        if files:
                            print(f"📄 Found {len(files)} files, processing content and instructions...")
                            
                            # Process the first file (or files if multiple)
                            for i, file_info in enumerate(files[:3]):  # Limit to first 3 files
                                file_id = file_info.get("id")
                                file_name = file_info.get("name", "Unknown")
                                mime_type = file_info.get("mimeType", "Unknown")
                                
                                if file_id:
                                    print(f"📄 Processing file {i+1}: {file_name}")
                                    
                                    # Read file content
                                    content_result = await self._read_file_content(file_id, file_name, mime_type)
                                    
                                    if content_result.get("success"):
                                        content = content_result.get("content", "")
                                        
                                        # Extract instructions from content
                                        instructions = self._extract_instructions_from_text(content)
                                        
                                        # Process instructions
                                        processed_instructions = await self._process_instructions(instructions, file_name)
                                        
                                        # Add results to response
                                        results.append(f"\n📄 **File Content Analysis: {file_name}**")
                                        results.append(f"   📊 Content Length: {len(content)} characters")
                                        
                                        # Show instruction summary
                                        total_instructions = sum(len(cat) for cat in instructions.values())
                                        if total_instructions > 0:
                                            results.append(f"   🔧 Instructions Found: {total_instructions}")
                                            for category, instruction_list in instructions.items():
                                                if instruction_list:
                                                    results.append(f"      - {category.title()}: {len(instruction_list)} items")
                                            
                                            # Show processed instruction results
                                            results.append(f"   ⚡ **Instruction Processing Results:**")
                                            for proc_inst in processed_instructions:
                                                if proc_inst["success"]:
                                                    results.append(f"      ✅ {proc_inst['instruction'][:100]}...")
                                                    if proc_inst["result"].get("action"):
                                                        results.append(f"         Action: {proc_inst['result']['action']}")
                                                else:
                                                    results.append(f"      ❌ {proc_inst['instruction'][:100]}...")
                                                    if proc_inst["result"].get("error"):
                                                        results.append(f"         Error: {proc_inst['result']['error']}")
                                        else:
                                            results.append(f"   ℹ️ No specific instructions found in file content")
                                        
                                        # Show content preview
                                        content_preview = content[:300] + "..." if len(content) > 300 else content
                                        results.append(f"   📝 Content Preview: {content_preview}")
                                        
                                        file_content_processed = True
                                    else:
                                        results.append(f"   ❌ Failed to read file content: {content_result.get('error', 'Unknown error')}")
                                
                                if file_content_processed:
                                    break  # Only process one file for now
                        else:
                            results.append(f"   ℹ️ No files found to process content from")
                
                else:
                    results.append(f"✅ {server_name}.{tool_name}: {result}")
            
            except Exception as error:
                print(f"❌ Tool call failed: {server_name}.{tool_name} - {error}")
                results.append(f"❌ {server_name}.{tool_name}: {error}")
        
        if not tools_to_use:
            try:
                print("🔍 No tools detected, using Google search as fallback")
                search_result = await self.mcp_client.call_tool("google", "search", {"query": user_input})
                formatted_result = self._format_google_search_results(search_result)
                results.append(f"✅ google.search (fallback): {formatted_result}")
                tools_to_use.append(("google", "search", {"query": user_input}))
            except Exception as error:
                results.append(f"❌ google.search (fallback): {error}")
        
        if results:
            response = f"I've processed your request using MCP tools:\n\n" + "\n".join(results)
        else:
            response = self._generate_intelligent_response(user_input)
        
        return response

    def _clean_html_text(self, html_text: str) -> str:
        """Remove HTML tags and decode HTML entities"""
        if not html_text:
            return ""
        
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', html_text)
        
        # Decode HTML entities (like &amp;, &lt;, etc.)
        clean_text = html.unescape(clean_text)
        
        # Clean up extra whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        return clean_text

    def _clean_google_search_item(self, item: dict) -> dict:
        """Clean HTML tags and format Google search result item"""
        # Extract and clean title
        title = item.get("title", "")
        html_title = item.get("htmlTitle", "")
        
        # Use htmlTitle if available, otherwise use title
        if html_title:
            # Remove HTML tags and decode HTML entities
            clean_title = self._clean_html_text(html_title)
        else:
            clean_title = title
        
        # Extract and clean snippet
        snippet = item.get("snippet", "")
        html_snippet = item.get("htmlSnippet", "")
        
        # Use htmlSnippet if available, otherwise use snippet
        if html_snippet:
            clean_snippet = self._clean_html_text(html_snippet)
        else:
            clean_snippet = snippet
        
        # Clean link
        link = item.get("link", "")
        
        # Create a formatted description
        formatted_description = f"{clean_title}\n\n{clean_snippet}\n\nSource: {link}"
        
        return {
            "title": clean_title,
            "snippet": clean_snippet,
            "link": link,
            "formatted_description": formatted_description,
            "original_item": item  # Keep original for debugging if needed
        }

    def _format_google_search_results(self, search_result: dict) -> str:
        """Format Google search results into clean, readable paragraphs"""
        if not search_result or "items" not in search_result:
            return "No search results found."
        
        items = search_result.get("items", [])
        total_results = search_result.get("totalResults", 0)
        
        if not items:
            return "No search results found."
        
        # Format the results as clean paragraphs
        formatted_results = []
        formatted_results.append(f"Found {total_results} results for your search:\n")
        
        for i, item in enumerate(items[:5], 1):  # Limit to top 5 results
            # Clean the item if it's not already cleaned
            if "formatted_description" not in item:
                cleaned_item = self._clean_google_search_item(item)
                title = cleaned_item.get("title", "No title")
                snippet = cleaned_item.get("snippet", "No description")
                link = cleaned_item.get("link", "")
            else:
                title = item.get("title", "No title")
                snippet = item.get("snippet", "No description")
                link = item.get("link", "")
            
            # Format each result as a clean paragraph
            result_text = f"{i}. {title}\n\n{snippet}\n\nSource: {link}"
            formatted_results.append(result_text)
            
            # Add separator between results
            if i < min(5, len(items)):
                formatted_results.append("-" * 50)
        
        return "\n".join(formatted_results)

    def _create_email_summary(self, email_contents: list) -> str:
        """Create a summary of email contents with intelligent highlights"""
        summary_lines = [
            f"📧 EMAIL SUMMARY - {len(email_contents)} RECENT MESSAGES",
            "=" * 50,
            ""
        ]
        
        # Process each email and create highlights
        for i, email in enumerate(email_contents, 1):
            subject = email.get('subject', 'No Subject')
            sender = email.get('from', 'Unknown Sender')
            body = email.get('body', '')
            snippet = email.get('snippet', '')
            
            summary_lines.extend([
                f"{i}. SUBJECT: {subject}",
                f"   FROM: {sender}",
                ""
            ])
            
            # Process email content and create highlights
            if body:
                highlights = self._extract_highlights_from_content(body)
                if highlights:
                    summary_lines.extend([
                        f"   📝 HIGHLIGHTS: {highlights}",
                        ""
                    ])
                else:
                    # Fallback to snippet if no highlights extracted
                    summary_lines.extend([
                        f"   📝 CONTENT: {snippet[:200]}...",
                        ""
                    ])
            else:
                # Use snippet if no body content
                summary_lines.extend([
                    f"   📝 SNIPPET: {snippet[:200]}...",
                    ""
                ])
        
        summary_lines.extend([
            "=" * 50,
            f"Total emails processed: {len(email_contents)}",
            f"Summary generated at: {datetime.now()}"
        ])
        
        return "\n".join(summary_lines)
    
    def _extract_highlights_from_content(self, content: str):
        """Extract key highlights from email content and format as a paragraph"""
        if not content:
            return ""
        
        # Clean the content
        content = re.sub(r'<[^>]+>', '', content)
        content = re.sub(r'\s+', ' ', content).strip()
        content = re.sub(r'--\s*\n.*', '', content, flags=re.DOTALL)
        
        # Extract key information using patterns
        highlights = []
        
        # Look for action items
        action_patterns = [
            r'please\s+([^.]+)',
            r'need\s+([^.]+)',
            r'request\s+([^.]+)',
            r'urgent\s+([^.]+)',
            r'deadline\s+([^.]+)',
            r'meeting\s+([^.]+)',
            r'call\s+([^.]+)',
            r'email\s+([^.]+)',
            r'update\s+([^.]+)',
            r'confirm\s+([^.]+)'
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) > 10:
                    highlights.append(f"Action required: {match.strip()}")
        
        # Look for important dates/times
        date_patterns = [
            r'\b(today|tomorrow|next week|this week|this month)\b',
            r'\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?\b',
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}\b'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if match not in highlights:
                    highlights.append(f"Timeline: {match}")
        
        # Look for key topics/themes
        topic_patterns = [
            r'\b(project|meeting|report|budget|client|team|update|status)\b',
            r'\b(issue|problem|solution|plan|strategy|goal|target)\b',
            r'\b(approval|review|feedback|decision|agreement|contract)\b'
        ]
        
        for pattern in topic_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if match not in highlights:
                    highlights.append(f"Topic: {match.title()}")
        
        # If we found specific highlights, format them as a paragraph
        if highlights:
            unique_highlights = list(dict.fromkeys(highlights))[:5]
            return " ".join(unique_highlights) + "."
        
        # If no specific highlights found, create a summary from the content
        sentences = re.split(r'[.!?]+', content)
        meaningful_sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        if meaningful_sentences:
            summary_sentences = meaningful_sentences[:3]
            return " ".join(summary_sentences) + "."
        
        # Fallback: return first 150 characters as a highlight
        return content[:150] + "..." if len(content) > 150 else content

    async def _read_file_content(self, file_id: str, file_name: str, mime_type: str):
        """Read content from a Google Drive file and extract text"""
        try:
            print(f"📄 Reading file content: {file_name} (ID: {file_id})")
            print(f"📄 File type: {mime_type}")
            
            # Use the drive retrieve tool to get file content
            result = await self.mcp_client.call_tool("drive", "retrieve", {"file_id": file_id})
            
            if result and isinstance(result, dict):
                if result.get("success"):
                    content = result.get("content", "")
                    if content:
                        print(f"✅ Successfully read file content, length: {len(content)} characters")
                        return {
                            "success": True,
                            "content": content,
                            "file_name": file_name,
                            "file_id": file_id,
                            "mime_type": mime_type
                        }
                    else:
                        print(f"⚠️ File content is empty")
                        return {
                            "success": False,
                            "error": "File content is empty",
                            "file_name": file_name,
                            "file_id": file_id
                        }
                else:
                    print(f"❌ Failed to read file: {result.get('error', 'Unknown error')}")
                    return {
                        "success": False,
                        "error": result.get("error", "Unknown error"),
                        "file_name": file_name,
                        "file_id": file_id
                    }
            else:
                print(f"❌ Invalid response from drive retrieve: {result}")
                return {
                    "success": False,
                    "error": "Invalid response from drive retrieve",
                    "file_name": file_name,
                    "file_id": file_id
                }
                
        except Exception as e:
            print(f"❌ Exception reading file content: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_name": file_name,
                "file_id": file_id
            }

    def _extract_instructions_from_text(self, text: str):
        """Extract instructions and actionable items from text content"""
        if not text:
            return []
        
        instructions = []
        
        # Clean the text
        text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
        text = re.sub(r'\s+', ' ', text).strip()  # Normalize whitespace
        
        # Instruction patterns - look for various forms of instructions
        instruction_patterns = [
            # Direct instructions
            r'(?:please|kindly|can you|could you|would you)\s+([^.]+)',
            r'(?:you should|you need to|you must|you have to)\s+([^.]+)',
            r'(?:next steps?|action items?|to do|tasks?)\s*:?\s*([^.]+)',
            r'(?:instructions?|directions?|guidelines?)\s*:?\s*([^.]+)',
            
            # Action verbs
            r'(?:send|email|call|contact|schedule|create|make|do|complete|finish|submit|upload|download|save|delete|update|modify|change|edit|review|approve|reject|accept|decline)\s+([^.]+)',
            
            # Time-sensitive actions
            r'(?:urgent|asap|immediately|today|tomorrow|this week|by [^.]*)\s+([^.]+)',
            
            # File operations
            r'(?:save as|download|upload|attach|send the file|open the file|read the file)\s+([^.]+)',
            
            # Communication actions
            r'(?:reply to|respond to|notify|inform|tell|ask|request)\s+([^.]+)',
            
            # Meeting/calendar actions
            r'(?:schedule|book|arrange|set up|create a meeting|add to calendar)\s+([^.]+)',
            
            # Data processing actions
            r'(?:analyze|calculate|compare|review|check|verify|validate|process|format|organize)\s+([^.]+)'
        ]
        
        for pattern in instruction_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                instruction = match.strip()
                if len(instruction) > 10 and len(instruction) < 200:  # Reasonable length
                    instructions.append(instruction)
        
        # Remove duplicates while preserving order
        unique_instructions = list(dict.fromkeys(instructions))
        
        # Categorize instructions by type
        categorized_instructions = {
            "file_operations": [],
            "communication": [],
            "calendar": [],
            "data_processing": [],
            "general": []
        }
        
        for instruction in unique_instructions:
            instruction_lower = instruction.lower()
            
            if any(word in instruction_lower for word in ["file", "download", "upload", "save", "attach", "open", "read"]):
                categorized_instructions["file_operations"].append(instruction)
            elif any(word in instruction_lower for word in ["email", "send", "reply", "contact", "call", "notify", "inform"]):
                categorized_instructions["communication"].append(instruction)
            elif any(word in instruction_lower for word in ["schedule", "meeting", "calendar", "book", "arrange"]):
                categorized_instructions["calendar"].append(instruction)
            elif any(word in instruction_lower for word in ["analyze", "calculate", "review", "check", "process", "format"]):
                categorized_instructions["data_processing"].append(instruction)
            else:
                categorized_instructions["general"].append(instruction)
        
        return categorized_instructions

    async def _process_instructions(self, instructions: dict, file_name: str):
        """Process extracted instructions and execute them using available MCP tools"""
        processed_instructions = []
        
        print(f"🔧 Processing {sum(len(cat) for cat in instructions.values())} instructions from {file_name}")
        
        for category, instruction_list in instructions.items():
            if not instruction_list:
                continue
                
            print(f"📋 Processing {category} instructions: {len(instruction_list)} items")
            
            for instruction in instruction_list:
                print(f"   🔧 Instruction: {instruction}")
                
                try:
                    # Process based on category
                    if category == "file_operations":
                        result = await self._process_file_instruction(instruction)
                    elif category == "communication":
                        result = await self._process_communication_instruction(instruction)
                    elif category == "calendar":
                        result = await self._process_calendar_instruction(instruction)
                    elif category == "data_processing":
                        result = await self._process_data_instruction(instruction)
                    else:
                        result = await self._process_general_instruction(instruction)
                    
                    processed_instructions.append({
                        "instruction": instruction,
                        "category": category,
                        "result": result,
                        "success": result.get("success", False)
                    })
                    
                except Exception as e:
                    print(f"   ❌ Error processing instruction: {e}")
                    processed_instructions.append({
                        "instruction": instruction,
                        "category": category,
                        "result": {"error": str(e)},
                        "success": False
                    })
        
        return processed_instructions

    async def _process_file_instruction(self, instruction: str):
        """Process file-related instructions"""
        instruction_lower = instruction.lower()
        
        if "search" in instruction_lower or "find" in instruction_lower:
            # Extract search terms
            search_terms = re.findall(r'(?:search for|find)\s+([^.]+)', instruction_lower)
            if search_terms:
                search_query = search_terms[0].strip()
                try:
                    result = await self.mcp_client.call_tool("drive", "search", {"query": search_query})
                    return {"success": True, "action": "search", "query": search_query, "result": result}
                except Exception as e:
                    return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "File instruction not recognized"}

    async def _process_communication_instruction(self, instruction: str):
        """Process communication-related instructions"""
        instruction_lower = instruction.lower()
        
        if "email" in instruction_lower or "send" in instruction_lower:
            # Extract email details
            email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', instruction)
            if email_match:
                email_address = email_match.group(1)
                # Extract subject and body from instruction
                subject = "Message from file instructions"
                body = instruction
                
                try:
                    result = await self.mcp_client.call_tool("gmail", "send_message", {
                        "to": email_address,
                        "subject": subject,
                        "body": body
                    })
                    return {"success": True, "action": "send_email", "to": email_address, "result": result}
                except Exception as e:
                    return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "Communication instruction not recognized"}

    async def _process_calendar_instruction(self, instruction: str):
        """Process calendar-related instructions"""
        instruction_lower = instruction.lower()
        
        if "meeting" in instruction_lower or "schedule" in instruction_lower:
            # Extract meeting details
            meeting_name = "Meeting from file instructions"
            if "about" in instruction_lower:
                meeting_name = instruction_lower.split("about")[-1].strip()
            
            # Default time (next hour)
            from datetime import datetime, timedelta
            now = datetime.now()
            start_time = now + timedelta(hours=1)
            end_time = start_time + timedelta(hours=1)
            
            try:
                result = await self.mcp_client.call_tool("calendar", "create_event", {
                    "summary": meeting_name,
                    "start_time": start_time.isoformat() + "Z",
                    "end_time": end_time.isoformat() + "Z",
                    "description": f"Event created from file instruction: {instruction}"
                })
                return {"success": True, "action": "create_event", "event_name": meeting_name, "result": result}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "Calendar instruction not recognized"}

    async def _process_data_instruction(self, instruction: str):
        """Process data processing instructions"""
        instruction_lower = instruction.lower()
        
        if "search" in instruction_lower or "look up" in instruction_lower:
            # Extract search terms
            search_terms = re.findall(r'(?:search for|look up|find information about)\s+([^.]+)', instruction_lower)
            if search_terms:
                search_query = search_terms[0].strip()
                try:
                    result = await self.mcp_client.call_tool("google", "search", {"query": search_query})
                    return {"success": True, "action": "search", "query": search_query, "result": result}
                except Exception as e:
                    return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "Data processing instruction not recognized"}

    async def _process_general_instruction(self, instruction: str):
        """Process general instructions"""
        # For now, just acknowledge the instruction
        return {
            "success": True,
            "action": "acknowledge",
            "message": f"Instruction noted: {instruction}",
            "note": "This instruction requires manual review"
        }

    async def process_message_with_tool_chaining(self, user_input: str, max_urls: int = 3, enable_tool_chaining: bool = True):
        """Process user message with enhanced tool chaining for Gmail and URL processing"""
        input_lower = user_input.lower()
        tool_results = []
        processed_urls = []
        
        print(f"🔗 Tool chaining enabled: {enable_tool_chaining}")
        print(f"🔗 Max URLs to process: {max_urls}")
        
        # Check if this is a Gmail-related request
        if any(word in input_lower for word in ["gmail", "email", "mail", "inbox", "emails", "messages"]):
            print(f"📧 Processing Gmail request: {user_input}")
            
            # Call Gmail tool
            if "get_messages" in input_lower or "check" in input_lower or "read" in input_lower:
                try:
                    gmail_result = await self.mcp_client.call_tool("gmail", "get_messages", {
                        "query": "",
                        "max_results": 5
                    })
                    tool_results.append({
                        "tool": "gmail.get_messages",
                        "result": gmail_result,
                        "success": True
                    })
                    print(f"✅ Gmail messages retrieved: {len(gmail_result.get('messages', []))} messages")
                    
                    # If tool chaining is enabled, automatically process URLs
                    if enable_tool_chaining and gmail_result.get("messages"):
                        print(f"🔗 Tool chaining enabled - processing URLs from {len(gmail_result['messages'])} messages")
                        
                        # Get the first message content to extract URLs
                        first_message_id = gmail_result["messages"][0]["id"]
                        print(f"📧 Reading content of first message: {first_message_id}")
                        
                        try:
                            # Get the actual message content
                            print(f"🔍 Calling gmail.get_message_content for message ID: {first_message_id}")
                            message_content = await self.mcp_client.call_tool("gmail", "get_message_content", {
                                "message_id": first_message_id
                            })
                            
                            print(f"🔍 Message content response: {type(message_content)}")
                            if message_content:
                                print(f"🔍 Message content keys: {list(message_content.keys()) if isinstance(message_content, dict) else 'Not a dict'}")
                            
                            if message_content and isinstance(message_content, dict) and message_content.get("body"):
                                print(f"✅ Retrieved message content, length: {len(message_content['body'])}")
                                
                                # Extract URLs from the message content
                                url_results = await self._extractAnd_access_urls_from_emails(
                                    [{"body": message_content["body"]}], 
                                    max_urls
                                )
                                processed_urls = url_results
                                
                                if url_results and isinstance(url_results, dict) and url_results.get("urls"):
                                    urls = url_results["urls"]
                                    print(f"🌐 Found and processed {len(urls)} URLs:")
                                    for url_result in urls:
                                        if isinstance(url_result, dict):
                                            print(f"   - {url_result.get('url', 'Unknown')} ({url_result.get('domain', 'Unknown')}) - {url_result.get('content_type', 'Unknown')}")
                                        else:
                                            print(f"   - {url_result}")
                                elif url_results and isinstance(url_results, list):
                                    print(f"🌐 Found and processed {len(url_results)} URLs:")
                                    for url_result in url_results:
                                        if isinstance(url_result, dict):
                                            print(f"   - {url_result.get('url', 'Unknown')} ({url_result.get('domain', 'Unknown')}) - {url_result.get('content_type', 'Unknown')}")
                                        else:
                                            print(f"   - {url_result}")
                                else:
                                    print("🌐 No URLs found in the first email message")
                            else:
                                print(f"⚠️ No message body content found. Response: {message_content}")
                                
                        except Exception as e:
                            print(f"❌ Failed to get message content: {e}")
                            print(f"❌ Exception type: {type(e)}")
                            import traceback
                            print(f"❌ Traceback: {traceback.format_exc()}")
                            processed_urls = []
                    
                except Exception as e:
                    print(f"❌ Gmail tool call failed: {e}")
                    tool_results.append({
                        "tool": "gmail.get_messages",
                        "result": {"error": str(e)},
                        "success": False
                    })
            
            elif "get_message_content" in input_lower or "read message" in input_lower:
                # Extract message ID if provided
                message_id_match = re.search(r'[a-f0-9]{16,}', user_input)
                if message_id_match:
                    message_id = message_id_match.group(0)
                    try:
                        gmail_result = await self.mcp_client.call_tool("gmail", "get_message_content", {
                            "message_id": message_id
                        })
                        tool_results.append({
                            "tool": "gmail.get_message_content",
                            "result": gmail_result,
                            "success": True
                        })
                        
                        # Process URLs from message content
                        if enable_tool_chaining and gmail_result.get("body"):
                            urls = await self._extractAnd_access_urls_from_emails(
                                [{"body": gmail_result["body"]}], 
                                max_urls
                            )
                            processed_urls = urls
                    except Exception as e:
                        print(f"❌ Gmail message content tool call failed: {e}")
                        tool_results.append({
                            "tool": "gmail.get_message_content",
                            "result": {"error": str(e)},
                            "success": False
                        })
                else:
                    tool_results.append({
                        "tool": "gmail.get_message_content",
                        "result": {"error": "No message ID provided"},
                        "success": False
                    })
        
        # Handle direct URL processing requests
        elif "http" in user_input:
            from utils import extract_urls_from_text
            urls = extract_urls_from_text(user_input)
            if urls:
                print(f"🌐 Processing {len(urls)} URLs from user input")
                url_results = await self._extractAnd_access_urls_from_emails(
                    [{"body": user_input}], 
                    max_urls
                )
                processed_urls = url_results
        
        # Handle other tool requests using the original method
        else:
            # Use the original process_message method for non-Gmail requests
            response = await self.process_message(user_input)
            return response
        
        # Prepare response with tool chaining results
        if tool_results:
            response_parts = []
            response_parts.append("I've processed your request using MCP tools with automatic tool chaining:")
            
            for tool_result in tool_results:
                if tool_result["success"]:
                    response_parts.append(f"✅ {tool_result['tool']}: Success")
                else:
                    response_parts.append(f"❌ {tool_result['tool']}: {tool_result['result'].get('error', 'Unknown error')}")
            
            if processed_urls:
                # Handle the new structure that includes both URLs and images
                if isinstance(processed_urls, dict) and "urls" in processed_urls:
                    # New structure with both URLs and images
                    url_results = processed_urls.get("urls", [])
                    image_results = processed_urls.get("images", [])
                    total_urls = processed_urls.get("total_urls", 0)
                    total_images = processed_urls.get("total_images", 0)
                    
                    if url_results:
                        response_parts.append(f"\n🌐 **URL Processing Results** ({len(url_results)} URLs processed):")
                        for url_result in url_results:
                            if isinstance(url_result, dict):
                                url = url_result.get('url', 'Unknown')
                                domain = url_result.get('domain', 'Unknown')
                                content_type = url_result.get('content_type', 'Unknown')
                                response_parts.append(f"   - {url}")
                                #response_parts.append(f"   - {url}")
                                response_parts.append(f"     Type: {content_type}")
                                
                                # Enhanced content summary and action handling
                                if url_result.get('content'):
                                    content = url_result['content']
                                    if isinstance(content, dict):
                                        if content.get('success'):
                                            response_parts.append(f"     Status: ✅ Success")
                                            
                                            # Provide content summary based on type
                                            if content_type == "wikipedia":
                                                if content.get('title'):
                                                    response_parts.append(f"     📖 Title: {content.get('title', 'Unknown')}")
                                                if content.get('extract'):
                                                    extract = content.get('extract', '')[:200]
                                                    response_parts.append(f"     📝 Summary: {extract}...")
                                                elif content.get('content'):
                                                    content_text = str(content.get('content', ''))[:200]
                                                    response_parts.append(f"     📝 Content: {content_text}...")
                                            
                                            elif content_type == "web_content":
                                                if content.get('title'):
                                                    response_parts.append(f"     🌐 Title: {content.get('title', 'Unknown')}")
                                                if content.get('text'):
                                                    text = content.get('text', '')[:200]
                                                    response_parts.append(f"     📝 Content: {text}...")
                                            
                                            # Check for actionable content
                                            if content.get('text') or content.get('extract') or content.get('content'):
                                                content_text = str(content.get('text') or content.get('extract') or content.get('content', ''))
                                                if any(action_word in content_text.lower() for action_word in ['click', 'download', 'sign up', 'register', 'subscribe', 'buy', 'order', 'contact', 'call', 'email']):
                                                    response_parts.append(f"     ⚡ Action Required: Content contains actionable items")
                                        
                                    else:
                                        response_parts.append(f"     Status: ⚠️ Partial content")
                                        if content.get('error'):
                                            response_parts.append(f"     ❌ Error: {content.get('error')}")
                                else:
                                    response_parts.append(f"     Status: ❌ No content")
                            else:
                                response_parts.append(f"   - {url_result}")
                    
                    if image_results:
                        response_parts.append(f"\n🖼️ **Image Processing Results** ({len(image_results)} images processed):")
                        for image_result in image_results:
                            response_parts.append(f"   - {image_result.image_url}")
                            response_parts.append(f"     Source: {image_result.source_email}")
                            response_parts.append(f"     Google Results: {len(image_result.google_search_results)}")
                            response_parts.append(f"     Safe: {image_result.is_safe}")
                            response_parts.append(f"     Processing Time: {image_result.processing_time:.2f}s")
                            
                            # Show web content if available
                            if image_result.web_content and not image_result.web_content.get("error"):
                                response_parts.append(f"     Web Content: ✅ Available")
                            else:
                                response_parts.append(f"     Web Content: ❌ Not available")
                    
                    response_parts.append(f"\n📊 **Summary**: {total_urls} URLs and {total_images} images found in emails")
                else:
                    # Legacy structure (just URLs)
                    response_parts.append(f"\n🌐 **URL Processing Results** ({len(processed_urls)} URLs processed):")
                    for url_result in processed_urls:
                        if isinstance(url_result, dict):
                            url = url_result.get('url', 'Unknown')
                            domain = url_result.get('domain', 'Unknown')
                            content_type = url_result.get('content_type', 'Unknown')
                            response_parts.append(f"   - {url}")
                            response_parts.append(f"     Type: {content_type}")
                            
                            # Enhanced content summary and action handling
                            if url_result.get('content'):
                                content = url_result['content']
                                if isinstance(content, dict):
                                    if content.get('success'):
                                        response_parts.append(f"     Status: ✅ Success")
                                        
                                        # Provide content summary based on type
                                        if content_type == "wikipedia":
                                            if content.get('title'):
                                                response_parts.append(f"     📖 Title: {content.get('title', 'Unknown')}")
                                            if content.get('extract'):
                                                extract = content.get('extract', '')[:200]
                                                response_parts.append(f"     📝 Summary: {extract}...")
                                            elif content.get('content'):
                                                content_text = str(content.get('content', ''))[:200]
                                                response_parts.append(f"     📝 Content: {content_text}...")
                                        
                                        elif content_type == "web_content":
                                            if content.get('title'):
                                                response_parts.append(f"     🌐 Title: {content.get('title', 'Unknown')}")
                                            if content.get('text'):
                                                text = content.get('text', '')[:200]
                                                response_parts.append(f"     📝 Content: {text}...")
                                        
                                        # Check for actionable content
                                        if content.get('text') or content.get('extract') or content.get('content'):
                                            content_text = str(content.get('text') or content.get('extract') or content.get('content', ''))
                                            if any(action_word in content_text.lower() for action_word in ['click', 'download', 'sign up', 'register', 'subscribe', 'buy', 'order', 'contact', 'call', 'email']):
                                                response_parts.append(f"     ⚡ Action Required: Content contains actionable items")
                                    
                                else:
                                    response_parts.append(f"     Status: ⚠️ Partial content")
                                    if content.get('error'):
                                        response_parts.append(f"     ❌ Error: {content.get('error')}")
                            else:
                                response_parts.append(f"     Status: ❌ No content")
                        else:
                            response_parts.append(f"   - {url_result}")
            
            return "\n".join(response_parts)
        else:
            return "No tools were executed. Please try a different request."



async def interactive_chat():
    """Interactive chat mode for command-line interface"""
    print("🤖 LLM Chat with MCP Integration v2")
    print("=" * 50)
    print("Connecting to MCP servers...")
    
    # Initialize chat bot
    chat_bot = IntelligentChatBot()
    await chat_bot.connect()
    
    print("✅ Connected! You can now chat with the LLM.")
    print("\n💡 Try these commands:")
    print("- 'Search for artificial intelligence news'")
    print("- 'Find the location of Times Square'")
    print("- 'Show my calendar events'")
    print("- 'Create a calendar event today at 10pm for 10 minutes'")
    print("- 'Check my Gmail inbox'")
    print("- 'Read my Gmail messages'")
    print("- 'Read my 1st email and process image'")
    print("- 'Extract images from my emails'")
    print("- 'Search for files in Google Drive'")
    print("- 'Read file content and process instructions'")
    print("- 'Find file named LoR Example.docx and read content'")
    print("- 'What is your name?'")
    print("- 'What is today's date?'")
    print("- Type 'quit' to exit")
    """
    print("\n🔗 **Tool Chaining Features:**")
    print("   • Gmail → URL extraction → Web processing")
    print("   • Gmail → Image extraction → Google search → Web processing")
    print("   • Automatic Wikipedia page fetching")
    print("   • Safe URL and image validation and sanitization")
    print("   • Configurable URL and image processing limits")
    print("\n🖼️ **NEW Image Processing Features:**")
    print("   • Extract images (JPG, PNG, GIF, QR codes) from emails")
    print("   • Process images through Google search for analysis")
    print("   • Visit websites found in email bodies")
    print("   • Automatic tool chaining for comprehensive analysis")
    """
    print("=" * 50)
    
    try:
        while True:
            user_input = input("\n👤 You: ").strip()
            if user_input.lower() in ['quit', 'exit', 'bye']:
                break
            
            if not user_input:
                continue
            
            print("🤖 Processing with MCP...")
            response = await chat_bot.process_message(user_input)
            print(f"🤖 Assistant: {response}")
    
    except KeyboardInterrupt:
        print("\n🛑 Chat interrupted")
    finally:
        await chat_bot.disconnect()
        print("👋 Goodbye!")

# Signal handlers for graceful shutdown
def signal_handler(signum, frame):
    print("\n🛑 Shutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def main():
    """Main function with command-line argument parsing"""
    parser = argparse.ArgumentParser(description="MCP Integration Chat Bot")
    parser.add_argument("--chat", action="store_true", help="Start interactive chat mode")
    parser.add_argument("--message", type=str, help="Process a single message")
    parser.add_argument("--max-urls", type=int, default=3, help="Maximum URLs to process (default: 3)")
    parser.add_argument("--max-images", type=int, default=3, help="Maximum images to process (default: 3)")
    parser.add_argument("--enable-tool-chaining", action="store_true", default=True, help="Enable automatic tool chaining (default: True)")
    parser.add_argument("--process-images", action="store_true", default=True, help="Enable image processing from emails (default: True)")
    
    args = parser.parse_args()
    
    if args.chat:
        # Interactive chat mode
        asyncio.run(interactive_chat())
    elif args.message:
        # Single message processing mode
        asyncio.run(process_single_message(args.message, args.max_urls, args.max_images, args.enable_tool_chaining, args.process_images))
    else:
        # Default to interactive chat mode
        print("🤖 Starting interactive chat mode...")
        print("💡 Use --help for command-line options")
        print("💡 Use --chat for explicit interactive mode")
        print("💡 Use --message 'your prompt' for single message processing")
        print("💡 Use --max-images 5 to limit image processing")
        print("💡 Use --process-images false to disable image processing")
        print()
        asyncio.run(interactive_chat())

async def process_single_message(message: str, max_urls: int = 3, max_images: int = 3, enable_tool_chaining: bool = True, process_images: bool = True):
    """Process a single message with tool chaining"""
    print(f"🤖 Processing message: {message}")
    print(f"🔗 Max URLs: {max_urls}, Max Images: {max_images}, Tool Chaining: {enable_tool_chaining}, Process Images: {process_images}")
    print("=" * 50)
    
    # Initialize chat bot
    chat_bot = IntelligentChatBot()
    await chat_bot.connect()
    
    try:
        print("🤖 Processing with MCP and tool chaining...")
        
        # Check if this is an image processing request
        if any(word in message.lower() for word in ["image", "images", "photo", "photos", "qr", "qr code", "picture", "pictures"]):
            print("🖼️ Detected image processing request - using enhanced tool chaining")
            response = await chat_bot.process_message_with_tool_chaining(message, max_urls, enable_tool_chaining)
        else:
            response = await chat_bot.process_message_with_tool_chaining(message, max_urls, enable_tool_chaining)
        
        print(f"🤖 Assistant: {response}")
    finally:
        await chat_bot.disconnect()

if __name__ == "__main__":
    main()
