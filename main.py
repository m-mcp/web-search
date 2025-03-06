import os
import uuid
from mcp.server.fastmcp import FastMCP
import httpx
from dotenv import load_dotenv

# 创建服务器
server = FastMCP("we-search-server")

# 加载环境变量
load_dotenv()

@server.tool()
async def web_search(query: str) -> str:
    """
    Search the web for information.
    Args:
        query (str): The query to search for.
    Returns:
        str: The result of the search.
    """
    async with httpx.AsyncClient() as client:
        # 从环境中获取api key
        api_key = os.getenv("BIGMODEL_API_KEY") or ""
        response = await client.post(
            "https://open.bigmodel.cn/api/paas/v4/tools", 
            headers={ 'Authorization': api_key},
            json={
                "request_id": str(uuid.uuid4()),
                "tool": "web-search-pro",
                "messages": [
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "stream": False
            }
        )
        # 解析返回结果
        res_data = []
        response = response.json()
        
        # 处理异常
        if "error" in response:
            error_message = response["error"]["message"]
            return "Error: " + error_message
        
        # 处理正常逻辑
        for choice in response.get("choices", []):
            messages = choice.get("message", {})
            for tool_call in messages.get("tool_calls", []):
                # 检查 'search_result' 是否存在于 tool_call 中
                if "search_result" in tool_call:
                    search_results = tool_call["search_result"]
                    res_data.extend(result["content"] for result in search_results if result.get("content"))
        return res_data

def test_main():
    """
    Test the web search tool.
    """
    async def test_web_search():
        res = await web_search("如何使用GPT?")
        # print(res)

    import asyncio  # 添加: 导入asyncio模块
    asyncio.run(test_web_search())  # 添加: 使用asyncio.run来运行异步test函数


def main():
    server.run(transport='stdio')

if __name__ == "__main__":
   # 运行
   main()
   # 测试功能
   # test_main()