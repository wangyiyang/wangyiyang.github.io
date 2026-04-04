---
layout: post
title: "21 | LangChain v1 Agent：动态选模，DeepSeek-V3.2/V3.2-Speciale在同一个ChatBI里怎么分工？"
categories: ["Agent", "LangChain", "AI"]
description: "> 你想用最强推理模型把 ChatBI 的“分析质量”拉满，但一接上工具就翻车：模型不支持 Tool Calls / JSON Output。 > > 这不是“模型不够强”，而是“能力约束不匹配”。 > LangChain v1 的解..."
keywords: "Agent, LangChain, AI, DeepSeek, 21 | LangChain v1 Agent：动态选模，DeepSeek-V3.2/V3.2-Speciale在同一个ChatBI里怎么分工？"
mermaid: true
sequence: false
flow: false
mathjax: false
mindmap: false
mindmap2: false
---
> 你想用最强推理模型把 ChatBI 的“分析质量”拉满，但一接上工具就翻车：**模型不支持 Tool Calls / JSON Output**。
>
> 这不是“模型不够强”，而是“能力约束不匹配”。  
> LangChain v1 的解法也很直接：**同一个 Agent 的不同环节，用不同的模型**——工具环节用能调工具的模型，分析环节用推理更强但“只思考”的模型。

---

## 一、现实案例：DeepSeek-V3.2 / V3.2-Speciale 在同一个 ChatBI 里怎么分工？

以 DeepSeek 的最新版本为例（以下描述以官方发布信息/控制台能力矩阵为准）：

- **DeepSeek-V3.2**：强调“推理能力与输出长度的平衡”，更适合日常问答与通用 Agent 任务（尤其是需要工具调用时）。  
- **DeepSeek-V3.2-Speciale**：强调“长思考/强推理/严谨验证”，但在一些渠道/配置下**不支持 Tool Calls（甚至不支持 JSON Output）**；并且它可能要求你使用控制台提供的**专用 Base URL**（不是默认的 `https://api.deepseek.com`）。

这会导致一个非常现实的冲突：

- 你希望用 **Speciale** 做更严谨的“数据分析与逻辑验证”
- 但 **ChatBI 的数据获取离不开数据库工具**（SQL 查询 / 数据抽取）
- Speciale 一旦不支持 tool calls，你把它当“Agent 主模型”就会卡死在工具环节

于是正确的落地姿势变成：**工具走 V3.2，分析走 Speciale**。

---

## 二、第一性原理：ChatBI 不是一个任务，是三段链路

把 ChatBI（数据库问答/分析）拆开，你会得到三段“性质完全不同”的链路：

1. **数据获取（必须能调工具）**：把自然语言问题变成 SQL，并执行查询拿到数据  
2. **分析与验证（需要更强推理，但不一定要工具）**：基于数据做推导、对齐口径、发现异常、给出结论与依据  
3. **表达与收口（偏格式化）**：把结论写成“业务能看懂”的回答（可控长度、结构清晰）

这三段里，只有第 1 段对“能不能 tool call”是硬要求；第 2 段反而更适合用 Speciale 这类“强推理但只思考”的模型。

用一张最小流程图把分工钉死：

```mermaid
flowchart LR
  U["用户问题"] --> M1["V3.2：决策/生成SQL"]
  M1 --> T["run_sql"]
  T --> R["tool结果"]
  R --> M2["Speciale：严格分析<br/>tools=[]"]
  M2 --> M3["V3.2：收口输出"]
```

---

## 三、LangChain v1 里“不同环节用不同模型”到底指什么？

在 LangChain v1（`create_agent`）里，Agent 的一次执行会触发**多次模型调用**（例如：决定是否调用工具、工具结果回填后的再决策、最终回答生成等）。

v1 把“每次模型调用之前，你能做什么”收敛成 middleware：  
你不需要重写 agent，也不需要在 prompt 里做花活——只要在 `wrap_model_call` 里**基于请求信号路由模型**。

核心手法只有一句话：

- 在 middleware 里判断“这一跳该用哪档模型”，然后 `handler(request.override(model=...))`

---

## 四、先把选模“写成白盒”：ChatBI 的选模矩阵怎么画

在 ChatBI 里，一个足够现实、且非常好解释的矩阵通常长这样：

| 环节 | 你能观测到的信号 | 建议模型 | 解释 |
|---|---|---|---|
| 生成 SQL / 决定是否查库 | 本轮需要数据库工具 | V3.2（支持 tool calls） | 工具调用是硬门槛 |
| 数据回填后的分析与验证 | 上一条消息是 tool result，且要求“严格推理/校验” | V3.2-Speciale（不调工具） | 把强推理用在“分析质量”上 |
| 最终回答收口 | 需要可控长度/清晰结构 | V3.2（或更省的） | 主要是表达与格式化 |

为了让它稳定落地，你只需要两类信号：

- **当前是否处于“工具回填后”**（用消息类型判断）  
- **本轮是否开启“严格分析模式”**（从 `runtime.context` 注入）

---

## 五、路由信号从哪来：`state` / `runtime.context` / `store` 三件套

### 1）从 `state` 读“对话态势”

典型信号：

- `messages` 长度（越长越可能需要强模型做整合/消歧）  
- 是否已进入某个阶段（例如已完成鉴权、已拿到关键证据、已触发高风险工具）  

### 2）从 `runtime.context` 读“运行时策略”（强烈建议：敏感信息也只放这里）

典型信号：

