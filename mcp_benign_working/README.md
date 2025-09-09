# Enhanced MCP Integration API with Image Processing

This enhanced API server provides automatic tool chaining between Gmail, web access, and Google search tools, with special capabilities for processing images and URLs from emails.

## 🚀 Features

- **Automatic Email Processing**: Read Gmail messages and extract content
- **Image Detection & Processing**: Automatically find and process images (including QR codes) from emails
- **URL Processing**: Extract and safely process URLs from email content
- **Tool Chaining**: Seamlessly chain Gmail → Image/URL → Google Search → Web Access
- **Security**: Built-in URL validation and domain safety checks
- **Flexible API**: Support for various prompt formats and processing options

## 📁 Project Structure

```
├── api_server.py          # Main FastAPI server
├── image_processor.py     # Image processing module
├── mcp_client.py          # MCP client for tool integration
├── test_image_processing.py # Test script
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🛠️ Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure your MCP servers are running and configured

3. Start the API server:
```bash
python api_server.py
```

The server will run on `http://localhost:8000`

## 📖 Usage Examples

### Example 1: Read First Email and Process Images
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "read my 1st email and process image",
    "max_urls": 5,
    "enable_tool_chaining": true,
    "process_images": true
  }'
```

### Example 2: Process Specific Email Content
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "read message abc123 and extract images",
    "max_urls": 3,
    "enable_tool_chaining": true,
    "process_images": true
  }'
```

### Example 3: Direct Image Processing
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Process this QR code: https://example.com/qr.png",
    "max_urls": 2,
    "enable_tool_chaining": true,
    "process_images": true
  }'
```

## 🔧 API Endpoints

### POST `/api/chat`
Main endpoint for processing requests with automatic tool chaining.

**Request Body:**
```json
{
  "message": "string",
  "max_urls": 3,
  "enable_tool_chaining": true,
  "process_images": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "string",
  "tool_results": [...],
  "processed_urls": [...],
  "processed_images": [...],
  "error": null
}
```

### GET `/health`
Health check endpoint

### GET `/`
API information and feature list

## 🖼️ Image Processing Capabilities

The API automatically:

1. **Extracts Images** from email content using regex patterns
2. **Validates Safety** of image URLs with domain checks
3. **Searches Google** for image-related content
4. **Fetches Web Content** from image URLs when possible
5. **Processes QR Codes** and other image formats
6. **Chains Tools** automatically for comprehensive analysis

### Supported Image Formats
- JPG/JPEG, PNG, GIF, BMP, WebP, SVG, ICO
- Image URLs with query parameters
- URLs containing `/image`, `/img`, `/photo` paths

## 🖥️ Command-Line Interface

### Using main.py

The enhanced `main.py` now supports image processing through the command line:

#### Interactive Chat Mode
```bash
python main.py --chat
```

#### Single Message Processing
```bash
# Process the specific prompt you mentioned
python main.py --message "read my 1st email and process image"

# Extract images from emails
python main.py --message "Extract images from my emails"

# Process QR codes
python main.py --message "Process QR codes in my inbox"
```

#### Command-Line Options
```bash
python main.py --help
```

**Available Options:**
- `--chat`: Start interactive chat mode
- `--message "your prompt"`: Process a single message
- `--max-urls 5`: Maximum URLs to process (default: 3)
- `--max-images 5`: Maximum images to process (default: 3)
- `--enable-tool-chaining`: Enable automatic tool chaining (default: True)
- `--process-images`: Enable image processing from emails (default: True)

#### Examples with Parameters
```bash
# Process first email with image processing, limit to 5 URLs and 3 images
python main.py --message "read my 1st email and process image" --max-urls 5 --max-images 3

# Extract images with custom limits
python main.py --message "Extract images from my emails" --max-images 10 --process-images

# Disable image processing if not needed
python main.py --message "Check my emails" --process-images false
```

### Testing the Integration

Run the integration test script:
```bash
python test_main_integration.py
```

This will test:
- Command-line interface functionality
- Image processing integration
- Local function testing
- Various prompt formats

## 🔗 Tool Chaining Flow

```
User Request → Gmail Tool → Extract Content → Process Images/URLs → Google Search → Web Access → Response
```

1. **Gmail Tool**: Fetches email messages
2. **Content Extraction**: Finds images and URLs in email body
3. **Image Processing**: Searches Google for image analysis
4. **URL Processing**: Visits websites and extracts content
5. **Response Assembly**: Combines all results into comprehensive response

## 🧪 Testing

Run the test script to verify functionality:

```bash
python test_image_processing.py
```

This will test:
- Local image extraction
- API endpoint functionality
- Image processing capabilities
- Tool chaining

## 🔒 Security Features

- **Domain Whitelisting**: Safe domains are pre-approved
- **Blocked Domains**: Known malicious domains are blocked
- **Pattern Detection**: Suspicious URL patterns are flagged
- **Local IP Blocking**: Internal/localhost URLs are blocked
- **File Extension Filtering**: Dangerous file types are blocked

## 📝 Prompt Examples

The API recognizes various prompt formats:

- `"read my 1st email and process image"`
- `"check emails for images and URLs"`
- `"process QR codes in my inbox"`
- `"read emails and visit websites"`
- `"extract images from latest email"`

## 🚨 Error Handling

The API gracefully handles:
- MCP tool failures
- Invalid URLs
- Network timeouts
- Malformed email content
- Security violations

## 🔄 Dependencies

- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation
- **httpx**: HTTP client
- **MCP Client**: Tool integration

## 📞 Support

For issues or questions:
1. Check the `/health` endpoint
2. Review server logs for errors
3. Verify MCP server connectivity
4. Test with the provided test script

## 🔮 Future Enhancements

- OCR for image text extraction
- Advanced image analysis (AI-powered)
- Batch processing capabilities
- Real-time email monitoring
- Enhanced security features 