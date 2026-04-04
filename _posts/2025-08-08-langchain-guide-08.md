---
layout: post
title: "08. 解锁AI潜能：DeepSeek与LangChain的MCP客户端教程"
categories: ["MCP", "LangChain", "AI"]
description: "> Model-Control-Protocol (MCP) 是一个开放标准，用于定义大型语言模型如何与外部工具和服务进行通信。本文将详细介绍如何使用DeepSeek与MCP进行集成，并且如何和mcp.so 大量的mcp服务进行集成，..."
keywords: "MCP, LangChain, AI, DeepSeek, 08. 解锁AI潜能：DeepSeek与LangChain的MCP客户端教程"
mermaid: false
sequence: false
flow: false
mathjax: false
mindmap: false
mindmap2: false
---
> Model-Control-Protocol (MCP) 是一个开放标准，用于定义大型语言模型如何与外部工具和服务进行通信。本文将详细介绍如何使用DeepSeek与MCP进行集成，并且如何和mcp.so 大量的mcp服务进行集成，实现功能强大的AI应用。
> 

## 为什么选择MCP？

在当今的AI开发中，如何让大模型高效调用外部工具和服务是一个关键问题。MCP协议通过标准化的通信方式，解决了这一难题。它的优势包括：

- **灵活性**：支持多种传输机制（如stdio和SSE）
- **可扩展性**：轻松集成多个工具和服务
- **高效性**：优化了大模型与外部工具的交互流程

通过本文，你将学会如何使用MCP协议扩展AI应用的能力。

## 快速入门

首先，我们需要安装必要的Python库，以支持MCP客户端和DeepSeek大模型的集成。

```python
%%capture #避免显示pip安装信息
%pip install langchain-mcp-adapters langchain-deepseek python-dotenv langgraph fastmcp

```

## 构建你的第一个MCP服务器

> 参考：https://github.com/langchain-ai/langchain-mcp-adapters
> 

在深入了解客户端前，我们先了解如何创建自定义MCP服务器，这将为我们提供与大模型交互的工具。

### 数学运算服务器示例

下面是一个简单的数学运算MCP服务器示例，它提供两个基本工具：加法和乘法。

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

if __name__ == "__main__":
    mcp.run(transport="stdio")

```

这个简单的服务器定义了两个数学工具，并通过stdio传输机制运行，这便于在同一进程内进行通信。

## 深入探索MCP客户端

客户端是与MCP服务器交互的关键部分，它能让我们的大模型有效地使用外部工具。下面我们将详细介绍如何构建和使用MCP客户端。

### 客户端连接与工具加载

```python
# 导入必要的库
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent

from langchain_deepseek import ChatDeepSeek

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# 初始化DeepSeek模型
model = ChatDeepSeek(model="deepseek-chat")

# 设置服务器参数 - 通过stdio连接
server_params = StdioServerParameters(
    command="python",
    # 确保更新为你的math_server.py文件的完整绝对路径
    args=["./math_server.py"],
)

# 异步方式连接服务器并执行任务
async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        # 初始化连接
        await session.initialize()

        # 获取可用工具
        tools = await load_mcp_tools(session)

        # 创建并运行代理
        agent = create_react_agent(model, tools)
        agent_response = await agent.ainvoke({"messages": "what's (3 + 5) x 12?"})
        print("Answer:", agent_response)

