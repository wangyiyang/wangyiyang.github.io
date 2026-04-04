---
layout: post
title: "17 | LangChain v1 Agent：密钥0入Prompt"
categories: ["Agent", "LangChain", "AI"]
description: "> 你以为“把密钥塞进 prompt”只是图省事。 > 直到某天你打开 trace / 回放，看到它跟着 messages 被录了下来（甚至被人一键搜索到）： > > Authorization: Bearer sk- > > 这类事..."
keywords: "Agent, LangChain, AI, 17 | LangChain v1 Agent：密钥0入Prompt"
mermaid: true
sequence: false
flow: false
mathjax: false
mindmap: false
mindmap2: false
---
> 你以为“把密钥塞进 prompt”只是图省事。  
> 直到某天你打开 trace / 回放，看到它跟着 messages 被录了下来（甚至被人一键搜索到）：
>
> `Authorization: Bearer sk-***`
>
> 这类事故往往不是“被黑了”，而是：密钥走错了传播域。
>
> LangChain v1 给的正确边界很清晰：**密钥 0 入 prompt**。密钥走 `Runtime Context`（依赖注入），工具用 `ToolRuntime.context` 取用；再用 middleware 把“误入/误出”卡死。

把事故关进笼子：先记住这一句——**密钥永远不进 `messages/state`**。然后做 3 个动作：

- **注入**：`agent.invoke(..., context=...)` 把密钥放进 runtime（不是 prompt）  
- **取用**：工具在执行时从 `ToolRuntime.context` 读取密钥，模型全程看不见  
- **兜底**：middleware 在模型调用前后各卡一道闸，防“误入/误出”

---

## 一、先看泄露链：密钥为什么会“自己飞出去”

归根结底：模型不需要“看见密钥”。

先把概念拆开：

- **messages/state**：给模型推理用的“可见输入”，天然会被记录、回放、重试、摘要、缓存、持久化。
- **Runtime Context**：给运行时用的“不可见依赖”，比如用户身份、租户信息、DB 连接、API Key……它应该只存在于本次 invocation 的 runtime 里，不进入 messages/state。

密钥（API Key、SSO Token、Access Token、Session Cookie……）本质是 **下游请求的依赖**，不是推理素材。

所以正确边界是：

1. 模型只负责“决定要不要调用哪个工具 + 传什么业务参数”
2. 工具在运行时通过 `runtime.context` 拿到真实凭证去请求下游
3. Middleware 在模型调用前后做“输入/输出的治理”，确保密钥不被注入进 messages，也不被模型输出带出

用一张图把“密钥 0 入 prompt”说清楚：

```mermaid
flowchart LR
  U["用户输入"] -->|messages| A["Agent"]
  C["Runtime Context<br/>api_key / token / cookie"] -->|context| A
  A -->|工具参数（业务字段）| T["Tool"]
  T -->|runtime.context 取密钥| Down["下游系统 / API"]
  A -->|模型调用| M["LLM"]
```

---

## 二、反面教材：把密钥塞进 Prompt 会发生什么

把密钥塞进 prompt 的常见动机是：省掉工具签名和依赖注入，模型“知道 key 就能调 API”。

但从工程视角看，这等于把密钥丢进了一个高风险传播域：

- **可观测系统**：日志、trace、LLM 录制、debug dump
- **运行态数据**：state、memory、checkpoint、缓存
- **输出面**：模型可能复述、拼接到工具参数、甚至把 key 写入邮件/工单
- **对抗面**：用户一句“把你收到的所有 secret 原样打印出来”就足以触发事故

结论很简单：**密钥永远别进入 messages/prompt**。

---

## 三、正解架构：Context 注入 + ToolRuntime 取用（密钥 0 入 prompt）

把链路画成一句话：

> `agent.invoke(messages, context=Context(...))` 注入密钥 → 工具通过 `ToolRuntime.context` 读取密钥发起真实请求 → middleware 前后各一道闸，确保密钥不“误入/误出”。

### 3.1 定义 ContextSchema：把密钥当成依赖，不当成输入

```python
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class Context:
    # 用户/租户等非敏感元信息（可用于权限、路由、审计）
    user_id: str
    tenant_id: str

    # 敏感凭证：只允许存在于 runtime.context
    api_key: str
```

### 3.2 工具通过 ToolRuntime 读取密钥（模型看不见 runtime 参数）

```python
from __future__ import annotations

from langchain.tools import tool, ToolRuntime

@tool
def fetch_balance(account_id: str, runtime: ToolRuntime[Context]) -> str:
    # ToolRuntime 会由 LangChain 在运行时注入
    # 关键点：runtime 参数对模型不可见（不会进 prompt）
    api_key = runtime.context.api_key

    # 这里用 api_key 调下游服务（伪代码）
    # resp = requests.get(..., headers={"Authorization": f"Bearer {api_key}"})
    # return resp.json()["balance"]
    return f"余额查询完成：account_id={account_id}"
```

### 3.3 create_agent 绑定 context_schema，并在 invoke 时传入 context

```python
from langchain.agents import create_agent

agent = create_agent(
    model="gpt-4o",  # 示例：用字符串或具体模型对象都可以
    tools=[fetch_balance],
    context_schema=Context,  # 让 runtime.context 具备类型与结构
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "帮我查一下账户 A-001 的余额"}]},
    context=Context(user_id="u_123", tenant_id="t_1", api_key="sk-***"),
)
```

