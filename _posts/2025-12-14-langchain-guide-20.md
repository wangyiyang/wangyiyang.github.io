---
layout: post
title: "20 | LangChain v1 Agent：全链路追踪开起来，事故复盘不用猜"
categories: ["Agent", "LangChain", "AI"]
description: "> 线上 Agent 出问题时，最常见的“复盘现场”是这样的： > > - 现象：工具调用突然暴增、成本飙升、或者干脆把生产打挂 > - 追问：到底是谁触发的？哪一次对话？模型看见了什么？工具拿到了什么参数？ > - 结果：日志只有一..."
keywords: "Agent, LangChain, AI, 20 | LangChain v1 Agent：全链路追踪开起来，事故复盘不用猜"
mermaid: false
sequence: false
flow: false
mathjax: false
mindmap: false
mindmap2: false
---
> 线上 Agent 出问题时，最常见的“复盘现场”是这样的：
>
> - 现象：工具调用突然暴增、成本飙升、或者干脆把生产打挂  
> - 追问：到底是谁触发的？哪一次对话？模型看见了什么？工具拿到了什么参数？  
> - 结果：日志只有一句 `tool=xxx`，然后全员开始“推理式排障”
>
> 这不是你们不会写日志，而是你们缺的根本不是日志——缺的是**能回放的全链路 trace**。
>
> LangChain v1 的好消息是：用 `create_agent` 构建的 Agent **天然支持 LangSmith tracing**；再配合 middleware，你可以把“谁在何时做了什么”串成一条链：模型调用、工具调用、耗时、错误、成本、关键字段脱敏，一次事故复盘不再靠猜。

---

## 一、第一性原理：你要的不是“更多日志”，而是“可回放的因果链”

排障/复盘真正需要回答的问题只有三个：

1. **当时模型“看见了什么”**：系统提示词 + state.messages + 工具列表（以及被动态改写后的版本）
2. **模型“决定了什么”**：回复内容 / tool_call（包含工具名与参数）
3. **系统“实际执行了什么”**：工具有没有被执行、执行了几次、耗时/错误是什么、结果如何写回 state

如果这三段之间无法用同一个 `thread_id/run_id` 串起来，你就只能靠“猜测因果”。  
所以可观测的核心不是打印更多字符串，而是把每一步做成可关联的事件：**trace → runs → span-like steps**。

---

## 二、LangChain v1 的“全链路追踪”长什么样（你应该在 UI 里看到什么）

在 LangSmith 里，一次 Agent 运行通常会被拆成一条 trace（总链路）+ 多个 run（步骤）：

- 顶层 run：一次 `agent.invoke(...)`（对应一次用户输入触发的执行闭环）
- 子 run：一次模型调用（LLM）
- 子 run：一次工具调用（Tool）
- （可选）更多子 run：重试、摘要、RAG 注入、审批 interrupt/resume 等

如果你已经做了第 17～19 篇的治理（密钥走 context、HITL、摘要），这一条 trace 的价值会更大：  
它能让你把“治理策略是否生效”从主观感觉，变成可验证的链路事实。

---

## 三、LangSmith 一键开追踪：最小到只剩环境变量

LangChain 官方文档给的结论很明确：`create_agent` 构建的 Agent 会自动支持 LangSmith tracing。  
你只需要把 tracing 打开即可（以下是常见的最小配置）：

```bash
# 打开 tracing
export LANGSMITH_TRACING=true

# 配置 LangSmith API Key
export LANGSMITH_API_KEY=<your-api-key>

# 可选：把 trace 打到指定项目（不配默认是 default）
export LANGSMITH_PROJECT=my-agent-project
```

你不需要改 Agent 代码：照常 `agent.invoke(...)` 就会自动把步骤记录下来。

---

## 四、让 trace “可检索、可归因”：把关键上下文放进 tags/metadata（别放进 messages）

线上排障最痛的不是“没有 trace”，而是“trace 找不到”。  
你要让一次运行可以被快速过滤出来：按租户、按用户、按环境、按版本、按实验组……

LangGraph/LangChain 的调用层支持在 invocation 上挂 `tags` / `metadata`（注意：这不是给模型看的内容）：

```python
response = agent.invoke(
    {"messages": [{"role": "user", "content": "把今天的订单退款情况汇总一下"}]},
    config={
        # tags：用于归类和筛选（建议用枚举风格，别塞长文本）
        "tags": ["production", "refund-agent", "ab:route-v2"],
        # metadata：用于关联/追责（建议放可索引字段）
        "metadata": {
            "tenant_id": "t_001",
            "user_id": "u_123",
            "thread_id": "thread_20251214_0001",
            "release": "2025.12.14",
        },
    },
)
```

几个落地建议（少走弯路）：

- `thread_id` 你们要自己定义一套稳定策略：否则“同一会话”的工具调用会散落在多条 trace 里
- `user_id`/`tenant_id` 建议用内部 ID 或哈希，不要直接塞手机号/邮箱
- 把“排障要用的字段”放 `metadata`，不要塞进 `messages` 去污染 prompt（更不要把密钥塞进去）

---

## 五、敏感数据怎么处理：别赌“没人会看 trace”

追踪系统的本质是“录屏”。  
你做了追踪，就等于默认接受：**会有人打开回放**（开发、SRE、审计、甚至供应商支持）。

所以敏感数据要两层保险：

### 5.1 第一层：治理边界正确（密钥永不进入 messages/state）

如果你按第 17 篇做了 `Runtime Context` 注入：密钥/Token/Cookie 只存在于 `runtime.context`，模型侧 messages 看不见。  
这一步能直接把“密钥被 trace 录下来”的概率降到极低。

