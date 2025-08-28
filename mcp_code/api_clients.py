import os
import httpx
import json
import re
import html
import base64
from typing import Dict, Any, List
import asyncio

async def _google_search(query: str):
    api_key = os.getenv("GOOGLE_API_KEY")
    cse_id = os.getenv("GOOGLE_CSE_ID")
    if not api_key or not cse_id:
        raise Exception("Google API key or CSE ID not configured")
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": api_key, "cx": cse_id, "q": query}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            return {"items": items, "totalResults": data.get("searchInformation", {}).get("totalResults", 0)}
        else:
            raise Exception(f"Google search failed: {response.text}")

async def _slack_send_message(channel: str, text: str):
    bot_token = os.getenv("SLACK_BOT_TOKEN")
    if not bot_token:
        raise Exception("Slack bot token not configured")
    
    url = "https://slack.com/api/chat.postMessage"
    headers = {"Authorization": f"Bearer {bot_token}", "Content-Type": "application/json"}
    data = {"channel": channel, "text": text}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                return {"ok": True, "channel": channel, "ts": result.get("ts")}
            else:
                raise Exception(f"Slack API error: {result.get('error')}")
        else:
            raise Exception(f"Slack API request failed: {response.text}")

async def _maps_geocode(address: str):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise Exception("Google Maps API key not configured")
    
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": api_key}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "OK" and data.get("results"):
                result = data["results"][0]
                geometry = result.get("geometry", {})
                location = geometry.get("location", {})
                return {
                    "formatted_address": result.get("formatted_address"),
                    "latitude": location.get("lat"),
                    "longitude": location.get("lng"),
                    "place_id": result.get("place_id"),
                }
            else:
                raise Exception(f"Geocoding failed: {data.get('status')}")
        else:
            raise Exception(f"Maps API request failed: {response.text}")

async def _google_calendar_events(time_min: str = None, time_max: str = None, max_results: int = 10):
    access_token = os.getenv("GOOGLE_ACCESS_TOKEN")
    if not access_token:
        raise Exception("Google access token not configured for Calendar access")
    
    url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    params = {
        "timeMin": time_min or "2024-01-01T00:00:00Z",
        "maxResults": max_results,
        "singleEvents": True,
        "orderBy": "startTime",
    }
    if time_max:
        params["timeMax"] = time_max
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            events = data.get("items", [])
            return {"events": events, "total": len(events), "nextPageToken": data.get("nextPageToken")}
        else:
            raise Exception(f"Google Calendar API failed: {response.text}")

async def _google_calendar_create_event(summary: str, start_time: str, end_time: str, description: str = ""):
    access_token = os.getenv("GOOGLE_ACCESS_TOKEN")
    if not access_token:
        raise Exception("Google access token not configured for Calendar access")
    
    url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    event_data = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start_time, "timeZone": "UTC"},
        "end": {"dateTime": end_time, "timeZone": "UTC"},
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=event_data)
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "eventId": result.get("id"),
                "htmlLink": result.get("htmlLink"),
                "summary": result.get("summary"),
                "start": result.get("start", {}).get("dateTime"),
                "end": result.get("end", {}).get("dateTime"),
            }
        else:
            raise Exception(f"Google Calendar API failed: {response.text}")

async def _gmail_messages(query: str = None, max_results: int = 10):
    access_token = os.getenv("GOOGLE_ACCESS_TOKEN")
    if not access_token:
        raise Exception("Google access token not configured for Gmail access")
    
    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    params = {"maxResults": max_results}
    if query:
        params["q"] = query
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            messages = data.get("messages", [])
            return {"messages": messages, "total": len(messages), "nextPageToken": data.get("nextPageToken")}
        else:
            raise Exception(f"Gmail API failed: {response.text}")

async def _gmail_send_message(to: str, subject: str, body: str):
    access_token = os.getenv("GOOGLE_ACCESS_TOKEN")
    if not access_token:
        raise Exception("Google access token not configured for Gmail access")
    
    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    email_content = f"""From: me
To: {to}
Subject: {subject}

{body}"""
    encoded_message = base64.urlsafe_b64encode(email_content.encode()).decode()
    data = {"raw": encoded_message}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            return {"success": True, "messageId": result.get("id"), "threadId": result.get("threadId")}
        else:
            raise Exception(f"Gmail send failed: {response.text}")

