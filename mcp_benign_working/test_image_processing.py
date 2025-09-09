#!/usr/bin/env python3
"""
Test script for the enhanced MCP Integration API with image processing
"""

import asyncio
import httpx
import json
from image_processor import extract_images_from_text, is_safe_url

async def test_image_processing():
    """Test the image processing capabilities"""
    
    # Test the specific prompt: "read my 1st email and process image"
    test_prompt = "read my 1st email and process image"
    
    print(f"🧪 Testing prompt: '{test_prompt}'")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        try:
            # Make request to the API
            response = await client.post(
                "http://localhost:8000/api/chat",
                json={
                    "message": test_prompt,
                    "max_urls": 5,
                    "enable_tool_chaining": True,
                    "process_images": True
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ API Response:")
                print(f"Success: {result['success']}")
                print(f"Message: {result['message']}")
                
                # Display tool results
                if result['tool_results']:
                    print(f"\n🔧 Tools Executed ({len(result['tool_results'])}):")
                    for i, tool_result in enumerate(result['tool_results'], 1):
                        print(f"  {i}. {tool_result['tool']}")
                        print(f"     Success: {tool_result['success']}")
                
                # Display processed URLs
                if result['processed_urls']:
                    print(f"\n🌐 URLs Processed ({len(result['processed_urls'])}):")
                    for i, url_result in enumerate(result['processed_urls'], 1):
                        print(f"  {i}. {url_result['url']}")
                        print(f"     Domain: {url_result['domain']}")
                        print(f"     Type: {url_result['content_type']}")
                        print(f"     Safe: {url_result['is_safe']}")
                
                # Display processed images
                if result['processed_images']:
                    print(f"\n🖼️ Images Processed ({len(result['processed_images'])}):")
                    for i, image_result in enumerate(result['processed_images'], 1):
                        print(f"  {i}. {image_result['image_url']}")
                        print(f"     Source: {image_result['source_email']}")
                        print(f"     Google Results: {len(image_result['google_search_results'])}")
                        print(f"     Safe: {image_result['is_safe']}")
                        print(f"     Processing Time: {image_result['processing_time']:.2f}s")
                
                # Display any errors
                if result.get('error'):
                    print(f"\n❌ Error: {result['error']}")
                    
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")

async def test_direct_image_processing():
    """Test direct image processing without Gmail"""
    
    print(f"\n🧪 Testing direct image processing")
    print("=" * 50)
    
    # Test with a message containing an image URL
    test_message = "Process this image: https://example.com/image.jpg and search for related content"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/api/chat",
                json={
                    "message": test_message,
                    "max_urls": 3,
                    "enable_tool_chaining": True,
                    "process_images": True
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Direct Image Processing Response:")
                print(f"Success: {result['success']}")
                print(f"Message: {result['message']}")
                
                if result['processed_images']:
                    print(f"Images found and processed: {len(result['processed_images'])}")
                if result['processed_urls']:
                    print(f"URLs found and processed: {len(result['processed_urls'])}")
                    
            else:
                print(f"❌ Direct processing failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Direct processing request failed: {e}")

def test_image_extraction():
    """Test image extraction functionality locally"""
    print(f"\n🧪 Testing image extraction locally")
    print("=" * 50)
    
    # Test text with various image URLs
    test_text = """
    Check out these images:
    https://example.com/photo.jpg
    https://site.com/image.png?size=large
    https://domain.org/picture.gif
    And this QR code: https://qr.example.com/code.png
    """
    
    images = extract_images_from_text(test_text)
    print(f"Found {len(images)} images:")
    for i, img in enumerate(images, 1):
        print(f"  {i}. {img}")
        print(f"     Safe: {is_safe_url(img)}")

if __name__ == "__main__":
    print("🚀 Testing Enhanced MCP Integration API with Image Processing")
    print("Make sure the API server is running on localhost:8000")
    print()
    
    # Test local image extraction first
    test_image_extraction()
    
    # Run API tests
    asyncio.run(test_image_processing())
    asyncio.run(test_direct_image_processing())
    
    print("\n✨ Test completed!") 