### 5.2 第二层：对 trace 做规则化脱敏（anonymizer）

LangChain/LangGraph 文档提供了一个可复用的思路：给 tracer client 配 anonymizer，把匹配规则的内容在入库前替换掉。

下面是**最小示意片段**（重点看注释的思路，不用纠结细节类名是否与你们版本完全一致）：

```python
from langsmith import Client
from langsmith.anonymizer import create_anonymizer

# 1) 定义脱敏规则：用正则匹配敏感模式，然后替换为占位符
anonymizer = create_anonymizer(
    [
        # 示例：把疑似 SSN 的格式打成 <ssn>
        {"pattern": r"\\b\\d{3}-?\\d{2}-?\\d{4}\\b", "replace": "<ssn>"},
        # 你也可以加：API Key 前缀、Bearer token、cookie 键名等规则
    ]
)

# 2) 用带 anonymizer 的 client 构建 tracer（只要接入 callbacks，就会自动应用脱敏）
tracer_client = Client(anonymizer=anonymizer)
```

把“脱敏”下沉到 tracer 这层的好处是：  
你不用指望每个开发都记得“别打印”，也不用靠 code review 去抓漏网之鱼。

---

## 六、Middleware 视角：把一次 Agent 运行拆成“你能解释清楚的事件”

LangSmith 解决的是“链路回放”；middleware 更擅长补齐“你们自己的业务可观测”：例如你们想把 tool_call 的审计字段打到自建日志/指标系统里。

下面给一个“够克制”的观测中间件骨架：它不引入额外依赖，只展示你应该在哪些 hook 上打点，以及**哪些字段必须脱敏**。

```python
from __future__ import annotations

import json
import time
from typing import Any, Callable

from langchain.agents.middleware import (
    after_agent,
    before_agent,
    wrap_model_call,
    ModelRequest,
    ModelResponse,
)

def _redact(value: Any) -> Any:
    # 统一的脱敏入口：别把“怎么脱敏”散落到每个 hook 里
    if value is None:
        return None
    return "<redacted>"

@before_agent
def obs_start(state: dict[str, Any], runtime: Any) -> dict[str, Any] | None:
    # before_agent：适合做“本次运行”的起始打点（一次 invocation 只会触发一次）
    runtime.metadata = getattr(runtime, "metadata", {})  # 防御式写法：避免 runtime 结构差异
    runtime.metadata["obs_start_ms"] = int(time.time() * 1000)
    return None

@wrap_model_call
def obs_model(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    # wrap_model_call：适合记录模型调用耗时、失败原因、选用模型等（每次模型调用都会触发）
    t0 = time.time()
    try:
        response = handler(request)
        ok = True
        err = None
        return response
    except Exception as e:  # noqa: BLE001
        ok = False
        err = repr(e)
        raise
    finally:
        cost_ms = int((time.time() - t0) * 1000)

        # 注意：千万别把 runtime.context 原样打出去（里面可能有密钥/Token/Cookie）
        event = {
            "type": "model_call",
            "ok": ok,
            "cost_ms": cost_ms,
            "model": str(request.model),
            # 你可以从 request.state / request.runtime 拿到 thread_id / tenant_id 等
            "tenant_id": request.runtime.context.tenant_id if hasattr(request.runtime, "context") else None,
            # 对敏感字段做脱敏或直接不记录
            "credentials": _redact(getattr(getattr(request.runtime, "context", None), "api_key", None)),
        }

        print(json.dumps(event, ensure_ascii=False))

@after_agent
def obs_end(state: dict[str, Any], runtime: Any) -> dict[str, Any] | None:
    # after_agent：适合做“本次运行”的收口打点（一次 invocation 只会触发一次）
    start_ms = getattr(getattr(runtime, "metadata", {}), "get", lambda _k, _d=None: _d)("obs_start_ms")
    end_ms = int(time.time() * 1000)
    event = {
        "type": "agent_done",
        "cost_ms": (end_ms - start_ms) if start_ms else None,
        # 示例：记录 messages 的规模（注意别把内容原样打出去）
        "message_count": len(state.get("messages", [])),
    }
    print(json.dumps(event, ensure_ascii=False))
    return None
```

你会发现：  
真正“好用的观测”不是把内容全打出来，而是把**可关联字段 + 关键指标**打出来，并且默认脱敏。

---

## 七、当你需要跨服务链路：OpenTelemetry 让 trace 贯穿整个系统

如果你的 Agent 不只是一个进程：它还会调用网关、业务服务、异步任务、外部 API……  
这时你要的不是“LangChain 内部链路”，而是“跨服务分布式链路”。

官方也给了方向：LangSmith 支持基于 OpenTelemetry 的 tracing，把 LangChain 的步骤作为 spans 汇入统一的观测体系（以及把 trace context 传播到下游服务）。

工程上你可以把它当成一句话：

> LangSmith 解决“Agent 内部可回放”，OpenTelemetry 解决“系统级可串联”。

---

## 八、把它和前 3 篇串起来：可观测不是锦上添花，是治理闭环的最后一环

到这里，你会发现第 17～20 篇其实是一套上线组合拳：

- 密钥/凭证走 `runtime.context`（降低泄露面）
- middleware 卡住“误入/误出”（把事故概率压到更低）
- HITL 把高风险工具变成“默认不可达”（把副作用关进笼子）
- 摘要把长对话成本打下来（让产品敢放量）
- 全链路追踪把复盘从“猜”变成“看”（让治理能被验证、能被追责）

下一篇我们会把“不同环节用不同模型”讲透：让你不仅能看见链路，还能把成本、效果、风险在链路上做成可控开关。
