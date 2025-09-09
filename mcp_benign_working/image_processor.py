#!/usr/bin/env python3
"""
Image Processing Module for MCP Integration
Handles image extraction, processing, and Google search integration
"""

import re
import time
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
from pydantic import BaseModel

class ImageProcessingResult(BaseModel):
    """Result of image processing operation"""
    image_url: str
    source_email: str
    google_search_results: List[Dict[str, Any]]
    web_content: Dict[str, Any]
    processing_time: float
    is_safe: bool

def is_safe_url(url: str) -> bool:
    """Check if URL is safe to process"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Blocked domains for security
        BLOCKED_DOMAINS = {
            "malware.com", "phishing.com", "scam.com", "virus.com", "hack.com",
            "exploit.com", "crack.com", "warez.com", "torrent.com", "pirate.com"
        }
        
        # Check if domain is blocked
        if domain in BLOCKED_DOMAINS:
            return False
            
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

def extract_images_from_text(text: str) -> List[str]:
    """Extract image URLs from text using regex"""
    if not text:
        return []
    
    # Image URL patterns (common image formats)
    image_patterns = [
        r'https?://[^\s<>"]+\.(jpg|jpeg|png|gif|bmp|webp|svg|ico)(\?[^\s<>"]*)?',
        r'https?://[^\s<>"]+\.(jpg|jpeg|png|gif|bmp|webp|svg|ico)(#[^\s<>"]*)?',
        r'https?://[^\s<>"]+/image[^\s<>"]*',
        r'https?://[^\s<>"]+/img[^\s<>"]*',
        r'https?://[^\s<>"]+/photo[^\s<>"]*'
    ]
    
    all_images = []
    for pattern in image_patterns:
        images = re.findall(pattern, text, re.IGNORECASE)
        all_images.extend(images)
    
    # Clean and validate image URLs
    cleaned_images = []
    for img_url in all_images:
        if isinstance(img_url, tuple):
            # Handle regex groups
            img_url = img_url[0]
        
        # Remove trailing punctuation
        img_url = img_url.rstrip('.,;:!?')
        # Remove trailing quotes
        img_url = img_url.rstrip('"\'')
        # Remove trailing parentheses
        img_url = img_url.rstrip(')')
        
        if img_url and is_safe_url(img_url):
            cleaned_images.append(img_url)
    
    return list(set(cleaned_images))  # Remove duplicates

async def process_image_with_google_search(mcp_client, image_url: str, source_email: str = "unknown") -> ImageProcessingResult:
    """Process image by searching Google and analyzing web content"""
    start_time = time.time()
    
    try:
        # Search Google for the image URL or related content
        search_query = f"image analysis {image_url}"
        google_results = await mcp_client.call_tool("google", "search", {
            "query": search_query,
            "num_results": 5
        })
        
        # Try to get web content from the image URL if it's a website
        web_content = {}
        try:
            if "http" in image_url:
                web_content = await mcp_client.call_tool("web_access", "get_content", {
                    "url": image_url
                })
        except Exception:
            web_content = {"error": "Could not fetch web content from image URL"}
        
        processing_time = time.time() - start_time
        
        return ImageProcessingResult(
            image_url=image_url,
            source_email=source_email,
            google_search_results=google_results.get("results", []),
            web_content=web_content,
            processing_time=processing_time,
            is_safe=True
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        return ImageProcessingResult(
            image_url=image_url,
            source_email=source_email,
            google_search_results=[],
            web_content={"error": str(e)},
            processing_time=processing_time,
            is_safe=False
        )

async def process_gmail_with_image_and_url_chaining(mcp_client, messages: List[Dict[str, Any]], max_urls: int = 3, process_images: bool = True):
    """Process Gmail messages and automatically chain image and URL processing"""
    from utils import extract_urls_from_text, process_urls_safely
    
    all_urls = []
    all_images = []
    
    # Extract URLs and images from all messages
    for msg in messages:
        body = msg.get("body", "") or msg.get("snippet", "")
        urls = extract_urls_from_text(body)
        all_urls.extend(urls)
        
        if process_images:
            images = extract_images_from_text(body)
            all_images.extend(images)
    
    # Remove duplicates while preserving order
    unique_urls = list(dict.fromkeys(all_urls))
    unique_images = list(dict.fromkeys(all_images))
    
    # Limit to max_urls
    urls_to_process = unique_urls[:max_urls]
    images_to_process = unique_images[:max_urls] if process_images else []
    
    # Process URLs safely
    url_results = []
    for url in urls_to_process:
        result = await process_urls_safely([url], mcp_client, 1)
        if result:
            url_results.append(result[0])
    
    # Process images with Google search
    image_results = []
    for img_url in images_to_process:
        result = await process_image_with_google_search(mcp_client, img_url, "gmail")
        image_results.append(result)
    
    return url_results, image_results 