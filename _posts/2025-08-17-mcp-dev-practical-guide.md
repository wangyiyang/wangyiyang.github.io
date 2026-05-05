---
layout: post
title: "MCP 开发实战：从入门到企业级应用"
categories: [AI, MCP, 教程]
description: "完整讲解 MCP 开发的实战技能，从 Function Calling 的痛点到 MCP 协议的统一标准，再到企业级部署方案。"
keywords: MCP, Model Context Protocol, Function Calling, AI工具集成, 企业级部署
mermaid: true
sequence: false
flow: false
mathjax: false
mindmap: false
mindmap2: false
---

# MCP 开发实战：从入门到企业级应用

## 引言：为什么 MCP 是 AI 工具集成的未来

在做 AI 应用开发时，最头疼的是什么？不是模型调优，不是 prompt 工程，而是**工具集成**。

在 MCP 出现之前，我们主要依赖 **Function Calling** 机制——OpenAI 在 2023 年推出的技术。虽然它解决了 AI 调用工具的基本需求，但痛点也很明显：每个 AI 平台的实现都不一样，同样的业务逻辑要为不同平台写多套代码，维护成本随着平台数量线性增长。

直到我遇到了 **MCP（Model Context Protocol）**，这个由 Anthropic 开源的标准协议，彻底改变了 AI 工具集成的游戏规则。你可以把它理解为"AI 工具集成的 USB-C 标准"：写一次 MCP 服务器，所有支持 MCP 的 AI 都能用。

本教程将从入门到企业级应用，完整讲解 MCP 开发的实战技能。无论你是想快速搭建个人项目，还是构建生产级的企业系统，这篇文章都能给你清晰的指引。

---

## 第一部分：MCP 基础与核心价值

### Function Calling 时代的集成噩梦

Function Calling 虽然解决了 AI 调用工具的基本需求，但每个平台的实现方式都不一样：

- **OpenAI**：标准的 functions 参数，JSON schema 格式
- **Qwen**：自定义的 tool_use 格式，参数结构不同
- **ChatGLM**：各种自定义实现，兼容性一塌糊涂

我之前给一个公司做智能客服，让 AI 访问一些平台的接口。结果光是这一个功能，就要写三套 Function Calling 实现。虽然代码是一样的，但是要维护三个地方，每次数据结构一变，三个地方都要改。

更要命的是本地模型的适配噩梦。我们系统主要使用 **Qwen 2.5 72B 模型**，通过 vLLM 进行推理，应用层用 LangChain 的 OpenAI SDK 调用。听起来很标准对吧？但实际上，Qwen 模型的工具调用格式和 OpenAI 的标准还是有不少差异：

**OpenAI 标准格式**：
```json
{
  "tool_calls": [
    {
      "id": "call_abc123",
      "type": "function",
      "function": {
        "name": "query_user",
        "arguments": "{\"user_id\": \"12345\"}"
      }
    }
  ]
}
```

**Qwen 2.5 实际输出格式**：
```text
Action: query_user
Action Input: {"user_id": "12345"}
```

你看，Qwen 用的是完全不同的文本格式，而不是 JSON 结构。更要命的是，Qwen 还经常输出一些不规范的 JSON——单引号、缺少结束括号等等。为了处理这些格式差异，我们不得不写大量适配代码，包括正则表达式解析、JSON 格式修复、键名转换、错误兜底处理。明明同样的业务功能，就因为格式不统一，要写 100 多行适配代码。

### MCP 协议：统一 AI 数据访问的游戏规则

MCP 通过统一标准彻底解决了这个问题。它的核心架构思维是：**AI 模型只需要理解 MCP 协议，不需要关心具体的工具实现；工具开发者只需要实现业务逻辑，不需要关心 AI 模型差异**。

```mermaid
graph TD
    subgraph "Function Calling 时代 - N×M 复杂度"
        A1[OpenAI] --> B1[业务系统 1]
        A1 --> B2[业务系统 2]
        A2[Claude] --> B1
        A2 --> B2
        A3[本地模型] --> B1
        A3 --> B2
        style A1 fill:#ff9999
        style A2 fill:#ff9999
        style A3 fill:#ff9999
    end
```

