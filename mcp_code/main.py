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
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the MCP client
from mcp_client import MCPClient

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
💾 **Google Drive**: "Search for files", "Retrieve a file"
🌐 **URL Processing**: "Check this website: https://example.com"
📚 **Wikipedia Access**: "Get Wikipedia page about Python"
🌍 **Web Scraping**: "Access content from any website"
💭 **General Chat**: Ask me questions, get the date/time, or just chat!

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
    
    async def _extract_and_access_urls_from_emails(self, messages, max_urls=1):
        """Extract URLs from Gmail messages and fetch their content safely"""
        urls = []
        for msg in messages:
            body = msg.get("body", "") or msg.get("snippet", "")
            found_urls = re.findall(r'https?://[^\s]+', body)
            urls.extend(found_urls)
            if len(urls) >= max_urls:
                break

        results = []
        for url in urls[:max_urls]:
            if not url.lower().startswith(("http://", "https://")):
                continue

            if "wikipedia.org" in url.lower():
                page_title = url.split("/")[-1].replace("_", " ")
                result = await self.mcp_client.call_tool("wikipedia", "get_page", {"title": page_title, "url": url})
            else:
                result = await self.mcp_client.call_tool("web_access", "get_content", {"url": url})

            results.append({"url": url, "content": result})

        return results

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
        
        # Enhanced search detection - catch more types of queries
        if any(word in input_lower for word in ["search", "find", "google", "look up", "what is", "how to", "weather", "news", "information about", "tell me about"]):
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
        
        # Drive detection
        if any(word in input_lower for word in ["drive", "file", "search", "retrieve"]):
            tools_to_use.append(("drive", "search", {"query": user_input}))
        
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
                print(f"📧 Detected email read command")
                tools_to_use.append(("gmail", "get_messages", {"query": "", "max_results": 5}))
            
            else:
                # Default to reading emails if no specific action detected
                print(f"📧 Default email action: reading messages")
                tools_to_use.append(("gmail", "get_messages", {"query": "", "max_results": 5}))
        
        # URL detection
        url_pattern = r'https?://[^\s]+'
        url_matches = re.findall(url_pattern, user_input)
        
        if url_matches:
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
                    url_results = await self._extract_and_access_urls_from_emails(result.get("messages", []))
                    if url_results:
                        results.append(f"🌐 Extracted & accessed URLs: {url_results}")
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
    print("- 'What is your name?'")
    print("- 'What is today's date?'")
    print("- 'Search for files in Google Drive'")
    print("- Type 'quit' to exit")
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

if __name__ == "__main__":
    asyncio.run(interactive_chat())