- 会员套餐/预算：`plan=free/pro/enterprise`  
- 环境：`env=dev/staging/prod`  
- 风险等级：`risk=low/medium/high`（由你自己的前置策略或守卫计算得出）

这里可以顺手呼应第 17 篇的治理原则：**密钥/Token/Cookie 等凭证，只进 `context`，永不进 messages/state**。

### 3）从 `store` 读“长期偏好”

典型信号：

- 用户偏好“更快/更省/更稳”  
- 租户级策略：默认模型档位、是否允许高成本步骤、灰度开关等

---

## 六、落地实现（案例版）：ChatBI 的“工具模型 + 分析模型”自动分工

下面我们把“ChatBI”的路由逻辑落进 `wrap_model_call`。  
核心思路只有两句：

1. **工具环节**：永远用“支持 tool calls”的模型（例如 V3.2）  
2. **分析环节**：如果你开启了“严格分析”，就把工具禁用，然后切到 Speciale（避免它尝试 tool call）

Speciale 的 Base URL 需要你显式指定（示例：`https://api.deepseek.com/v3.2_speciale_expires_on_20251215`）。

```python
import os
from typing import Callable

from langchain.agents.middleware import ModelRequest, ModelResponse, wrap_model_call
from langchain_deepseek import ChatDeepSeek

# 工具模型：V3.2（能 tool call），走默认 Base URL
tool_model = ChatDeepSeek(
    model="deepseek-chat",
    api_key=os.environ["DEEPSEEK_API_KEY"],
    api_base=os.environ.get("DEEPSEEK_API_BASE", "https://api.deepseek.com"),
)

# 分析模型：V3.2-Speciale（某些配置下不支持 tool calls / JSON Output）
# 注意：如果 Speciale 在控制台给了“专用 Base URL”，需要在这里显式指定
analysis_model = ChatDeepSeek(
    # 以你控制台的实际模型名为准（有的环境会显示为 deepseek-reasoner(1) 之类的变体）
    model=os.environ.get("DEEPSEEK_SPECIALE_MODEL", "deepseek-reasoner"),
    api_key=os.environ["DEEPSEEK_API_KEY"],
    api_base=os.environ["DEEPSEEK_SPECIALE_API_BASE"],
)

@wrap_model_call
def route_model(request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]) -> ModelResponse:
    # ToolMessage 通常会有 type="tool"：表示已拿到数据库结果，进入“分析/收口”
    last_type = getattr(request.messages[-1], "type", "") if request.messages else ""

    # strict_analysis：由调用方通过 runtime.context 注入（模型看不见）
    strict_analysis = bool((request.runtime.context or {}).get("strict_analysis", False))

    # 工具环节用 tool_model；分析环节切 analysis_model，并强制 tools=[]
    if last_type == "tool" and strict_analysis:
        request = request.override(model=analysis_model, tools=[])
    else:
        request = request.override(model=tool_model)

    return handler(request)
```

接入方式也很简单（`run_sql` 是数据库查询工具，示意）：

```python
from langchain.agents import create_agent

agent = create_agent(model=tool_model, tools=[run_sql], middleware=[route_model])
```

这段代码的“现实价值”在于：它把 Speciale 的能力放进了正确的位置——**只在拿到数据之后做分析与校验**，并且用 `tools=[]` 把“工具能力不支持”这件事变成硬约束，而不是祈祷模型自觉。

---

## 七、让它真的可运营：把“选模原因”写进 tracing，而不是写进 prompt

你会遇到一个很现实的问题：上线后老板只问一句——“为什么这周账单变低了/变高了？”  
如果你没有把路由原因可观测化，你就只能回到“推理式排障”。

实践建议是：把选模原因写进 `tags/metadata`，并且和第 20 篇的链路追踪打通（只做索引字段，不塞长文本）：

```python
result = agent.invoke(
    {"messages": [{"role": "user", "content": "按渠道统计上周退款率，并解释异常波动原因"}]},
    # context：只放运行时策略/依赖（敏感信息也应该只在这里）
    context={"tenant_id": "t_1", "strict_analysis": True},
    # config：用于 trace 的可检索信息（模型看不见）
    config={
        "tags": ["chatbi", "route:model"],
        "metadata": {"tenant_id": "t_1", "strict_analysis": True},
    },
)
```

这样你就能在 LangSmith 里直接按 `tenant_id/strict_analysis` 过滤，做“同类请求”的成本与效果对比。

---

## 八、一个常见坑：pre-bound model（尤其 structured output）会让“换模型”失效

如果你把模型提前做了绑定（例如 `model.bind_tools(...)` 或 structured output 相关绑定），在某些场景下**不支持再动态替换成另一套 model**。  
更稳的做法通常是二选一：

1. **每档模型用一致的绑定方式**（强/便宜都 bind 同一组能力，保持可替换）  
2. **把绑定推迟到调用链里**（在路由后，再对选中的 model 进行绑定）

---

## 九、把第 17 / 20 / 21 篇串起来：你需要的是“可治理的 Agent 默认架构”

如果你想把它变成一套能长期跑在生产的基线，可以用一句话概括分工：

- **凭证走 `runtime.context`（第 17 篇）**：敏感信息不入 prompt、不入 state  
- **模型走路由（第 21 篇）**：强模型只在关键时刻上场  
- **链路走 tracing（第 20 篇）**：每次路由决策都可检索、可对比、可复盘

下一篇（第 22 篇）我们再把“工具也做成可路由的资源”补齐：按权限/阶段裁剪工具集，避免工具全暴露带来的越权与误用。