```mermaid
graph TD
    subgraph "MCP 时代 - N+M 线性复杂度"
        C1[OpenAI] --> D[MCP 协议]
        C2[Claude] --> D
        C3[本地模型] --> D
        D --> E1[业务系统 1]
        D --> E2[业务系统 2]
        style D fill:#99ff99
    end
```

**核心优势**：

1. **一次开发，多平台使用**：写一次 MCP 服务器，OpenAI、Claude、本地模型都能用
2. **标准化数据交换**：统一的消息格式，告别各种适配代码
3. **动态发现能力**：AI 可以自动发现工具有什么功能，不需要手动配置
4. **双向通信**：不仅 AI 能调用工具，工具也能主动推送数据给 AI

### MCP 协议核心概念

MCP 协议定义了三个核心原语：

| 原语 | 作用 | 示例 |
|------|------|------|
| **Resources** | 数据暴露 | 文件、数据库记录、API 响应 |
| **Tools** | 动作执行 | 发送邮件、创建订单、查询数据 |
| **Prompts** | 交互模板 | 结构化提示词、多轮对话模板 |

**Resources** 是只读的，用来让 AI 获取数据。**Tools** 是可执行的，用来让 AI 完成动作。**Prompts** 是交互式的，用来定义标准化的对话流程。

---

## 第二部分：快速入门——搭建你的第一个 MCP 服务器

### 环境准备

```bash
# 安装 Python 3.10+
python --version

# 安装 FastMCP（推荐）
pip install fastmcp

# 或者安装官方 SDK
pip install mcp
```

### 最简单的 MCP 服务器

```python
# server.py
from fastmcp import FastMCP

# 创建 MCP 服务器
mcp = FastMCP("我的第一个服务器")

# 定义一个工具
@mcp.tool()
def add(a: int, b: int) -> int:
    """两个数字相加"""
    return a + b

# 定义一个资源
@mcp.resource("config://app")
def get_config() -> str:
    """获取应用配置"""
    return "{\"version\": \"1.0\", \"name\": \"demo\"}"

# 运行服务器
if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### 配置 Claude Desktop

```json
{
  "mcpServers": {
    "my-first-server": {
      "command": "python",
      "args": ["/path/to/server.py"]
    }
  }
}
```

保存到 `~/Library/Application Support/Claude/claude_desktop_config.json`（Mac）或 `%APPDATA%\Claude\claude_desktop_config.json`（Windows）。

重启 Claude Desktop，你就能在对话中使用 `add` 工具了。

---

## 第三部分：核心功能详解

### Tools：让 AI 执行动作

Tools 是 MCP 最常用的功能。它让 AI 能够执行具体的业务动作。

```python
from fastmcp import FastMCP
from typing import Optional
import sqlite3

mcp = FastMCP("用户管理系统")

# 数据库连接
db = sqlite3.connect("users.db")
db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

@mcp.tool()
def create_user(name: str, email: str) -> dict:
    """
    创建新用户
    
    Args:
        name: 用户姓名
        email: 用户邮箱
    
    Returns:
        包含用户ID和状态的字典
    """
    try:
        cursor = db.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (name, email)
        )
        db.commit()
        return {
            "success": True,
            "user_id": cursor.lastrowid,
            "message": f"用户 {name} 创建成功"
        }
    except sqlite3.IntegrityError:
        return {
            "success": False,
            "error": "邮箱已存在"
        }

@mcp.tool()
def get_user(user_id: int) -> Optional[dict]:
    """根据ID查询用户信息"""
    cursor = db.execute(
        "SELECT * FROM users WHERE id = ?", (user_id,)
    )
    row = cursor.fetchone()
    if row:
        return {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "created_at": row[3]
        }
    return None

@mcp.tool()
def list_users(limit: int = 10) -> list:
    """列出所有用户，支持分页"""
    cursor = db.execute(
        "SELECT * FROM users LIMIT ?", (limit,)
    )
    return [
        {
            "id": row[0],
            "name": row[1],
            "email": row[2]
        }
        for row in cursor.fetchall()
    ]
