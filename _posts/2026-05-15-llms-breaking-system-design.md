---
layout: post
title: "LLM 正在瓦解 20 年的云原生架构假设"
date: 2026-05-15 09:30:00 +0800
categories: [AI Engineering, System Design]
tags: [LLM, Agent, Cloud Native, Stateful Compute, Durable Execution]
description: "LLM 和 Agent 正在从三个维度瓦解云原生架构的 20 年假设——状态存储、计算范式、系统边界的根本性变革。"
---

> 过去十年，"云原生"架构建立在一个 20 年前的假设上：状态存储在数据库，计算是无状态的。LLM 和 Agent 的出现，正在从三个维度瓦解这个假设。

## 一个正在失效的架构契约

2006 年左右，Web 架构达成了一项隐性契约：

- **数据库 = 状态**
- **应用服务器 = 无状态**
- **负载均衡器 = 不关心请求发给谁**

这套设计让水平扩展变得简单——数据库垂直扩容（换更大的机器），应用服务器水平扩容（增加更多机器）。任何请求都可以发给任何服务器，负载均衡器只需要做轮询。

这个假设支撑了从单体到微服务的整个演进路径，也定义了我们熟悉的 "stateless HTTP + load balancer + database" 三元组。

但 LLM 和 Agent 正在让这套契约失效。

## 三个被违反的假设

### 假设一：请求应该在毫秒级完成

传统 API 设计假设一次请求在几百毫秒内返回。但一个 Agent 任务可能运行 10 分钟——调用工具、等待结果、继续推理、再调用下一个工具。

这不是 "慢请求"，这是 **异步进程**。

### 假设二：计算应该是无状态的

无状态意味着服务器不保留任何请求间的上下文。但多轮对话、工具调用链、累积的上下文窗口——这些都是 **Agent 的记忆**，不是数据库状态。

把 Agent 的每一步推理结果都写回数据库，再用轮询拉回来，本质上是在用数据库当消息总线。

### 假设三：用户只需要结果，不需要过程

传统架构假设客户端发起请求、拿到响应、结束。但用户想 **观看** Agent 的思考过程、**中断** 错误的推理方向、**重定向** 任务目标。

这是一种与进程的 **双向对话**，不是一次性的状态less查询。

## 为什么 Durable Execution 不够

Temporal、Inngest、Restate 等 Durable Execution 框架解决了 **执行韧性** 问题——让长进程在崩溃后能够恢复。但它们没有解决 **交互** 问题。

```
┌─────────────┐     HTTP      ┌─────────────┐
│   Client    │ ────────────▶ │   Server    │
└─────────────┘               └─────────────┘
                                    │
                                    ▼
                              ┌─────────────┐
                              │  Temporal   │
                              │  Workflow   │
                              └─────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
              ┌─────────┐    ┌─────────┐    ┌─────────┐
              │  Poll   │    │  Poll   │    │  Poll   │
              └─────────┘    └─────────┘    └─────────┘
```

上图是当前的主流方案：Durable Execution 负责 resilient 执行，但客户端仍然通过轮询数据库获取进度。

**轮询是一个路由问题的 workaround。**

HTTP + 负载均衡器 + 无状态服务器 无法路由到特定进程。它只能路由到数据库。所以业界发明了轮询这个通用 workaround——但 latency、数据库负载、浪费的请求、糟糕的流式体验，这些问题一个都没解决。

> "Polling is what you do when you can't figure out how to address the thing you want to talk to."

## 缺失的原语：可路由的传输名称

我们需要的是一个 **可路由的传输名称**，它不是服务器，不是连接，而是一个 **地址**。

目标是："把这条消息交付给正在为 workflow X 产生输出的那个进程"——而无需知道它在哪台机器、哪个副本、哪个进程 ID。

### WebSocket 为什么不行

WebSocket 是 **连接**，不是地址。它通过直接的客户端-服务器链路一次性解决了路由问题，但连接断开后，"地址" 就丢失了。你无法重新连接到同一个进程。

### Pub/Sub Channel 的反转

Pub/Sub Channel 反转了所有权：

- 服务器进程不可寻址
- 客户端不可寻址
- **传输通道本身可寻址**

双方都通过 **名称** 连接到同一个 channel，实现双向、有状态的通信。连接断开/重连不会丢失数据或破坏路由。

```
┌─────────────┐         ┌─────────────┐
│   Client    │◄───────►│   Channel   │◄───────►│  Workflow   │
│  (any box)  │  "wf-123"│  (by name)  │  "wf-123"│  (any box)  │
└─────────────┘         └─────────────┘         └─────────────┘
       │                                               │
       └──────────── 双向通信，双方都可断开/重连 ─────────────┘
```

Temporal 的示例：workflow activity 连接到以 `workflow ID` 命名的 pub/sub channel，客户端也连接到同一个 channel 获取更新 + 发送中断/转向指令。无论 workflow 进程还是客户端连接如何中断，重连到同一个 channel 就能恢复通信。

这消除了：
- 通过数据库传递数据
- 轮询
- 无法寻址的 durable 进程

