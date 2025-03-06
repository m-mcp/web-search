# Web Search MCP 服务器

这是一个基于 MCP（Model Context Protocol）实现的网络搜索服务器，提供了网络搜索功能的工具接口。

## 项目功能

项目主要提供了一个网络搜索工具，通过调用智谱 AI 的搜索 API 实现搜索功能。主要特点：

- 提供异步网络搜索接口
- 支持错误处理和结果解析
- 使用环境变量配置 API 密钥
- 支持标准输入输出（stdio）作为传输方式

## 技术栈

- Python >= 3.10
- 主要依赖：
  - httpx: 用于异步 HTTP 请求
  - mcp[cli]: MCP 服务器实现
  - python-dotenv: 环境变量管理

## 项目结构

```
.
├── main.py          # 主程序文件，包含 MCP 服务器实现
├── pyproject.toml   # 项目配置和依赖管理
├── .env            # 环境变量配置文件
└── README.md       # 项目文档
```

## 主要组件

### MCP 服务器（main.py）

实现了一个名为 `web-search-server` 的 FastMCP 服务器，提供以下功能：

- `web_search` 工具：
  - 接收搜索查询字符串
  - 调用智谱 AI 的搜索 API
  - 处理 API 响应并返回搜索结果
  - 支持错误处理

### 配置文件

- `pyproject.toml`: 定义项目元数据和依赖
- `.env`: 存储 API 密钥配置

## 使用方法

1. 确保已安装 Python 3.10 或更高版本
2. 配置环境变量：在 `.env` 文件中设置 `BIGMODEL_API_KEY`
3. 安装依赖：使用包管理器安装 `pyproject.toml` 中列出的依赖
4. 运行服务器：执行 `uv run main.py`

## 开发指南

### 开发环境设置

1. 创建并激活 Python 虚拟环境
```bash
uv venv && source .venv/bin/activate  # Unix/macOS
# 或
.venv\Scripts\activate  # Windows
```

2. 安装开发依赖
```bash
uv sync  # 以可编辑模式安装项目
```

### 调试方法

1. 使用 mcp 调试
```bash
mcp dev main.py
```
2. 使用 inspector 调试
```bash
npx -y @modelcontextprotocol/inspector uv run main.py
```

### 开发工作流程

1. 代码修改
   - 遵循异步编程模式
   - 使用类型注解增强代码可读性
   - 保持错误处理的完整性

2. 测试验证
   - 运行测试功能验证改动
   - 检查 API 响应处理
   - 验证错误处理机制

3. 错误处理最佳实践
   - API 调用错误：检查 response 中的 error 字段
   - 网络错误：使用 try-except 捕获 httpx 异常
   - 参数验证：确保查询字符串不为空

4. 性能优化建议
   - 使用 httpx.AsyncClient 的上下文管理器
   - 适当处理并发请求
   - 考虑添加响应缓存机制

### 常见问题排查

1. API 密钥问题
   - 检查 .env 文件是否存在
   - 验证 BIGMODEL_API_KEY 是否正确设置
   - 确认环境变量是否正确加载

2. 网络请求问题
   - 检查网络连接
   - 验证 API 请求 URL 是否正确
   - 查看请求头和参数格式

3. 结果解析问题
   - 检查 API 响应格式是否符合预期
   - 验证 JSON 解析是否正确
   - 确认结果提取逻辑是否正确