import os
import subprocess
import asyncio
from typing import Dict, Any

from api_clients import (
    _google_search,
    _slack_send_message,
    _maps_geocode,
    _google_calendar_events,
    _google_calendar_create_event,
    _gmail_messages,
    _gmail_send_message,
    _gmail_summarize_and_send,
    _drive_search,
    _drive_retrieve,
    _wikipedia_get_page,
    _web_access_get_content,
)

class MCPClient:
    def __init__(self):
        self.servers = {}
        self.processes = {}

    async def connect_to_servers(self):
        """Connect to all MCP servers"""
        try:
            print("🚀 Connecting to MCP servers...")

            self.servers = {
                "gmail": "unknown",
                "maps": "unknown",
                "slack": "unknown",
                "calendar": "unknown",
                "google": "unknown",
                "drive": "unknown",
                "wikipedia": "unknown",
                "web_access": "unknown",
            }

            await self._connect_gmail_mcp_server()
            await self._connect_maps_mcp_server()
            await self._connect_slack_mcp_server()
            await self._connect_calendar_mcp_server()
            await self._connect_google_mcp_server()
            await self._connect_drive_mcp_server()

            print("✅ MCP server connections completed")

        except Exception as error:
            print(f"❌ Error connecting to MCP servers: {error}")
            for server_name in self.servers:
                if self.servers[server_name] == "unknown":
                    self.servers[server_name] = "api_only"

    async def _connect_gmail_mcp_server(self):
        try:
            print(f"🔍 Attempting to connect to Gmail MCP server...")
            if not self._check_npx():
                self.servers["gmail"] = "api_only"
                return

            # Force API-only mode for now to avoid MCP server issues
            print(f"💡 Using direct Gmail API calls instead of MCP server")
            self.servers["gmail"] = "api_only"
            return

            env = os.environ.copy()
            if os.getenv("GOOGLE_ACCESS_TOKEN"):
                env["GOOGLE_ACCESS_TOKEN"] = os.getenv("GOOGLE_ACCESS_TOKEN")

            process = subprocess.Popen(
                ["npx", "@gongrzhe/server-gmail-autoauth-mcp"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
            )
            await asyncio.sleep(2)
            if process.poll() is None:
                self.processes["gmail"] = process
                self.servers["gmail"] = "connected"
                print(f"✅ Connected to Gmail MCP server")
            else:
                print(f"⚠️ Gmail MCP server failed to start")
                self.servers["gmail"] = "api_only"
        except Exception as error:
            print(f"⚠️ Gmail MCP server package not found: {error}")
            print(f"💡 Using direct Gmail API calls instead.")
            self.servers["gmail"] = "api_only"

    async def _connect_maps_mcp_server(self):
        try:
            print(f"🔍 Attempting to connect to Maps MCP server...")
            if not self._check_npx():
                self.servers["maps"] = "api_only"
                return

            # Force API-only mode for now to avoid MCP server issues
            print(f"💡 Using direct Maps API calls instead of MCP server")
            self.servers["maps"] = "api_only"
            return

            env = os.environ.copy()
            if os.getenv("GOOGLE_API_KEY"):
                env["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

            process = subprocess.Popen(
                ["npx", "@modelcontextprotocol/server-google-maps"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
            )
            await asyncio.sleep(2)
            if process.poll() is None:
                self.processes["maps"] = process
                self.servers["maps"] = "connected"
                print(f"✅ Connected to Maps MCP server")
            else:
                print(f"⚠️ Maps MCP server failed to start")
                self.servers["maps"] = "api_only"
        except Exception as error:
            print(f"⚠️ Maps MCP server package not found: {error}")
            print(f"💡 Using direct Maps API calls instead.")
            self.servers["maps"] = "api_only"

    async def _connect_slack_mcp_server(self):
        try:
            print(f"🔍 Attempting to connect to Slack MCP server...")
            if not self._check_npx():
                self.servers["slack"] = "api_only"
                return

            # Force API-only mode for now to avoid MCP server issues
            print(f"💡 Using direct Slack API calls instead of MCP server")
            self.servers["slack"] = "api_only"
            return

            env = os.environ.copy()
            if os.getenv("SLACK_BOT_TOKEN"):
                env["SLACK_BOT_TOKEN"] = os.getenv("SLACK_BOT_TOKEN")
            if os.getenv("SLACK_APP_TOKEN"):
                env["SLACK_APP_TOKEN"] = os.getenv("SLACK_APP_TOKEN")
            if os.getenv("SLACK_SIGNING_SECRET"):
                env["SLACK_SIGNING_SECRET"] = os.getenv("SLACK_SIGNING_SECRET")

            process = subprocess.Popen(
                ["npx", "slack-mcp-server"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
            )
            await asyncio.sleep(2)
            if process.poll() is None:
                self.processes["slack"] = process
                self.servers["slack"] = "connected"
                print(f"✅ Connected to Slack MCP server")
            else:
                print(f"⚠️ Slack MCP server failed to start")
                self.servers["slack"] = "api_only"
        except Exception as error:
            print(f"⚠️ Slack MCP server package not found: {error}")
            print(f"💡 Using direct Slack API calls instead.")
            self.servers["slack"] = "api_only"

    async def _connect_calendar_mcp_server(self):
        try:
            print(f"🔍 Attempting to connect to Calendar MCP server...")
            if not self._check_npx():
                self.servers["calendar"] = "api_only"
                return

            # Force API-only mode for now to avoid MCP server issues
            print(f"💡 Using direct Calendar API calls instead of MCP server")
            self.servers["calendar"] = "api_only"
            return

            env = os.environ.copy()
            if os.getenv("GOOGLE_ACCESS_TOKEN"):
                env["GOOGLE_ACCESS_TOKEN"] = os.getenv("GOOGLE_ACCESS_TOKEN")

            process = subprocess.Popen(
                ["npx", "@teamsparta/mcp-server-google-calendar"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
            )
            await asyncio.sleep(2)
            if process.poll() is None:
                self.processes["calendar"] = process
                self.servers["calendar"] = "connected"
                print(f"✅ Connected to Calendar MCP server")
            else:
                print(f"⚠️ Calendar MCP server failed to start")
                self.servers["calendar"] = "api_only"
        except Exception as error:
            print(f"⚠️ Calendar MCP server package not found: {error}")
            print(f"💡 Using direct Calendar API calls instead.")
            self.servers["calendar"] = "api_only"

    async def _connect_google_mcp_server(self):
        try:
            print(f"🔍 Attempting to connect to Google Search MCP server...")
            if not self._check_npx():
                self.servers["google"] = "api_only"
                return

            # Force API-only mode for now to avoid MCP server issues
            print(f"💡 Using direct Google Search API calls instead of MCP server")
            self.servers["google"] = "api_only"
            return

            env = os.environ.copy()
            if os.getenv("GOOGLE_API_KEY"):
                env["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
            if os.getenv("GOOGLE_CSE_ID"):
                env["GOOGLE_CSE_ID"] = os.getenv("GOOGLE_CSE_ID")

            process = subprocess.Popen(
                ["npx", "@modelcontextprotocol/server-google"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
            )
            await asyncio.sleep(2)
            if process.poll() is None:
                self.processes["google"] = process
                self.servers["google"] = "api_only"
                print(f"✅ Connected to Google Search MCP server")
            else:
                print(f"⚠️ Google Search MCP server failed to start")
                self.servers["google"] = "api_only"
        except Exception as error:
            print(f"⚠️ Google Search MCP server package not found: {error}")
            print(f"💡 Using direct Google Search API calls instead.")
            self.servers["google"] = "api_only"

    async def _connect_drive_mcp_server(self):
        try:
            print(f"🔍 Attempting to connect to Google Drive MCP server...")
            if not self._check_npx():
                self.servers["drive"] = "api_only"
                return

            env = os.environ.copy()
            if os.getenv("GOOGLE_ACCESS_TOKEN"):
                env["GOOGLE_ACCESS_TOKEN"] = os.getenv("GOOGLE_ACCESS_TOKEN")

            process = subprocess.Popen(
                ["npx", "@isaacphi/mcp-gdrive"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
            )
            await asyncio.sleep(2)
            if process.poll() is None:
                self.processes["drive"] = process
                self.servers["drive"] = "connected"
                print(f"✅ Connected to Google Drive MCP server")
            else:
                print(f"⚠️ Google Drive MCP server failed to start")
                self.servers["drive"] = "api_only"
        except Exception as error:
            print(f"⚠️ Google Drive MCP server package not found: {error}")
            print(f"💡 Using direct Google Drive API calls instead.")
            self.servers["drive"] = "api_only"

    def _check_npx(self):
        try:
            subprocess.run(["npx", "--version"], capture_output=True, check=True)
            print(f"✅ npx found in system PATH")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"⚠️ npx not found in system PATH")
            return False

    async def call_tool(self, server_name: str, tool_name: str, params: Dict[str, Any]):
        """Call a tool on an MCP server or fallback to direct API"""
        server_status = self.servers.get(server_name, "unknown")
        print(f"🔍 Debug: Server {server_name} status: {server_status}")

        if server_status == "connected":
            print(f"Using MCP for {server_name}...")
            # For this example, we always fallback to the direct API,
            # as the original code's MCP-connected paths were not fully implemented.
            pass

        if server_name == "gmail":
            if tool_name == "get_messages":
                return await _gmail_messages(params.get("query"), params.get("max_results", 10))
            elif tool_name == "send_message":
                return await _gmail_send_message(params.get("to"), params.get("subject"), params.get("body"))
            elif tool_name == "summarize_and_send":
                return await _gmail_summarize_and_send(params.get("target_email"), params.get("max_emails", 10))
            else:
                raise HTTPException(status_code=404, detail=f"Unknown Gmail tool: {tool_name}")
        
        elif server_name == "calendar":
            if tool_name == "get_events":
                return await _google_calendar_events(params.get("time_min"), params.get("time_max"), params.get("max_results", 10))
            elif tool_name == "create_event":
                return await _google_calendar_create_event(params.get("summary"), params.get("start_time"), params.get("end_time"), params.get("description", ""))
            else:
                raise HTTPException(status_code=404, detail=f"Unknown Calendar tool: {tool_name}")

        elif server_name == "google":
            if tool_name == "search":
                return await _google_search(params.get("query", ""))
            else:
                raise HTTPException(status_code=404, detail=f"Unknown Google tool: {tool_name}")

        elif server_name == "maps":
            if tool_name == "geocode":
                return await _maps_geocode(params.get("address", ""))
            else:
                raise HTTPException(status_code=404, detail=f"Unknown Maps tool: {tool_name}")

        elif server_name == "slack":
            if tool_name == "send_message":
                return await _slack_send_message(params.get("channel", ""), params.get("text", ""))
            else:
                raise HTTPException(status_code=404, detail=f"Unknown Slack tool: {tool_name}")

        elif server_name == "drive":
            if tool_name == "search":
                return await _drive_search(params.get("query", ""))
            elif tool_name == "retrieve":
                return await _drive_retrieve(params.get("target_file", ""))
            else:
                raise HTTPException(status_code=404, detail=f"Unknown Drive tool: {tool_name}")
        
        elif server_name == "wikipedia":
            if tool_name == "get_page":
                return await _wikipedia_get_page(params.get("title", ""), params.get("url"))
            else:
                raise HTTPException(status_code=404, detail=f"Unknown Wikipedia tool: {tool_name}")

        elif server_name == "web_access":
            if tool_name == "get_content":
                return await _web_access_get_content(params.get("url", ""))
            else:
                raise HTTPException(status_code=404, detail=f"Unknown Web Access tool: {tool_name}")

        else:
            raise HTTPException(status_code=404, detail=f"Server {server_name} not configured")

    async def disconnect(self):
        """Terminate all subprocesses"""
        print("🛑 Disconnecting from MCP servers...")
        for server, process in self.processes.items():
            if process.poll() is None:
                print(f"🛑 Terminating {server} process...")
                process.terminate()
                try:
                    await asyncio.wait_for(self._wait_for_process_exit(process), timeout=5)
                except asyncio.TimeoutError:
                    print(f"🔪 Forcing kill on {server} process...")
                    process.kill()
        self.processes.clear()
        print("✅ Disconnected.")

    async def _wait_for_process_exit(self, process):
        while process.poll() is None:
            await asyncio.sleep(0.1)