import re
import html
import asyncio
import json
import os
from datetime import datetime
from api_clients import _gmail_get_message_content
from mcp_client import MCPClient

def _clean_html_text(html_text: str) -> str:
    if not html_text:
        return ""
    clean_text = re.sub(r'<[^>]+>', '', html_text)
    clean_text = html.unescape(clean_text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    return clean_text

def _create_email_summary(email_contents: list) -> str:
    summary_lines = [
        f"📧 EMAIL SUMMARY - {len(email_contents)} RECENT MESSAGES",
        "=" * 50,
        "",
    ]
    for i, email in enumerate(email_contents, 1):
        subject = email.get('subject', 'No Subject')
        sender = email.get('from', 'Unknown Sender')
        body = email.get('body', '')
        summary_lines.extend([
            f"{i}. SUBJECT: {subject}",
            f"   FROM: {sender}",
            "",
        ])
        
        highlights = _extract_highlights_from_content(body)
        if highlights:
            summary_lines.extend([
                f"   📝 HIGHLIGHTS: {highlights}",
                "",
            ])
        else:
            summary_lines.extend([
                f"   📝 CONTENT: {email.get('snippet', '')[:200]}...",
                "",
            ])
    
    summary_lines.extend([
        "=" * 50,
        f"Total emails processed: {len(email_contents)}",
        f"Summary generated at: {datetime.now()}",
    ])
    return "\n".join(summary_lines)

def _extract_highlights_from_content(content: str):
    if not content:
        return ""
    
    content = re.sub(r'<[^>]+>', '', content)
    content = re.sub(r'\s+', ' ', content).strip()
    content = re.sub(r'--\s*\n.*', '', content, flags=re.DOTALL)
    
    highlights = []
    action_patterns = [r'please\s+([^.]+)', r'need\s+([^.]+)', r'request\s+([^.]+)', r'urgent\s+([^.]+)', r'deadline\s+([^.]+)', r'meeting\s+([^.]+)', r'call\s+([^.]+)', r'email\s+([^.]+)', r'update\s+([^.]+)', r'confirm\s+([^.]+)' ]
    for pattern in action_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            if len(match.strip()) > 10:
                highlights.append(f"Action required: {match.strip()}")
    
    date_patterns = [r'\b(today|tomorrow|next week|this week|this month)\b', r'\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?\b', r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}\b' ]
    for pattern in date_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            if match not in highlights:
                highlights.append(f"Timeline: {match}")

    topic_patterns = [r'\b(project|meeting|report|budget|client|team|update|status)\b', r'\b(issue|problem|solution|plan|strategy|goal|target)\b', r'\b(approval|review|feedback|decision|agreement|contract)\b' ]
    for pattern in topic_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            if match not in highlights:
                highlights.append(f"Topic: {match.title()}")
                
    if highlights:
        unique_highlights = list(dict.fromkeys(highlights))[:5]
        return " ".join(unique_highlights) + "."

    sentences = re.split(r'[.!?]+', content)
    meaningful_sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    if meaningful_sentences:
        summary_sentences = meaningful_sentences[:3]
        return " ".join(summary_sentences) + "."
    
    return content[:150] + "..." if len(content) > 150 else content

async def interactive_chat():
    print("🤖 Welcome to MCP Chat!")
    print("Press Ctrl+C to exit.")
    mcp_client = MCPClient()
    await mcp_client.connect_to_servers()
    
    try:
        while True:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            
            print(f"🤖 Processing your request...")
            
            # Simple example of interactive tool call
            if "search" in user_input.lower():
                query = user_input.split("search", 1)[-1].strip()
                if query:
                    try:
                        result = await mcp_client.call_tool("google", "search", {"query": query})
                        print(json.dumps(result, indent=2))
                    except Exception as e:
                        print(f"❌ Error: {e}")
                else:
                    print("Please provide a search query.")
            
            else:
                print("I'm not sure how to handle that. Try a command like 'search [query]'.")
    
    except KeyboardInterrupt:
        print("\n🛑 Chat interrupted")
    finally:
        await mcp_client.disconnect()
        print("👋 Goodbye!")