```

**关键设计原则**：

1. **文档字符串必须详细**：AI 靠文档字符串理解工具功能
2. **类型注解要准确**：帮助 AI 正确构造参数
3. **返回结构化数据**：JSON 格式最友好
4. **错误处理要优雅**：返回错误信息而不是抛异常

### Resources：让 AI 读取数据

Resources 用于暴露只读数据。适合配置文件、数据库记录、文件内容等。

```python
@mcp.resource("users://{user_id}")
def get_user_resource(user_id: str) -> str:
    """获取用户详细信息（资源格式）"""
    user = get_user(int(user_id))
    if user:
        return json.dumps(user, ensure_ascii=False, indent=2)
    return "用户不存在"

@mcp.resource("config://database")
def get_db_config() -> str:
    """数据库配置信息"""
    return json.dumps({
        "type": "sqlite",
        "file": "users.db",
        "pool_size": 5
    }, indent=2)
```

Resources 和 Tools 的区别：

- **Resources**：只读，用于数据查询，AI 会自动缓存
- **Tools**：可写，用于业务操作，每次调用都会执行

### Prompts：标准化交互模板

Prompts 定义可复用的对话模板，适合标准化流程。

```python
@mcp.prompt()
def user_onboarding_prompt(name: str) -> str:
    """用户入职引导模板"""
    return f"""
    请帮助新用户 {name} 完成系统初始化：
    
    1. 创建用户账户
    2. 分配默认权限
    3. 发送欢迎邮件
    4. 记录操作日志
    
    请按顺序执行，每步完成后确认。
    """

@mcp.prompt()
def debug_user_issue_prompt(user_id: int, issue: str) -> str:
    """用户问题排查模板"""
    return f"""
    用户ID: {user_id}
    问题描述: {issue}
    
    请按以下步骤排查：
    1. 查询用户基本信息
    2. 检查用户权限状态
    3. 查看最近操作日志
    4. 给出解决方案
    """
```

---

## 第四部分：进阶技巧

### 1. 参数验证与转换

```python
from pydantic import BaseModel, EmailStr, validator
from typing import Literal

class CreateUserRequest(BaseModel):
    name: str
    email: EmailStr
    role: Literal["admin", "user", "guest"] = "user"
    
    @validator('name')
    def name_must_be_valid(cls, v):
        if len(v) < 2 or len(v) > 50:
            raise ValueError('姓名长度必须在2-50字符之间')
        return v.strip()

@mcp.tool()
def create_user_validated(request: CreateUserRequest) -> dict:
    """创建用户（带参数验证）"""
    # 参数已经通过 Pydantic 验证
    return create_user(request.name, request.email)
```

### 2. 异步工具

```python
import asyncio
import aiohttp

@mcp.tool()
async def fetch_weather(city: str) -> dict:
    """异步获取天气数据"""
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.weather.com/v1/current?city={city}"
        ) as response:
            data = await response.json()
            return {
                "city": city,
                "temperature": data["temp"],
                "condition": data["condition"]
            }
```

### 3. 流式响应

```python
from typing import AsyncIterator

@mcp.tool()
async def generate_report_stream(
    start_date: str,
    end_date: str
) -> AsyncIterator[str]:
    """流式生成报表"""
    # 模拟流式数据生成
    for i in range(10):
        await asyncio.sleep(0.5)
        yield f"报表部分 {i+1}/10 已生成...\n"
    
    yield "报表生成完成！"
```

### 4. 错误处理与重试

```python
from functools import wraps
import random

