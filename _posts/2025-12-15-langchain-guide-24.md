---
layout: post
title: "24 | Mem0 MCP × LangChain v1：把记忆当 MCP 工具（最小权限 + HITL）"
categories: ["Mem0", "LangChain", "AI"]
description: "> 第 23 篇我们把“读记忆 + 写回”做进 middleware，做到“自动长期记忆”。 > 但线上还有一类更危险的需求：用户让你改/删记忆（“把那条偏好改一下”“忘掉我 2023 年的记录”）。 > > 这类操作的本质是“持久化..."
keywords: "Mem0, LangChain, AI, MCP, 24 | Mem0 MCP × LangChain v1：把记忆当 MCP 工具（最小权限 + HITL）"
mermaid: true
sequence: false
flow: false
mathjax: false
mindmap: false
mindmap2: false
---
> 第 23 篇我们把“读记忆 + 写回”做进 middleware，做到“自动长期记忆”。  
> 但线上还有一类更危险的需求：**用户让你改/删记忆**（“把那条偏好改一下”“忘掉我 2023 年的记录”）。
>
> 这类操作的本质是“持久化副作用”，它不该是模型一句话就能直接落地的行为。  
> 所以这一篇换一个入口：把 Mem0 封装成 MCP 工具，用 **最小权限 + HITL** 把“写记忆”变成可审批能力。

---

## 一、第一性原理：记忆写入 = 高权限副作用，默认不可达

把“记忆”拆成两个原子动作：

- **读（检索）**：把相关记忆拿出来，辅助推理（可默认放行，但必须隔离作用域）  
- **写（新增/更新/删除）**：改变可持久化事实（必须默认拒绝，除非显式授权 + 审批）

因此这一篇的目标只有一句话：

> **把记忆当工具，把工具当权限。**  
> 默认只给模型“search”，写入类工具只有在“授权 + 审批”都满足时才可达。

---

## 二、架构：一个记忆内核（Mem0）+ MCP 工具入口（显式）+ LangChain 治理（最小权限 + HITL）

```mermaid
flowchart LR
  U["用户意图：查询/记住/修改/忘记"] --> A["LangChain v1 Agent"]
  A --> R["wrap_model_call<br/>动态裁剪可见工具"]
  R --> M["LLM（只看到最小工具集）"]
  M -->|tool_call| H["HITL（第18篇）<br/>写工具先审批"]
  H -->|approved| T["Mem0 MCP tools"]
  T --> P["Mem0 Platform API（SaaS）"]
```

这条链路解决的不是“怎么接 Mem0”，而是三个治理问题：

1. **模型默认看不见写工具**（第 22 篇：动态选工具 = 最小权限）  
2. **就算看见了，执行前也要停一下**（第 18 篇：HITL 审批流）  
3. **记忆作用域不可被 prompt 篡改**（user/tenant 只能来自 runtime.context）

---

## 三、先说清楚：本文示例默认使用 Mem0 Platform（SaaS）的 mem0-mcp-server

官方的 `mem0-mcp-server` 是一个 MCP server：把 **Mem0 Platform（SaaS）** 的 Memory API 暴露成 MCP 工具。  
因此本文示例默认使用：

- `MEM0_API_KEY`（服务端环境变量，只给 MCP server 用，不进 messages/prompt）
- MCP 工具（`search_memories` / `add_memory` / `update_memory` / `delete_memory` / `delete_all_memories` …）

如果你们最终要用 **Mem0 OSS + 自建向量数据库**（数据驻留/合规），也完全可行：  
但它不是 `mem0-mcp-server` 开箱即用覆盖的范围——你要么直接用第 23 篇的“Python 直连 Memory”，要么自己写一个 MCP server 包一层（下文第六节给最小骨架）。

---

## 四、接入 LangChain v1：先把 Mem0 MCP 工具“加载进来”（但不等于放权）

依赖（只保留 2 条命令，二选一）：

```bash
uv add langchain langgraph langchain-mcp-adapters
# 或
pip install langchain langgraph langchain-mcp-adapters
```

然后用 `MultiServerMCPClient` 启动本地 `mem0-mcp-server`（stdio），把工具列表拿到手：

```python
import asyncio
import os

from langchain_mcp_adapters.client import MultiServerMCPClient

MEM0_READ_TOOLS = {"search_memories"}
MEM0_WRITE_TOOLS = {"add_memory", "update_memory", "delete_memory", "delete_all_memories"}

async def load_mem0_tools():
    client = MultiServerMCPClient(
        {
            "mem0": {
                "transport": "stdio",
                "command": "uvx",
                "args": ["mem0-mcp-server"],
                "env": {"MEM0_API_KEY": os.environ["MEM0_API_KEY"]},
            }
        }
    )
    tools = await client.get_tools()
    allow = MEM0_READ_TOOLS | MEM0_WRITE_TOOLS
    return [t for t in tools if t.name in allow]

tools = asyncio.run(load_mem0_tools())
```

注意：**“加载工具”不等于“暴露工具”**。  
真正的权限控制，要在下一节的 middleware 里做。

---

