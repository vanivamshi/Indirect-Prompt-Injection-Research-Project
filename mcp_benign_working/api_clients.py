import os
import httpx
import json
import re
import html
import base64
from typing import Dict, Any, List
import asyncio
from datetime import datetime, timedelta

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
    
    # Use current time minus 7 days as default to get recent events
    if not time_min:
        now = datetime.now()
        one_week_ago = now - timedelta(days=7)
        time_min = one_week_ago.isoformat() + "Z"
        #if not time_max:
        #    month_ahead = (now + timedelta(days=30)).isoformat() + "Z"
        #    time_max = month_ahead
    elif not time_max:
        # If time_min is provided but time_max is not, set a default time_max
        now = datetime.now()
        month_ahead = (now + timedelta(days=30)).isoformat() + "Z"
        time_max = month_ahead
    
    url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    params = {
        "timeMin": time_min,
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

async def _google_calendar_update_event(event_id: str, summary: str = None, start_time: str = None, end_time: str = None, description: str = None, attendees: list = None):
    """Update an existing Google Calendar event"""
    access_token = os.getenv("GOOGLE_ACCESS_TOKEN")
    if not access_token:
        raise Exception("Google access token not configured for Calendar access")
    
    url = f"https://www.googleapis.com/calendar/v3/calendars/primary/events/{event_id}"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    
    # Build update data - only include fields that are being updated
    event_data = {}
    if summary is not None:
        event_data["summary"] = summary
    if description is not None:
        event_data["description"] = description
    if start_time is not None:
        event_data["start"] = {"dateTime": start_time, "timeZone": "UTC"}
    if end_time is not None:
        event_data["end"] = {"dateTime": end_time, "timeZone": "UTC"}
    if attendees is not None:
        event_data["attendees"] = [{"email": email} for email in attendees]
    
    async with httpx.AsyncClient() as client:
        response = await client.patch(url, headers=headers, json=event_data)
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "eventId": result.get("id"),
                "htmlLink": result.get("htmlLink"),
                "summary": result.get("summary"),
                "start": result.get("start", {}).get("dateTime"),
                "end": result.get("end", {}).get("dateTime"),
                "attendees": result.get("attendees", []),
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
    
    # Clean and validate message ID
    message_id = message_id.strip()
    if not message_id:
        raise Exception("Message ID cannot be empty")
    
    print(f"🔍 Fetching Gmail message content for ID: {message_id}")
    print(f"🔍 Message ID length: {len(message_id)}")
    print(f"🔍 Message ID format: {message_id[:10]}...{message_id[-10:] if len(message_id) > 20 else ''}")
    
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    params = {"format": "metadata", "metadataHeaders": ["Subject", "From"]}
    
    print(f"🔍 Using format: {params['format']}")
    print(f"🔍 Full URL: {url}")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        print(f"🔍 Gmail API response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"🔍 Gmail API response keys: {list(data.keys())}")
            print(f"🔍 Raw response preview: {str(data)[:500]}...")
            
            payload = data.get("payload", {})
            print(f"🔍 Payload keys: {list(payload.keys())}")
            print(f"🔍 Payload preview: {str(payload)[:500]}...")
            
            subject = ""
            sender = ""
            body = ""
            headers = payload.get("headers", [])
            
            for header in headers:
                if header.get("name") == "Subject":
                    subject = header.get("value", "")
                elif header.get("name") == "From":
                    sender = header.get("value", "")

            print(f"🔍 Found subject: {subject}")
            print(f"🔍 Found sender: {sender}")
            
            # With metadata format, we can only access headers and snippet
            # Extract what we can from the available data
            snippet = data.get("snippet", "")
            print(f"🔍 Snippet content: {snippet[:100] if snippet else 'EMPTY'}...")
            
            # Combine subject and snippet to maximize content for URL extraction
            combined_content = f"{subject} {snippet}".strip()
            print(f"🔍 Combined content (subject + snippet): {combined_content[:100] if combined_content else 'EMPTY'}...")
            
            # Use combined content as body for URL extraction
            if combined_content:
                body = combined_content
                print(f"🔍 Using combined content as body, length: {len(body)}")
            else:
                body = ""
                print("⚠️ No content available for URL extraction")
            
            print(f"🔍 Final body length: {len(body)}")
            print(f"🔍 Body preview: {body[:100] if body else 'EMPTY'}...")
            
            # Check if we got any content at all
            if not body and not data.get("snippet"):
                print("⚠️ Warning: No body content and no snippet found")
                print("🔍 This might indicate an empty message or API permission issue")
            
            result = {
                "id": message_id,
                "subject": subject,
                "from": sender,
                "body": body,
                "snippet": data.get("snippet", ""),
            }
            
            print(f"🔍 Returning result: {result}")
            return result
        else:
            print(f"❌ Gmail API error: {response.status_code} - {response.text}")
            
            # Handle common Gmail API errors
            if response.status_code == 401:
                raise Exception("Gmail API authentication failed. Please check your access token.")
            elif response.status_code == 403:
                raise Exception("Gmail API access denied. Please check your API permissions and scopes.")
            elif response.status_code == 404:
                raise Exception(f"Gmail message not found: {message_id}")
            elif response.status_code == 429:
                raise Exception("Gmail API quota exceeded. Please try again later.")
            else:
                raise Exception(f"Gmail message content failed: {response.status_code} - {response.text}")

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

    print(f"🔍 Drive API search for: '{query}'")
    
    url = "https://www.googleapis.com/drive/v3/files"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    
    # Clean the query first
    clean_query = query.strip().strip('"').strip("'")
    print(f"🔍 Cleaned query: '{clean_query}'")
    
    # Try multiple search strategies with proper Google Drive API syntax
    search_queries = [
        f"name contains '{clean_query}'",  # Original approach
        f"name='{clean_query}'",           # Exact match (no spaces around =)
        f"name contains '{clean_query.lower()}'",  # Lowercase
        f"name contains '{clean_query.upper()}'",  # Uppercase
        f"fullText contains '{clean_query}'",      # Full text search
    ]
    
    # Add variations if query has spaces
    if ' ' in clean_query:
        search_queries.extend([
            f"name contains '{clean_query.replace(' ', '_')}'",  # Underscore version
            f"name contains '{clean_query.replace(' ', '-')}'",  # Hyphen version
            f"name contains '{clean_query.replace(' ', '')}'",   # No space version
        ])
    
    # Add simple word searches
    words = clean_query.split()
    if len(words) > 1:
        for word in words:
            if len(word) > 2:  # Only meaningful words
                search_queries.append(f"name contains '{word}'")
    
    all_files = []
    successful_queries = []
    
    async with httpx.AsyncClient() as client:
        for search_q in search_queries:
            try:
                params = {
                    "q": search_q,
                    "fields": "files(id,name,mimeType,size,modifiedTime,webViewLink)",
                    "pageSize": 10,
                }
                
                print(f"🔍 Trying search: {search_q}")
                response = await client.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    files = data.get("files", [])
                    if files:
                        print(f"✅ Found {len(files)} files with query: {search_q}")
                        all_files.extend(files)
                        successful_queries.append(search_q)
                    else:
                        print(f"❌ No files found with query: {search_q}")
                else:
                    print(f"❌ Search failed with status {response.status_code}: {response.text}")
                    
            except Exception as e:
                print(f"❌ Exception during search '{search_q}': {e}")
    
    # Remove duplicates based on file ID
    unique_files = []
    seen_ids = set()
    for file in all_files:
        if file['id'] not in seen_ids:
            unique_files.append(file)
            seen_ids.add(file['id'])
    
    print(f"🔍 Total unique files found: {len(unique_files)}")
    print(f"🔍 Successful queries: {successful_queries}")
    
    # If no files found, try to list recent files to see what's available
    if len(unique_files) == 0:
        print("🔍 No files found with search queries. Trying to list recent files...")
        try:
            params = {
                "fields": "files(id,name,mimeType,size,modifiedTime,webViewLink)",
                "pageSize": 10,
                "orderBy": "modifiedTime desc"
            }
            
            response = await client.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                recent_files = data.get("files", [])
                print(f"🔍 Found {len(recent_files)} recent files in Drive:")
                for file in recent_files[:5]:  # Show first 5 files
                    print(f"   - {file.get('name', 'Unknown')} ({file.get('mimeType', 'Unknown type')})")
            else:
                print(f"❌ Failed to list recent files: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Exception listing recent files: {e}")
    
    return {
        "files": unique_files, 
        "total": len(unique_files), 
        "query": query,
        "successful_queries": successful_queries
    }

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
                result = {
                    "success": True,
                    "title": page['title'], 
                    "extract": page['extract'],
                    "content": page['extract']  # Add content field for compatibility
                }
                print(f"🔍 Wikipedia API result: {result}")
                return result
            else:
                result = {"success": False, "error": "Page not found"}
                print(f"🔍 Wikipedia API error: {result}")
                return result
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
            
            result = {"url": url, "content": text_content[:2000], "success": True} # Limit for brevity
            print(f"🔍 Web access result: {result}")
            return result
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