def retry_on_error(max_retries=3, delay=1.0):
    """重试装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    wait = delay * (2 ** attempt) + random.uniform(0, 1)
                    await asyncio.sleep(wait)
            return None
        return wrapper
    return decorator

@mcp.tool()
@retry_on_error(max_retries=3)
async def unstable_api_call(query: str) -> dict:
    """调用不稳定的外部 API（自动重试）"""
    # 模拟可能失败的 API 调用
    if random.random() < 0.5:
        raise ConnectionError("API 暂时不可用")
    
    return {"result": f"查询 '{query}' 的结果"}
```

---

## 第五部分：企业级部署

### 1. 认证与授权

```python
from fastmcp.auth import BearerAuthProvider
from fastmcp.auth.providers.bearer import RSAKeyPair

# 生成 RSA 密钥对
key_pair = RSAKeyPair.generate()

# 创建认证提供者
auth_provider = BearerAuthProvider(
    public_key=key_pair.public_key,
    audience="enterprise-mcp"
)

# 创建带认证的 MCP 服务器
mcp = FastMCP(
    "企业级服务器",
    auth=auth_provider
)

# 生成访问令牌
token = key_pair.create_token(
    user_id="admin",
    roles=["admin", "user"],
    expires_in=3600
)
```

### 2. 中间件系统

```python
class LoggingMiddleware:
    """日志中间件"""
    
    async def process_request(self, context, next_handler):
        start = time.time()
        
        try:
            result = await next_handler()
            duration = time.time() - start
            logger.info(
                f"{context.tool_name} 成功 ({duration:.2f}s)"
            )
            return result
        except Exception as e:
            logger.error(
                f"{context.tool_name} 失败: {e}"
            )
            raise

class RateLimitMiddleware:
    """限流中间件"""
    
    def __init__(self, max_requests=100, window=60):
        self.max_requests = max_requests
        self.window = window
        self.requests = {}
    
    async def process_request(self, context, next_handler):
        client_id = context.client_id
        now = time.time()
        
        # 清理过期请求记录
        self.requests[client_id] = [
            t for t in self.requests.get(client_id, [])
            if now - t < self.window
        ]
        
        if len(self.requests[client_id]) >= self.max_requests:
            raise RateLimitError("请求过于频繁")
        
        self.requests[client_id].append(now)
        return await next_handler()

# 注册中间件
mcp.add_middleware(LoggingMiddleware())
mcp.add_middleware(RateLimitMiddleware(max_requests=200))
```

### 3. 监控与告警

```python
import psutil
from dataclasses import dataclass
from typing import Callable

@dataclass
class Metrics:
    cpu_percent: float
    memory_percent: float
    request_count: int
    avg_response_time: float

class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self.request_times = []
        self.request_count = 0
    
    def record_request(self, duration: float):
        self.request_times.append(duration)
        self.request_count += 1
        
        # 只保留最近 1000 条记录
        if len(self.request_times) > 1000:
            self.request_times = self.request_times[-1000:]
    
    def get_metrics(self) -> Metrics:
        avg_time = (
            sum(self.request_times) / len(self.request_times)
            if self.request_times else 0
        )
        
        return Metrics(
            cpu_percent=psutil.cpu_percent(),
            memory_percent=psutil.virtual_memory().percent,
            request_count=self.request_count,
            avg_response_time=avg_time
        )

class AlertManager:
    """告警管理器"""
    
    def __init__(self):
        self.rules: list[Callable[[Metrics], bool]] = []
        self.handlers: list[Callable[[str], None]] = []
    
    def add_rule(self, check: Callable[[Metrics], bool], message: str):
        """添加告警规则"""
        self.rules.append((check, message))
    
    def add_handler(self, handler: Callable[[str], None]):
        """添加告警处理器"""
        self.handlers.append(handler)
    
    def check(self, metrics: Metrics):
        """检查告警"""
        for check, message in self.rules:
            if check(metrics):
                for handler in self.handlers:
                    handler(message)

# 创建监控组件
collector = MetricsCollector()
alerts = AlertManager()

# 配置告警规则
alerts.add_rule(
    lambda m: m.cpu_percent > 80,
    "CPU 使用率超过 80%"
)
alerts.add_rule(
    lambda m: m.memory_percent > 85,
    "内存使用率超过 85%"
)
alerts.add_rule(
    lambda m: m.avg_response_time > 5.0,
    "平均响应时间超过 5 秒"
)

# 添加告警处理器（发送邮件、Slack 通知等）
alerts.add_handler(lambda msg: send_alert_email(msg))
alerts.add_handler(lambda msg: send_slack_notification(msg))
```

### 4. 高可用架构

```python
import asyncio
from typing import List
import hashlib

class LoadBalancer:
    """简单的负载均衡器"""
    
    def __init__(self, servers: List[str]):
        self.servers = servers
        self.current = 0
    
    def get_server(self) -> str:
        """轮询获取服务器"""
        server = self.servers[self.current]
        self.current = (self.current + 1) % len(self.servers)
        return server
    
    def get_server_by_key(self, key: str) -> str:
        """根据 key 哈希选择服务器（保证同一 key 路由到同一服务器）"""
        hash_val = int(hashlib.md5(key.encode()).hexdigest(), 16)
        return self.servers[hash_val % len(self.servers)]

class HealthChecker:
    """健康检查器"""
    
    def __init__(self, check_interval=30):
        self.check_interval = check_interval
        self.healthy_servers = set()
    
    async def start(self):
        """启动健康检查"""
        while True:
            for server in self.servers:
                is_healthy = await self.check_server(server)
                if is_healthy:
                    self.healthy_servers.add(server)
                else:
                    self.healthy_servers.discard(server)
            
            await asyncio.sleep(self.check_interval)
    
    async def check_server(self, server: str) -> bool:
        """检查单个服务器健康状态"""
        try:
            # 发送健康检查请求
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{server}/health",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    return resp.status == 200
        except:
            return False

# 部署配置
DEPLOYMENT_CONFIG = {
    "servers": [
        "http://mcp-server-1:8000",
        "http://mcp-server-2:8000",
        "http://mcp-server-3:8000"
    ],
    "load_balancer": {
        "strategy": "round_robin",
        "health_check": {
            "interval": 30,
            "timeout": 5,
            "retries": 3
        }
    },
    "rate_limit": {
        "requests_per_minute": 1000,
        "burst": 100
    }
}
```

---

## 第六部分：最佳实践

### 1. 设计原则

**DO（推荐）**：

- ✅ 工具功能单一，职责清晰
- ✅ 文档字符串详细，包含参数说明和示例
- ✅ 返回结构化数据，便于 AI 理解
- ✅ 做好错误处理，返回友好错误信息
- ✅ 使用类型注解，帮助 AI 构造正确参数

**DON'T（避免）**：

- ❌ 一个工具做太多事情
- ❌ 文档字符串过于简单或缺失
- ❌ 返回无意义的字符串
- ❌ 直接抛异常而不处理
- ❌ 参数类型不明确

### 2. 性能优化

```python
# 1. 使用连接池
from aiohttp import ClientSession, TCPConnector

connector = TCPConnector(
    limit=100,  # 最大连接数
    limit_per_host=20  # 每个主机最大连接数
)
session = ClientSession(connector=connector)

# 2. 缓存常用数据
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_user_cache(user_id: int) -> dict:
    """缓存用户信息"""
    return get_user_from_db(user_id)

# 3. 异步数据库操作
import asyncpg

pool = await asyncpg.create_pool(
    "postgresql://user:pass@localhost/db",
    min_size=5,
    max_size=20
)

async def get_user_async(user_id: int) -> dict:
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM users WHERE id = $1",
            user_id
        )
        return dict(row) if row else None
```

### 3. 安全规范

```python
# 1. 输入验证
from pydantic import BaseModel, validator
import re

class SafeQuery(BaseModel):
    query: str
    
    @validator('query')
    def prevent_sql_injection(cls, v):
        # 简单的 SQL 注入防护
        dangerous = [';', '--', 'DROP', 'DELETE', 'UPDATE']
        for word in dangerous:
            if word.upper() in v.upper():
                raise ValueError(f'查询包含危险关键词: {word}')
        return v

# 2. 权限控制
from enum import Enum

class Role(Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

PERMISSIONS = {
    Role.ADMIN: ["read", "write", "delete", "admin"],
    Role.USER: ["read", "write"],
    Role.GUEST: ["read"]
}

def check_permission(role: Role, action: str) -> bool:
    """检查权限"""
    return action in PERMISSIONS.get(role, [])

# 3. 敏感数据脱敏
def mask_sensitive_data(data: dict) -> dict:
    """脱敏处理"""
    masked = data.copy()
    
    # 邮箱脱敏
    if 'email' in masked:
        email = masked['email']
        local, domain = email.split('@')
        masked['email'] = f"{local[:2]}***@{domain}"
    
    # 手机号脱敏
    if 'phone' in masked:
        phone = masked['phone']
        masked['phone'] = f"{phone[:3]}****{phone[-4:]}"
    
    return masked
```

---

## 第七部分：常见问题与解决方案

### Q1: AI 不调用我的工具怎么办？

**可能原因**：

1. 文档字符串不够清晰
2. 工具名称或描述不够明确
3. 参数类型定义不明确

**解决方案**：

```python
# 优化前
@mcp.tool()
def query(data: str) -> str:
    """查询数据"""
    return str(db.query(data))

# 优化后
@mcp.tool()
def search_user_by_email(email: str) -> dict:
    """
    根据邮箱搜索用户信息。
    
    当用户提供了邮箱地址，需要查找对应用户信息时使用此工具。
    
    Args:
        email: 用户的邮箱地址，格式如 user@example.com
    
    Returns:
        包含用户信息的字典，如果没找到返回 None
    
    Example:
        输入: "zhangsan@company.com"
        输出: {"id": 123, "name": "张三", "email": "zhangsan@company.com"}
    """
    return get_user_by_email(email)
```

### Q2: 工具执行超时怎么办？

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

# 使用线程池处理阻塞操作
executor = ThreadPoolExecutor(max_workers=10)

@mcp.tool()
async def heavy_computation(data: str) -> dict:
    """耗时计算任务"""
    # 在线程池中执行阻塞操作
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        executor,
        lambda: perform_heavy_computation(data)
    )
    return result

# 或者设置超时
@mcp.tool()
async def api_call_with_timeout(query: str) -> dict:
    """带超时的 API 调用"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.example.com/search?q={query}",
                timeout=aiohttp.ClientTimeout(total=10)  # 10 秒超时
            ) as resp:
                return await resp.json()
    except asyncio.TimeoutError:
        return {"error": "请求超时，请稍后重试"}
