from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import mcp.types as types
import asyncio
import mcp_client

# 为 stdio 连接创建服务器参数
server_params = StdioServerParameters(
    command="/Users/cheyipai/.local/bin/uv", # Executable
    args=["run","main.py"], # Optional command line arguments
    env={
        "BIGMODEL_API_KEY": "API Key"
    }
)

async def handle_sampling_message(message: types.CreateMessageRequestParams) -> types.CreateMessageResult:
    """创建一个回调函数，用于处理采样消息"""
    return types.CreateMessageResult(
        role="assistant",
        content=types.TextContent(
            type="text",
            text="Hello, world! from model",
        ),
        model="gpt-3.5-turbo",
        stopReason="endTurn",
    )

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write, sampling_callback=handle_sampling_message) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            for tool in tools:
                print("tool=", tool)

            # Call a tool
            result = await session.call_tool("web_search", arguments={"query": "如何使用GPT?"})
            print("result=", result)

async def main():
    client = mcp_client.MyClient()
    try:
        await client.connect_to_server()
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    # asyncio.run(run())
    asyncio.run(main())