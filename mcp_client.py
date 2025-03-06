from contextlib import AsyncExitStack
import json
import os
from typing import Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class MyClient:
    def __init__(self):
        # 创建客户端会话
        self.session: Optional[ClientSession] = None
        # 创建异步上下文管理器
        self.exit_stack = AsyncExitStack()
        self.client = OpenAI()
    
    # 连接到mcp服务
    async def connect_to_server(self):
        server_params = StdioServerParameters(
            command="/Users/cheyipai/.local/bin/uv", # Executable
            args=["run","main.py"], # Optional command line arguments
            env={
                "BIGMODEL_API_KEY": os.getenv("BIGMODEL_API_KEY") if os.getenv("BIGMODEL_API_KEY") else ""
            }
        )
        # 初始化 stdio 客户端
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        read, write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(read, write))

        # 初始化连接
        await self.session.initialize()

    # 处理查询
    async def process_query(self, query: str) -> str:
        system_prompt = (
            "你是一个非常智能的助手，你总是以帮助用户的方式回答问题。"
            "你可用调用函数来搜索网上信息"
            "在搜索时请牢记用户提问的内容,不要丢失用户提问的内容"
            "在回答问题之前请务必调用web_search函数来搜索网络上的信息并根据搜索的结果来总结回答用户的问题"
        )
        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": query,
            }
        ]
        # 获取mcp服务上的工具列表
        response = await self.session.list_tools()

        # 生成工具调用 function_call
        available_tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                }
            }
            for tool in response.tools
        ]

        # 请求AI获取回答
        response = self.client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL"),
            messages=messages,
            tools=available_tools,
        )
        # 处理返回的内容
        content = response.choices[0]
        if content.finish_reason == "tool_calls":
            # 获取工具调用
            tool_call = content.message.tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            print("tool_name=", tool_name, "tool_args=", tool_args)
            # 执行工具
            tool_result = await self.session.call_tool(tool_name, tool_args)
            print("tool_result=", tool_result)

            # 将执行结果存入到messages
            messages.append(content.message.model_dump())
            messages.append({
                "role": "tool",
                "content": tool_result.content[0].text,
                "tool_call_id": tool_call.id
            })

            # 将总结的结果再次请求AI获取回答
            response = self.client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL"),
                messages=messages,
            )
            return response.choices[0].message.content
        
        return content.message.content

    # 循环聊天
    async def chat_loop(self):
        while True:
            try:
                query = input("\n请输入问题：").strip()
                if query.lower() == "exit" or query.lower() == "quit":
                    break
                response = await self.process_query(query)
                print(f"\n {response}")
            except Exception as e:
                print(f"Error: {e}")
                import traceback
                traceback.print_exc()
    
    async def cleanup(self):
        """ 清空资源 """
        await self.exit_stack.aclose()