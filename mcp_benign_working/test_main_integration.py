#!/usr/bin/env python3
"""
Test script for the integrated image processing functionality in main.py
"""

import asyncio
import subprocess
import sys

def test_command_line_interface():
    """Test the command-line interface with various image processing commands"""
    
    print("🧪 Testing Main.py Integration with Image Processing")
    print("=" * 60)
    
    # Test 1: The specific prompt you mentioned
    print("\n1️⃣ Testing: 'read my 1st email and process image'")
    print("-" * 50)
    try:
        result = subprocess.run([
            sys.executable, "main.py", 
            "--message", "read my 1st email and process image",
            "--max-urls", "5",
            "--max-images", "3",
            "--enable-tool-chaining",
            "--process-images"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Command executed successfully!")
            print("📤 Output preview:")
            lines = result.stdout.split('\n')
            for line in lines[:10]:  # Show first 10 lines
                if line.strip():
                    print(f"   {line}")
            if len(lines) > 10:
                print("   ... (truncated)")
        else:
            print(f"❌ Command failed with return code: {result.returncode}")
            print(f"📤 Error output: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("⏰ Command timed out after 30 seconds")
    except Exception as e:
        print(f"❌ Error running command: {e}")
    
    # Test 2: Extract images from emails
    print("\n2️⃣ Testing: 'Extract images from my emails'")
    print("-" * 50)
    try:
        result = subprocess.run([
            sys.executable, "main.py", 
            "--message", "Extract images from my emails",
            "--max-images", "5",
            "--enable-tool-chaining",
            "--process-images"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Command executed successfully!")
            print("📤 Output preview:")
            lines = result.stdout.split('\n')
            for line in lines[:10]:  # Show first 10 lines
                if line.strip():
                    print(f"   {line}")
            if len(lines) > 10:
                print("   ... (truncated)")
        else:
            print(f"❌ Command failed with return code: {result.returncode}")
            print(f"📤 Error output: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("⏰ Command timed out after 30 seconds")
    except Exception as e:
        print(f"❌ Error running command: {e}")
    
    # Test 3: Process QR codes
    print("\n3️⃣ Testing: 'Process QR codes in my inbox'")
    print("-" * 50)
    try:
        result = subprocess.run([
            sys.executable, "main.py", 
            "--message", "Process QR codes in my inbox",
            "--max-images", "3",
            "--enable-tool-chaining",
            "--process-images"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Command executed successfully!")
            print("📤 Output preview:")
            lines = result.stdout.split('\n')
            for line in lines[:10]:  # Show first 10 lines
                if line.strip():
                    print(f"   {line}")
            if len(lines) > 10:
                print("   ... (truncated)")
        else:
            print(f"❌ Command failed with return code: {result.returncode}")
            print(f"📤 Error output: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("⏰ Command timed out after 30 seconds")
    except Exception as e:
        print(f"❌ Error running command: {e}")
    
    # Test 4: Help command
    print("\n4️⃣ Testing: Help command")
    print("-" * 50)
    try:
        result = subprocess.run([
            sys.executable, "main.py", "--help"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Help command executed successfully!")
            print("📤 Help output:")
            lines = result.stdout.split('\n')
            for line in lines:
                if line.strip():
                    print(f"   {line}")
        else:
            print(f"❌ Help command failed with return code: {result.returncode}")
            
    except subprocess.TimeoutExpired:
        print("⏰ Help command timed out")
    except Exception as e:
        print(f"❌ Error running help command: {e}")

def test_local_functions():
    """Test the local image processing functions"""
    
    print("\n🧪 Testing Local Image Processing Functions")
    print("=" * 60)
    
    try:
        # Import the functions
        from image_processor import extract_images_from_text, is_safe_url
        
        # Test image extraction
        test_text = """
        Check out these images:
        https://example.com/photo.jpg
        https://site.com/image.png?size=large
        https://domain.org/picture.gif
        And this QR code: https://qr.example.com/code.png
        """
        
        images = extract_images_from_text(test_text)
        print(f"✅ Image extraction test: Found {len(images)} images")
        for i, img in enumerate(images, 1):
            safe = is_safe_url(img)
            print(f"   {i}. {img} - Safe: {safe}")
        
        # Test URL safety
        test_urls = [
            "https://example.com/safe.jpg",
            "https://malware.com/bad.exe",
            "https://localhost:8080/test.png",
            "https://wikipedia.org/wiki/test"
        ]
        
        print(f"\n✅ URL safety test:")
        for url in test_urls:
            safe = is_safe_url(url)
            print(f"   {url} - Safe: {safe}")
            
    except ImportError as e:
        print(f"❌ Could not import image processing functions: {e}")
    except Exception as e:
        print(f"❌ Error testing local functions: {e}")

if __name__ == "__main__":
    print("🚀 Testing Main.py Integration with Image Processing")
    print("Make sure you have:")
    print("1. MCP servers running")
    print("2. Gmail access configured")
    print("3. All dependencies installed")
    print()
    
    # Test local functions first
    test_local_functions()
    
    # Test command-line interface
    test_command_line_interface()
    
    print("\n✨ Integration testing completed!")
    print("\n💡 To test manually, try:")
    print("   python main.py --message 'read my 1st email and process image'")
    print("   python main.py --chat")
    print("   python main.py --help") 