```

### 工作流程解析

在上面的代码中，我们完成了以下步骤：

1. **初始化连接**：使用`stdio_client`和`ClientSession`建立与MCP服务器的连接
2. **加载工具**：通过`load_mcp_tools`获取服务器提供的工具
3. **创建代理**：使用`create_react_agent`将大模型与工具集成
4. **执行查询**：通过`ainvoke`方法执行用户查询

当我们向代理发送"what's (3 + 5) x 12?"的问题时，代理会：

- 首先使用"add"工具计算3 + 5 = 8
- 然后使用"multiply"工具计算8 × 12 = 96
- 最后返回完整的计算过程和结果

## 集成多个MCP服务器

在实际应用中，我们可能需要集成多个不同功能的MCP服务器。下面我们将添加一个天气服务器作为示例。

### 天气服务器示例

```python
# 添加WeatherMCP
from typing import List
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather")

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather for location."""
    return "It's always sunny in New York"

if __name__ == "__main__":
    mcp.run(transport="sse")

```

### 多服务器客户端实现

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

from langchain_deepseek import ChatDeepSeek

model = ChatDeepSeek(model="deepseek-chat")

async with MultiServerMCPClient(
    {
        "math": {
            "command": "python",
            # Make sure to update to the full absolute path to your math_server.py file
            "args": ["./math_server.py"],
            "transport": "stdio",
        },
        "weather": {
            # make sure you start your weather server on port 8000
            "url": "<http://localhost:8000/sse>",
            "transport": "sse",
        }
    }
) as client:
    agent = create_react_agent(model, client.get_tools())
    math_response = await agent.ainvoke({"messages": "what's (3 + 5) x 12?"})
    print(math_response["messages"][-1]["content"])
    # The result of ((3 + 5) x 12) is (96).

    weather_response = await agent.ainvoke({"messages": "what is the weather in nyc?"})
    print(weather_response["messages"][-1]["content"])
    # The weather in New York City is sunny!

```

估计大家也都发现了，两个MCP Server分别用了不同的transport方式:`stdio`和`sse`。 它们是客户端-服务器通信的两种默认标准传输机制。

**1、stdio（标准输入输出）**

适用于客户端与服务端在同一台机器上的场景。

客户端通过启动服务端子进程（如命令行工具），利用操作系统的管道机制（stdin/stdout）进行数据传输。

是个同步阻塞模型，通信基于顺序处理，需等待前一条消息完成传输后才能处理下一条，适合简单的本地批处理任务。

**2、HTTP with SSE（Server-Sent Events）**

客户端与服务端可部署在不同节点，通过HTTP协议实现跨网络通信。

是个异步事件驱动。

服务端通过SSE长连接主动推送数据，

客户端通过HTTP POST端点发送请求，

支持实时或准实时交互，适合分布式系统或需要高并发的场景。

| 特性 | stdio | HTTP with SSE |
| --- | --- | --- |
| 协议基础 | 操作系统管道 | HTTP/1.1长连接 |
| 消息格式 | JSON-RPC 2.0，以换行符分隔 | JSON-RPC	2.0，通过SSE事件流传输 |
| 连接方向 | 双向（客户端↔服务端） | 客户端通过POST发送请求，服务端通过SSE单向推送响应 |
| 错误处理 | 依赖管道机制 | 支持HTTP状态码和SSE自动重连机制 |
| 适用场景 | 本地工具链、CLI应用 | 分布式系统、实时监控、远程服务调用 |

## 对接 [mcp.so](http://mcp.so/)

> 注意: 使用 npx 需要安装 npm，
> 
> - macOS上使用 `brew install npm`
> - Windows上需要下载 [Node.js](https://nodejs.org/en/download/)，然后安装 `npm`
> - Linux上使用 `sudo npm install -g npx`

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

from langchain_deepseek import ChatDeepSeek
import os
import json
from dotenv import load_dotenv

load_dotenv()

model = ChatDeepSeek(model="deepseek-chat")

async with MultiServerMCPClient(
    {
        "tavily-mcp": {
            "command": "npx",
            "args": [
                "-y",
                "tavily-mcp@0.1.4"
            ],
            "env": {
                "TAVILY_API_KEY": os.getenv("TAVILY_API_KEY")
            },
            "autoApprove": [],
            "name": "tavily-mcp"
        },
        "amap-maps": {
            "command": "npx",
            "args": [
                "-y",
                "@amap/amap-maps-mcp-server"
            ],
            "env": {
                "AMAP_MAPS_API_KEY": os.getenv("AMAP_MAPS_API_KEY")
            }
        }
    }
) as client:
    agent = create_react_agent(model, client.get_tools())
    web_search_response = await agent.ainvoke({"messages": "2025年4月有哪些AI的重大新闻？"})
    print(f"原始返回内容：{web_search_response}")
    print(web_search_response["messages"][-1].content)
    print("------------------------------------------------------")
    gaode_lbs_response = await agent.ainvoke({"messages": "请帮我规划一条从北京到上海的自驾游路线，途经南京和杭州，时间为3天，尽量避开拥堵的路段"})
    print(f"原始返回内容：{gaode_lbs_response}")
    print(gaode_lbs_response["messages"][-1].content)

```

### 返回内容：

原始返回内容：
......

2025年4月，AI领域发生了多起重大新闻事件，以下是部分关键内容：

1. **GSMA MWC上海大会聚焦AI与5G商业化**
    - 2025年GSMA MWC上海大会展示了AI与5G技术的创新突破，华为、中兴、小米等270家企业展示了AI、5G及物联网领域的最新成果。
    - [详情链接](https://news.sina.com.cn/zx/ds/2025-04-11/doc-inestvsi2877509.shtml)
2. **长安汽车与腾讯深化智能合作**
    - 长安汽车与腾讯于4月10日签署深化合作协议，共同推进智能化数据体系建设，加速汽车智能化发展。
    - [详情链接](https://news.sina.com.cn/zx/ds/2025-04-11/doc-inestvsi2877509.shtml)
3. **开源AI项目“小智AI”引发热潮**
    - 基于乐鑫ESP32芯片的开源AI硬件项目“小智AI”因其低门槛和情感化交互特性，两个月内接入设备激增10万台，带动芯片和文创产业链发展。
    - [详情链接](https://news.sina.com.cn/zx/ds/2025-04-11/doc-inestvsi2877509.shtml)
4. **联合国报告：AI市场将达4.8万亿美元**
    - 联合国预测到2033年AI市场规模将达4.8万亿美元，但需警惕技术资源集中和全球不平等问题。
    - [详情链接](https://news.un.org/zh/story/2025/04/1137251)
5. **高盛发布AI预测报告**
    - 高盛结合财报与市场动态，分析了AI在2025年的发展趋势和投资机会。
    - [详情链接](https://www.moomoo.com/hans/community/feed/114336466862089)
6. **开源大模型Skywork-OR1发布**
    - 明万维推出完全开源且免费使用的Skywork-OR1系列大模型，旨在降低企业使用AI技术的门槛。
    - [详情链接](https://news.sina.com.cn/zx/ds/2025-04-14/doc-inetanuy2077574.shtml)

## 这些新闻展示了AI技术在商业化、开源生态、国际合作等方面的快速发展。如果需要更详细的内容，可以点击相关链接查看。

原始返回内容：

......

以下是从北京到上海的自驾游路线规划，途经南京和杭州，总行程约3天，尽量避开拥堵路段：

### **第一天：北京 → 南京**

- **距离**：约1005公里
- **预计时间**：约11小时
- **主要路线**：
    1. 从北京市出发，沿G3京台高速向南行驶。
    2. 途经天津、河北、山东、江苏，最终到达南京。
- **建议**：
    - 早晨6点前出发，避开早高峰。
    - 在山东境内可选择G2京沪高速作为备选路线，避开G3京台高速的拥堵。

### **第二天：南京 → 杭州**

- **距离**：约280公里
- **预计时间**：约3小时
- **主要路线**：
    1. 从南京出发，沿G25长深高速向南行驶。
    2. 途经湖州，最终到达杭州。
- **建议**：
    - 上午9点后出发，避开南京早高峰。
    - 在杭州可选择绕城高速避开市区拥堵。

### **第三天：杭州 → 上海**

- **距离**：约175公里
- **预计时间**：约2.5小时
- **主要路线**：
    1. 从杭州出发，沿S2杭甬高速向东北行驶。
    2. 途经嘉兴，最终到达上海。
- **建议**：
    - 早晨7点前出发，避开杭州早高峰。
    - 进入上海后，选择外环高速避开市区拥堵。

### **注意事项**

1. **避开高峰时段**：尽量在早晨6点前或晚上8点后行驶，避开早晚高峰。
2. **实时导航**：使用导航软件（如高德、百度地图）实时查看路况，及时调整路线。
3. **休息点**：每2-3小时在服务区休息一次，避免疲劳驾驶。
4. **天气**：提前查看沿途天气，避免恶劣天气影响行程。

如果需要更详细的路线或实时路况更新，可以随时告诉我！

## 07. 最佳实践与应用场景

### 7.1 企业级应用场景

MCP客户端的灵活性使它适用于各种企业应用场景：

1. **客户服务自动化**：集成CRM系统，提供智能客服能力
2. **数据分析辅助**：连接数据库和分析工具，协助数据分析师工作
3. **知识管理系统**：接入企业知识库，实现智能知识检索和问答
4. **流程自动化**：与工作流系统集成，实现业务流程的智能决策

### 开发小贴士

1. **错误处理**：始终包含适当的错误处理机制，特别是处理工具调用失败的情况
2. **超时管理**：设定合理的超时时间，避免长时间等待外部服务响应
3. **日志记录**：记录所有工具调用和响应，便于调试和审计
4. **权限控制**：实施适当的权限控制，确保敏感操作的安全性

## 总结与展望

通过本文，我们了解了如何使用MCP协议扩展大模型的能力范围。MCP作为一种标准化的工具调用协议，使大模型能够无缝调用外部服务，显著增强了AI系统的实用性和灵活性。

DeepSeek与MCP的结合，不仅提高了大模型解决实际问题的能力，还为开发者提供了一种标准化的方式来扩展AI应用功能。随着更多工具和服务加入MCP生态系统，我们可以期待看到更多创新的AI应用场景。

希望本教程对你有所帮助，欢迎在评论区分享你的使用体验或问题！