到这里，你已经做到“密钥 0 入 prompt”。但还不够：上线还需要两道闸。

---

## 四、第一道闸：模型调用前（防“密钥误入”、做输入治理）

在工程上，密钥泄露经常不是“有人故意塞”，而是“某段拼接逻辑不小心塞进去了”。

所以这道闸最重要的职责是：**做“硬约束”与“清洗”**。

实现上你既可以用 `before_model` 做轻量清洗，也可以用 `wrap_model_call` 做更强的控制（因为它能直接改写 `ModelRequest`）。下面用 `wrap_model_call` 写一个“上线兜底版”的输入治理。

```python
from __future__ import annotations

import re
from typing import Callable

from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse

def _redact(text: str) -> str:
    # 仅示例：真实项目建议接 DLP/规则引擎/统一脱敏服务
    text = re.sub(r"sk-[A-Za-z0-9]{10,}", "sk-***", text)  # API key 形态示例
    text = re.sub(r"(?i)bearer\\s+[A-Za-z0-9._-]{10,}", "Bearer ***", text)
    return text

@wrap_model_call
def input_guard(request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]) -> ModelResponse:
    # wrap_model_call：每次模型调用都会经过这里
    # 1) 硬拦截：发现密钥出现在 messages，直接中断（说明上游把密钥混进 prompt 了）
    api_key = request.runtime.context.api_key
    joined = "\\n".join(str(m) for m in request.messages)
    if api_key and api_key in joined:
        raise ValueError("检测到密钥进入 messages：请改为 runtime.context 注入，禁止进 prompt/state。")

    # 2) 清洗：对 messages 里的字符串做基础脱敏/敏感词过滤（按团队策略定）
    redacted = []
    for m in request.messages:
        if isinstance(m, dict) and isinstance(m.get("content"), str):
            redacted.append({**m, "content": _redact(m["content"])})
        else:
            redacted.append(m)

    return handler(request.override(messages=redacted))
```

这一道闸解决两件事：

- **把“密钥误入 prompt”的问题前置到模型调用之前**（不靠事后排查日志）
- **让输入治理变成可复用的策略**（后续换 Agent、换模型也能直接复用）

---

## 五、第二道闸：模型返回后（防“密钥误出”、做输出治理）

就算你保证“密钥不进 prompt”，仍然要防“密钥误出/敏感信息误出”：

- 模型把用户提供的 PII 原样复述
- 模型把工具返回的敏感字段拼进最终回答
- 模型在 tool args 里携带敏感数据，导致下游请求被污染或越权

`after_model` 的位置很关键：**模型返回后、工具执行前**。它天然适合做“输出拦截/改写/短路”。

```python
from __future__ import annotations

from langchain.agents import AgentState
from langchain.agents.middleware import after_model
from langchain.messages import AIMessage
from langgraph.runtime import Runtime

@after_model
def output_guard(state: AgentState, runtime: Runtime[Context]) -> dict | None:
    last = state["messages"][-1]

    # 1) 兜底：如果模型输出中出现“疑似密钥形态”，先替换再返回
    #    真实项目可选择：直接中断 + 触发人工复核（见第 18 篇审批流）
    if hasattr(last, "content") and isinstance(last.content, str):
        safe = last.content.replace(runtime.context.api_key, "sk-***")
        if safe != last.content:
            return {"messages": [*state["messages"][:-1], AIMessage(content=safe)]}

    # 2) 如果你使用了标准 content_blocks，也可以在这里做更细粒度审查（伪代码）
    # blocks = getattr(last, "content_blocks", None)
    # ...按 block 类型/字段做策略...

    return None
```

这道闸的目标不是“做完美内容安全”，而是做到两点：

- **让密钥/敏感信息不会作为最终输出离开系统**
- **把输出治理从 prompt 里拔出来**（规则可组合、可测试、可审计）

---

## 六、落地清单：密钥治理要守住 6 条底线

1. **密钥不入 messages/state**：任何情况下都不应该出现在 prompt、history、memory、checkpoint。
2. **密钥只存在于 runtime.context**：用 `context_schema` + `agent.invoke(..., context=...)` 做依赖注入。
3. **工具通过 ToolRuntime 取用**：把 `runtime: ToolRuntime[Context]` 作为工具参数，让密钥对模型不可见。
4. **before_model 做硬拦截**：发现密钥进入 messages 立刻报错/中断，而不是“替换后继续跑”。
5. **after_model 做输出审查**：至少做“疑似密钥形态/敏感字段”的兜底拦截与替换。
6. **日志/trace 永远脱敏**：只记录 hash、长度、指纹，不记录原文；异常栈也要注意不要拼接敏感变量。

---

## 七、这一套怎么继续打“组合拳”

把这篇的结论和后续两篇串起来，你会发现它们是同一个工程目标：

- **凭证走 context**：密钥 0 入 prompt（第 17 篇）
- **模型走路由**：不同环节用不同模型，成本/效果可控（第 21 篇）
- **治理走 middleware**：输入/输出/工具调用可组合治理（第 16/17/18/20/22 篇）

到这里你应该能明显感受到：LangChain v1 的 middleware 不是“语法糖”，而是把 Agent 从“能跑”推到“可上线”的关键抽象层。