async def _gmail_get_message_content(message_id: str):
    access_token = os.getenv("GOOGLE_ACCESS_TOKEN")
    if not access_token:
        raise Exception("Google access token not configured for Gmail access")
    
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    params = {"format": "metadata"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            payload = data.get("payload", {})
            subject = ""
            sender = ""
            body = ""
            headers = payload.get("headers", [])
            for header in headers:
                if header.get("name") == "Subject":
                    subject = header.get("value", "")
                elif header.get("name") == "From":
                    sender = header.get("value", "")

            if "parts" in payload:
                for part in payload["parts"]:
                    if part.get("mimeType") == "text/plain":
                        body_data = part.get("body", {}).get("data", "")
                        if body_data:
                            body = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
                            break
                    elif part.get("mimeType") == "text/html":
                        body_data = part.get("body", {}).get("data", "")
                        if body_data:
                            body = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
                            break
            else:
                body_data = payload.get("body", {}).get("data", "")
                if body_data:
                    body = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
            
            return {
                "id": message_id,
                "subject": subject,
                "from": sender,
                "body": body,
                "snippet": data.get("snippet", ""),
            }
        else:
            raise Exception(f"Gmail message content failed: {response.text}")

async def _gmail_summarize_and_send(target_email: str, max_emails: int = 10):
    try:
        emails_data = await _gmail_messages(max_results=max_emails)
        messages = emails_data.get("messages", [])
        if not messages:
            return {"success": False, "error": "No emails found"}
        
        email_contents = []
        for message in messages[:max_emails]:
            try:
                content = await _gmail_get_message_content(message["id"])
                email_contents.append(content)
            except Exception as e:
                print(f"Warning: Could not get content for message {message['id']}: {e}")
        
        summary = _create_email_summary(email_contents)
        subject = f"Email Summary - {len(email_contents)} Recent Messages"
        send_result = await _gmail_send_message(target_email, subject, summary)
        
        return {
            "success": True,
            "emails_processed": len(email_contents),
            "summary_sent_to": target_email,
            "send_result": send_result,
            "summary": summary,
        }
    except Exception as error:
        return {"success": False, "error": str(error)}
        
async def _drive_search(query: str):
    access_token = os.getenv("GOOGLE_ACCESS_TOKEN")
    if not access_token:
        raise Exception("Google access token not configured for Drive access")

    url = "https://www.googleapis.com/drive/v3/files"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    params = {
        "q": f"name contains '{query}'",
        "fields": "files(id,name,mimeType,size,modifiedTime,webViewLink)",
        "pageSize": 10,
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            files = data.get("files", [])
            return {"files": files, "total": len(files), "query": query}
        else:
            raise Exception(f"Drive search failed: {response.text}")

async def _drive_retrieve(target_file: str):
    access_token = os.getenv("GOOGLE_ACCESS_TOKEN")
    if not access_token:
        raise Exception("Google access token not configured for Drive access")
    
    search_result = await _drive_search(target_file)
    files = search_result.get("files", [])

    if not files:
        raise Exception(f"No files found for query: {target_file}")
    
    file_id = files[0].get("id")
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            file_data = response.json()
            return {
                "success": True,
                "file": file_data,
                "download_url": f"https://drive.google.com/file/d/{file_id}/view?usp=sharing",
            }
        else:
            raise Exception(f"Failed to retrieve file: {response.text}")

async def _wikipedia_get_page(title: str, url: str):
    if url:
        # Extract title from URL if possible
        match = re.search(r"wikipedia\.org/wiki/(.*)", url)
        if match:
            title = match.group(1).replace("_", " ")

    if not title:
        raise Exception("No Wikipedia title or URL provided")
    
    # Simple search or direct fetch from Wikipedia API
    wikipedia_url = f"https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "extracts",
        "exintro": True,
        "explaintext": True,
        "titles": title,
        "format": "json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(wikipedia_url, params=params)
        if response.status_code == 200:
            data = response.json()
            page = next(iter(data['query']['pages'].values()))
            if 'extract' in page:
                return {"title": page['title'], "extract": page['extract']}
            else:
                return {"error": "Page not found"}
        else:
            raise Exception(f"Wikipedia API request failed: {response.text}")
            
async def _web_access_get_content(url: str):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, follow_redirects=True, timeout=10)
            response.raise_for_status()
            
            # Simple content extraction (can be improved with a parser)
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            text_content = soup.get_text()
            
            return {"url": url, "content": text_content[:2000]} # Limit for brevity
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP error fetching content: {e.response.status_code} - {e.response.reason_phrase}")
        except Exception as e:
            raise Exception(f"Error fetching content: {e}")

def _create_email_summary(email_contents: list) -> str:
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
            highlights = _extract_highlights_from_content(body)
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
        f"Summary generated at: {asyncio.get_event_loop().time()}"
    ])
    
    return "\n".join(summary_lines)

def _extract_highlights_from_content(content: str):
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