```

### Q3: 如何处理大量数据？

```python
from typing import AsyncIterator
import json

@mcp.tool()
async def stream_large_dataset(
    table: str,
    batch_size: int = 100
) -> AsyncIterator[str]:
    """
    流式返回大量数据
    
    适合处理大数据集，避免内存溢出
    """
    offset = 0
    
    while True:
        # 分批查询
        batch = await db.fetch(
            f"SELECT * FROM {table} LIMIT $1 OFFSET $2",
            batch_size, offset
        )
        
        if not batch:
            break
        
        # 返回 JSON 格式的批次数据
        yield json.dumps({
            "batch": offset // batch_size + 1,
            "data": [dict(row) for row in batch],
            "has_more": len(batch) == batch_size
        }, ensure_ascii=False)
        
        offset += batch_size
        
        # 每批之间短暂暂停，避免过载
        await asyncio.sleep(0.1)
```

---

## 总结

MCP 协议正在快速成为 AI 工具集成的行业标准。它的核心价值在于：

1. **统一标准**：告别多平台适配的噩梦
2. **动态发现**：AI 自动理解工具能力
3. **双向通信**：工具可以主动推送数据
4. **生态丰富**：越来越多的工具和平台支持 MCP

对于开发者来说，掌握 MCP 开发技能意味着：

- 一次开发，多平台使用
- 更简单的 AI 集成体验
- 更强大的 AI 应用能力
- 更好的职业竞争力

**下一步行动**：

1. 搭建你的第一个 MCP 服务器
2. 为现有项目添加 MCP 支持
3. 探索 MCP 生态中的工具和框架
4. 关注 MCP 协议的更新和发展

---

## 参考资源

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [FastMCP 文档](https://github.com/jlowin/fastmcp)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP 规范](https://spec.modelcontextprotocol.io/)

---

*本文持续更新中，如有问题或建议，欢迎交流讨论。*