## 五、三道闸：默认只读 + 写入走审批 + 强制 user/tenant 作用域

### 5.1 Context：把 user/tenant/权限信号放进 runtime.context

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Context:
    user_id: str
    tenant_id: str

    # 是否允许“写记忆”（通常来自用户同意、后台开关或灰度策略）
    allow_mem0_write: bool = False
```

### 5.2 动态选工具：模型默认只看见 search

```python
from typing import Callable

from langchain.agents.middleware import ModelRequest, ModelResponse, wrap_model_call

def _wants_mem0_write(text: str) -> bool:
    return any(k in text for k in ("记住", "保存", "更新记忆", "删除记忆", "忘记", "清空记忆"))

@wrap_model_call
def mem0_tool_router(
    request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    ctx = getattr(request.runtime, "context", None)
    last = str(getattr(request.messages[-1], "content", "")) if request.messages else ""

    visible = set(MEM0_READ_TOOLS)
    if ctx and getattr(ctx, "allow_mem0_write", False) and _wants_mem0_write(last):
        visible |= MEM0_WRITE_TOOLS

    return handler(request.override(tools=[t for t in request.tools if t.name in visible]))
```

### 5.3 执行层：写工具一律 HITL（先停一下再执行）

```python
from langchain.agents.middleware import HumanInTheLoopMiddleware

mem0_hitl = HumanInTheLoopMiddleware(
    interrupt_on={
        "search_memories": False,
        "add_memory": True,
        "update_memory": True,
        "delete_memory": {"allowed_decisions": ["approve", "reject"]},
        "delete_all_memories": {"allowed_decisions": ["approve", "reject"]},
    }
)
```

### 5.4 作用域强制：模型不允许指定 user_id（只从 context 注入）

最小可行策略：无论模型传什么参数，**Mem0 的读写都强制落在 `tenant_id:user_id` 这个 scope 上**。

```python
from langchain.agents.middleware import wrap_tool_call
from langchain.tools.tool_node import ToolCallRequest

@wrap_tool_call
def mem0_scope_guard(request: ToolCallRequest, handler):
    name = request.tool_call["name"]
    if name not in (MEM0_READ_TOOLS | MEM0_WRITE_TOOLS):
        return handler(request)

    ctx = request.runtime.context
    user_scope = f"{ctx.tenant_id}:{ctx.user_id}"
    args = dict(request.tool_call.get("args") or {})

    if name == "search_memories":
        args["filters"] = {"AND": [{"user_id": user_scope}]}
    elif name in {"add_memory", "delete_all_memories"}:
        args["user_id"] = user_scope

    request.tool_call["args"] = args
    return handler(request)
```

最后把它们组装进 `create_agent`（HITL 必须配 checkpointer，详见第 18 篇）：

```python
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(
    model="gpt-4o-mini",
    tools=tools,
    context_schema=Context,
    middleware=[mem0_tool_router, mem0_scope_guard, mem0_hitl],
    checkpointer=InMemorySaver(),
)
```

到这里你已经拿到一个很“克制”的能力面：

- 默认：模型只能 `search_memories`（而且只能搜自己的 scope）  
- 写入：必须满足 `allow_mem0_write=True` + 命中写入意图 + HITL 审批通过  

审批准备、interrupt/resume 的处理方式，直接复用第 18 篇的模板即可。

---

## 六、如果你们要 Mem0 OSS + 自建向量数据库：自己包一层 MCP（最小骨架）

Mem0 OSS 支持 `Memory.from_config(...)` 接自建向量库（例如 Qdrant）。  
你可以像第 11 篇那样用 FastMCP 很快包出一个“你们自己的 mem0-oss-mcp”：

```python
import json

from mcp.server.fastmcp import FastMCP
from mem0 import Memory

mcp = FastMCP("mem0-oss")
memory = Memory.from_config(
    {"vector_store": {"provider": "qdrant", "config": {"host": "localhost", "port": 6333}}}
)

@mcp.tool()
def search_memories(query: str, user_id: str) -> str:
    return json.dumps(memory.search(query, user_id=user_id), ensure_ascii=False)

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

你们真正要补齐的是两件事：

1. **鉴权与多租户隔离**：user_id/tenant_id 不能信模型传参，必须从服务端身份态注入  
2. **写入治理**：同样按本文的“最小权限 + HITL”做（只是工具后端从 SaaS 换成 OSS）

---

## 七、行动清单（上线版）

1. 默认只暴露 `search_memories`，别把 delete/update 工具常开  
2. `allow_mem0_write` 做成显式授权信号（用户同意/后台开关/灰度）  
3. 写工具一律走 HITL（第 18 篇），并把 `thread_id/user_id/tenant_id` 写进 tracing 的 tags/metadata（第 20 篇）  
4. Mem0 的作用域必须从 runtime.context 注入（禁止模型指定 user_id/tenant_id）  
5. 记忆 CRUD 的“更新/矛盾/TTL/忘记我”规则，留到第 25 篇做成治理规范

下一篇（第 25 篇）我们把“记忆治理”补齐：矛盾更新、TTL、忘记我（delete_all）怎么落地，以及上线 Checklist 怎么写。
