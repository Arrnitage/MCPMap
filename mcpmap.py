from typing import Optional
from mcp.client.sse import sse_client
from mcp import ClientSession
import argparse
import asyncio
import sys

class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self._streams_context = None
        self._session_context = None

    async def connect_to_sse_server(self, server_url: str):
        """Connect to an MCP server running with SSE transport"""
        self._streams_context = sse_client(url=server_url)
        streams = await self._streams_context.__aenter__()

        self._session_context = ClientSession(*streams)
        self.session = await self._session_context.__aenter__()

        # Initialize
        await self.session.initialize()

        # List available tools to verify connection
        print("Initialized SSE client...")

    async def enum_mcp_server(self):
        print("Listing tools")
        response = await self.session.list_tools()
        tools = getattr(response, "tools", [])

        for tool in tools:
            print(f"Tool name: {getattr(tool, 'name', '')}")
            print(f"Description: {getattr(tool, 'description', '')}")
            print(f"InputSchema: {getattr(tool, 'inputSchema', '')}")
            print(f"Model config: {getattr(tool, 'model_config', '')}")

        print("Listing resources")
        response = await self.session.list_resources()
        resources = getattr(response, 'resources', [])

        for resource in resources:
            print(f"Resource name: {getattr(resource, 'name', '')}")
            print(f"MIME type: {getattr(resource, 'mimeType', '')}")
            uri = getattr(resource, 'uri', '')
            print(f"URI: {uri}")
            response = await self.session.read_resource(uri)
            contents = getattr(response, 'contents', [])

            for content in contents:
                print(f"Content: {getattr(content, 'text', '')}")


        print("Listing Prompts")
        response = await self.session.list_prompts()
        prompts = getattr(response, "prompts", [])
        
        for prompt in prompts:
            # TODO: List Prompts
            pass

    async def fuzz_tool(self, tool_name: str):
        print("Fuzzing tool")
        # TODO
        # response = self.session.call_tool(tool_name, )
        pass

    async def close(self):
        # Properly close async context managers if they exist
        if self.session and self._session_context:
            await self._session_context.__aexit__(None, None, None)
            self.session = None
        if self._streams_context:
            await self._streams_context.__aexit__(None, None, None)
            self._streams_context = None

async def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("method", help="enum or fuzz")
    parser.add_argument("--sse", required=True, help="MCP SSE server address")

    args = parser.parse_args()

    client = MCPClient()
    try:
        await client.connect_to_sse_server(server_url=args.sse)
        if args.method == "enum":
            await client.enum_mcp_server()

        if args.method == "fuzz":
            # TODO
            pass
    finally:
        await client.close()

if __name__ == '__main__':
    asyncio.run(main())