## 为什么 LLM 让这个问题显性化

这个问题不是 LLM 带来的，但 LLM 让它的代价变得不可接受：

| 属性 | 影响 |
|------|------|
| 非确定性 | 重试 ≠ 相同响应 |
| 高成本（按 token 计费） | 浪费的 token = 真金白银 |
| 连接脆弱性 | "客户端进了隧道" = 昂贵的失败 |

以前连接断开，请求足够便宜可以重试，而且响应是确定性的。现在一个 10 分钟的 Agent 任务中断后重试，可能产生完全不同的结果，而且你已经为中断前的 token 付过费了。

你也不想为了让客户端连接更 resilient，就把每个 token 都写进数据库。

## 推荐的架构分层

```
┌─────────────────────────────────────────────┐
│           Stateless HTTP Layer              │
│    (传统请求/响应，短连接，无状态)            │
├─────────────────────────────────────────────┤
│         Durable Execution Layer             │
│    (Temporal/Restate，长进程，执行韧性)       │
├─────────────────────────────────────────────┤
│         Pub/Sub Channel Layer               │
│    (可寻址、可重连、双向传输)                 │
└─────────────────────────────────────────────┘
```

| 层级 | 职责 |
|------|------|
| **Stateless HTTP** | 传统请求/响应 |
| **Durable Execution** | 韧性长进程 |
| **Pub/Sub Channel** | 可寻址、可重连、双向传输 |

无状态 Web 没有错，它只是不适合 Agentic 应用——这些应用需要长运行、有状态、可交互的进程。我们需要一种新的架构，包含能够寻址 **进程** 而不仅仅是数据库的路由原语。

## 实战：一个最小可用的 Agent 通道设计

假设你正在构建一个内部 AI 平台，支持多步 Agent 工作流。以下是一个最小可用的 channel 设计：

```python
import asyncio
from dataclasses import dataclass
from typing import AsyncIterator, Callable

@dataclass
class AgentChannel:
    """可寻址的 Agent 通信通道"""
    workflow_id: str
    _inbox: asyncio.Queue
    _outbox: asyncio.Queue
    
    async def send(self, msg: dict) -> None:
        """向 workflow 发送指令/中断"""
        await self._inbox.put(msg)
    
    async def receive(self) -> AsyncIterator[dict]:
        """接收 workflow 的流式输出"""
        while True:
            msg = await self._outbox.get()
            if msg.get("type") == "done":
                break
            yield msg

class ChannelRegistry:
    """按 workflow_id 寻址的通道注册表"""
    _channels: dict[str, AgentChannel] = {}
    
    @classmethod
    def get_or_create(cls, workflow_id: str) -> AgentChannel:
        if workflow_id not in cls._channels:
            cls._channels[workflow_id] = AgentChannel(
                workflow_id=workflow_id,
                _inbox=asyncio.Queue(),
                _outbox=asyncio.Queue(),
            )
        return cls._channels[workflow_id]
    
    @classmethod
    def remove(cls, workflow_id: str) -> None:
        cls._channels.pop(workflow_id, None)
```

这个设计的核心思想：

- **Channel 是地址**，不是连接
- **Workflow ID 是路由键**，不是进程 ID
- **双方都可以断开/重连**，不影响通信连续性

## 踩坑与对比

### 常见错误一：用数据库当消息总线

把 Agent 的每一步输出都写入数据库，客户端轮询读取。这在小规模可行，但：

- 数据库成为瓶颈
- 轮询间隔 = latency 与负载的权衡
- 流式体验差

### 常见错误二：WebSocket 直接连接 Agent 进程

WebSocket 连接绑定到特定进程，进程崩溃后客户端无法重连到同一逻辑工作流。

### 备选方案对比

| 方案 | 优点 | 缺点 |
|------|------|------|
| 数据库轮询 | 简单，无需新基础设施 | 高延迟，数据库负载，差体验 |
| WebSocket | 实时双向 | 连接即地址，不可重连 |
| Server-Sent Events | 单向流式 | 无客户端→服务端通道 |
| **Pub/Sub Channel** | 可寻址，可重连，双向 | 需要额外基础设施 |

## 总结与行动

1. **识别你的 Agent 工作流**：哪些任务超过 10 秒？哪些需要用户交互？
2. **评估当前架构**：是否在用数据库轮询或 WebSocket 直接连接？
3. **引入 Channel 抽象**：即使先用 Redis Pub/Sub 或 SSE + 重连逻辑，也比轮询更接近正确方向
4. **分离关注点**：Stateless HTTP 处理短请求，Durable Execution 处理长进程，Channel 处理双向交互
5. **从小处开始**：不需要一次性替换整个架构，先在一个 Agent 工作流中验证 Channel 模式

---

**参考**

- [LLMs are breaking 20 year old system design](https://zknill.io/posts/llms-are-breaking-20-year-old-system-design/) — /dev/knill
- [Accelerating LLM-Driven Developer Productivity at Zoox](https://www.infoq.com/presentations/ai-software-development/) — InfoQ QCon SF 2026
