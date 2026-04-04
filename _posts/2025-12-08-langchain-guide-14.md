---
layout: post
title: "14 | LangGraph v1 实战：MCP 工具多模态返回，用 content_blocks 一口收"
categories: ["LangGraph", "LangChain", "AI"]
description: "上一篇我们解决的是「模型多模态」的问题："
keywords: "LangGraph, LangChain, AI, MCP, 14 | LangGraph v1 实战：MCP 工具多模态返回，用 content_blocks 一口收"
mermaid: false
sequence: false
flow: false
mathjax: false
mindmap: false
mindmap2: false
---
## 一、问题升级：不仅模型是多模态，工具也在变多模态

上一篇我们解决的是「模型多模态」的问题：

- 输入：文本 + 图片 → 用 `content_blocks` 组织成统一结构；
- 输出：文本 + 图片 → 用 `response.content_blocks` 统一解析。

但在 LangChain v1 + MCP 的世界里，还有一条容易被忽略的多模态通道：

- **工具（Tool）也可以返回多模态内容**——例如：
  - 截图工具返回「文字说明 + 截图」；
  - 报表生成工具返回「图表图片 + 描述文字」；
  - 监控系统工具返回「告警详情 + 截图」。

如果我们不做统一处理，很容易出现这样的工程现状：

- 模型输出走一套解析逻辑；
- 工具输出走另一套完全不同的解析逻辑；
- MCP 服务器之间各自定义自己的 JSON 结构，前端和日志系统苦不堪言。

LangChain v1 在 MCP 集成里给出的答案很直接：

> MCP 工具返回的多模态内容，同样会被适配成标准 `content_blocks`，挂载在 `ToolMessage.content_blocks` 上。

这一篇我们聚焦三件事：

1. 用一个简单的 MCP 多模态工具例子，说明「工具多模态 → content_blocks」的适配过程；
2. 展示如何在 Agent 结果里统一解析工具的 `content_blocks`；
3. 给出一套「前端 / 日志 / 搜索」统一消费工具多模态输出的实践建议。

---

## 二、MCP 多模态工具长什么样？先从接口说起

设想一个场景：我们有一个 MCP 服务器，提供一个 `take_screenshot` 工具：

- 输入：当前页面 URL；
- 输出：一段说明文本 + 页面截图（图片）。

在 MCP 协议层面，这个工具可能返回类似这样的结构（伪代码）：

```jsonc
{
  "content": [
    {
      "type": "text",
      "text": "已为你截取当前页面，分辨率为 1920x1080。"
    },
    {
      "type": "image",
      "url": "https://example.com/screenshot/abc123.png"
    }
  ]
}
```

对于 LangChain 而言，这个返回会经过 `langchain_mcp_adapters` 适配，最终出现在 `ToolMessage` 上：

- `ToolMessage.content`：provider 原生内容（通常就是上面那份 JSON）；
- `ToolMessage.content_blocks`：一份「跨 provider 标准化」后的 `content_blocks` 列表。

我们更关心的是后者。

---

## 三、从 MCP 到 LangChain：MultiServerMCPClient 与工具列表

在 LangChain v1 里，我们通常这样接入 MCP 服务器：

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

async def init_agent_with_mcp():
    client = MultiServerMCPClient(
        servers={
            "browser": {
                "command": "mcp-browser-server",
                "args": [],
            },
            # 也可以挂更多 MCP 服务器
        }
    )

    tools = await client.get_tools()

    agent = create_agent(
        model="claude-3-5-sonnet-20251001",
        tools=tools,
    )
    return agent
```

此时，`tools` 里就已经包含了 MCP 工具的所有定义信息——包括那个返回多模态内容的 `take_screenshot`。

当 Agent 在对话中决定调用这个工具时，LangChain 会：

1. 根据 Tool 调用信息，转发到对应 MCP 服务器；
2. 收到 MCP 返回的多模态内容；
3. 生成一个 `ToolMessage`，其中包含：
   - `content`：provider 原始格式；
   - `content_blocks`：标准化后的多模态块列表。

我们现在要做的，就是统一解析这些 `ToolMessage.content_blocks`。

---

## 四、统一解析工具多模态返回：遍历 ToolMessage.content_blocks

先看官方文档给出的典型用法（简化版）：

```python
result = await agent.ainvoke(
    {"messages": [{"role": "user", "content": "截一张当前页面的图，并简单说明。"}]}
)

for message in result["messages"]:
    if message.type == "tool":
        # 原始内容（provider 格式）
        print("Raw content:", message.content)

        # 标准 content_blocks
        for block in message.content_blocks:
            if block["type"] == "text":
                print("Text:", block["text"])
            elif block["type"] == "image":
                print("Image URL:", block.get("url"))
                print("Image base64 prefix:", block.get("base64", "")[:50], "...")
```

我们可以在这个基础上封装一层，让「工具多模态返回」在业务代码里变得像「普通多模态输出」一样好用。

### 4.1 把 ToolMessage 按工具名聚合

先写一个工具函数，把 Agent 返回中的工具消息统一整理一下：

```python
from typing import Any, Dict, List, Tuple
from langchain_core.messages import BaseMessage

def collect_tool_messages(messages: List[BaseMessage]) -> Dict[str, List[BaseMessage]]:
    """按工具名聚合 ToolMessage，便于后续处理。"""
    tool_messages: Dict[str, List[BaseMessage]] = {}
    for msg in messages:
        if msg.type == "tool":
            tool_name = msg.name or "unknown_tool"
            tool_messages.setdefault(tool_name, []).append(msg)
    return tool_messages
```

然后再写一个「块级解析器」：

```python

def parse_tool_multimodal_blocks(
    tool_msg: BaseMessage,
) -> Tuple[List[str], List[Dict[str, Any]]]:
    """解析单条工具消息中的文本与图片块。"""
    texts = []
    images = []

    for block in tool_msg.content_blocks:
        if block.get("type") == "text":
            texts.append(block.get("text") or "")
        elif block.get("type") == "image":
            images.append(block)

    return texts, images

### 4.2 进一步处理：用 deepseek-ocr + ChatOllama 为截图生成文本

在很多场景里，我们不仅想“看到截图”，还想：

- 把截图里的文字内容纳入后续检索 / 审计；
- 在故障回溯时，能直接搜索到「某次截图中出现的报错信息」；
- 为后续的模型调用提供更丰富的上下文。

这时候，就可以在上面的基础上再加一层 **OCR 处理**：

```python
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

def build_ocr_model() -> ChatOllama:
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model_id = os.getenv("OCR_MODEL", "deepseek-ocr")
    return ChatOllama(
        model=model_id,
        base_url=base_url,
        temperature=0,
        output_version="v1",
    )

async def ocr_images_from_tool_message(tool_msg: BaseMessage) -> str:
    """对 ToolMessage 中的图片块做 OCR，返回合并后的文本。"""
    _, images = parse_tool_multimodal_blocks(tool_msg)
    if not images:
        return ""

    ocr_model = build_ocr_model()
    ocr_texts = []

    for img in images:
        base64_data = img.get("base64")
        if not base64_data:
            # 只有 URL 的情况可以按需自行下载，这里先跳过
            continue

        prompt = (
            "请逐行识别图片中的文字，保持原有行结构，"
            "只输出纯文本，不要额外解释。"
        )

        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {
                    "type": "image",
                    "base64": base64_data,
                    "mime_type": img.get("mime_type") or "image/png",
                },
            ]
        )

        resp = await ocr_model.ainvoke([message])

        blocks = getattr(resp, "content_blocks", None)
        if blocks:
            text_blocks = [
                b.get("text") or ""
                for b in blocks
                if b.get("type") == "text" and b.get("text")
            ]
            if text_blocks:
                ocr_texts.append("\n".join(text_blocks).strip())
                continue

        # 回退到 text / content
        if hasattr(resp, "text") and isinstance(resp.text, str):
            ocr_texts.append(resp.text.strip())
        elif isinstance(resp.content, str):
            ocr_texts.append(resp.content.strip())

    return "\n\n".join(t for t in ocr_texts if t)
```

在实际调用里，你可以在打印图片信息后追加一段：

```python
ocr_text = await ocr_images_from_tool_message(msg)
if ocr_text:
    print("=== OCR 识别结果（来自 deepseek-ocr + ChatOllama） ===")
    print(ocr_text)
```

这样，“截图工具”就不再只是一个 UI 友好的附加信息，而是变成了：

- 可以被检索 / 索引的文本内容；
- 可以被模型继续消费的上下文（例如后续自动诊断某个错误页面）。
```

这样，在业务代码里我们可以很自然地写出：

```python

async def run_with_screenshot(agent):
    result = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "截一张当前页面的图，并告诉我当前页面的核心信息。",
                }
            ]
        }
    )

    messages = result["messages"]
    tool_messages = collect_tool_messages(messages)

    for tool_name, msgs in tool_messages.items():
        print(f"工具 {tool_name} 共被调用 {len(msgs)} 次。")

        for idx, msg in enumerate(msgs):
            print(f"--- 第 {idx+1} 次调用 ---")
            texts, images = parse_tool_multimodal_blocks(msg)

            print("文本部分：")
            print("\n".join(texts))

            print("图片部分：")
            for img in images:
                print("  mime_type:", img.get("mime_type"))
                print("  url:", img.get("url"))
                print("  base64 前 50 字符:", img.get("base64", "")[:50], "...")
```

这一段逻辑的关键在于：

- 完全不关心 MCP 服务端的具体 JSON 格式，只认 `content_blocks`；
- 当后续更换 MCP 服务器或增加新的多模态工具时，前端/日志层都可以无感迁移；
- 这也为后续的 middleware 和安全审计提供了一个统一入口。

---

## 五、前端、日志与搜索：统一消费工具多模态输出

有了标准 `content_blocks`，我们可以对 MCP 工具的多模态输出做更体系化的处理。这里给三个常见方向。

### 5.1 前端渲染：一套组件，消费所有多模态块

前端可以约定：无论是模型输出还是工具输出，只要拿到一份 `content_blocks` 列表，就按如下策略渲染：

- `type == "text"`：渲染为富文本（支持 markdown）；
- `type == "image"`：
  - 如果有 `url`：直接当图片 URL 用；
  - 如果只有 `base64`：转成 `data:image/...;base64,...`；
- 未来如果有 `type == "reasoning"`：可以在「开发者模式」里展示推理过程。

对应地，后端只需要给前端返回一个统一结构：

```jsonc
{
  "role": "tool",
  "name": "take_screenshot",
  "content_blocks": [
    { "type": "text", "text": "已为你截取当前页面..." },
    { "type": "image", "url": "https://..." }
  ]
}
```

这比在前端到处判断「这是模型输出还是工具输出」「这是哪家 MCP 的 JSON」要干净太多。

### 5.2 日志与审计：多模态内容分层落盘

在日志与审计层，我们可以对工具输出做分层落盘：

- 文本块：落到普通日志或搜索引擎（如 ES / OpenSearch）；
- 图片块：落到对象存储（S3 / OSS / COS），日志里只记录 URL + 摘要；
- 安全审计：可以在异步任务里对图片做 OCR / 风险识别（例如本篇示例中的 `deepseek-ocr + ChatOllama`）。

因为工具输出已经被标准化成 `content_blocks`，我们可以在 middleware 或日志中间件里统一处理：

```python
def log_tool_multimodal(tool_msg: BaseMessage):
    for block in tool_msg.content_blocks:
        if block.get("type") == "text":
            log_text(block["text"])
        elif block.get("type") == "image":
            url = block.get("url")
            if not url:
                url = upload_image_base64(block["base64"])
            log_image_reference(url, meta={"tool": tool_msg.name})
```

### 5.3 向量化与搜索：从多模态结果中抽取可检索文本

很多人会希望把工具输出的结果也纳入后续检索，例如：

- 把「截图 + 文字说明」转成一条多模态「监控事件」；
- 在后续排查问题时，能按照自然语言搜索到这些历史记录。

在有了 `content_blocks` 之后，我们可以做一个简单的「文本抽取策略」：

- 只取 `type == "text"` 的内容做向量化；
- 对图片，如果没有 OCR 能力，可以先只记录 URL，后续有需要再补；
- 在向量索引的 metadata 里加上 `source: tool_name`、`has_image: true` 等字段。

---

## 六、实践建议：把「工具多模态」当成第一等公民

最后，总结几个落地层面的建议。

### 6.1 一开始就设计成「模型和工具统一多模态结构」

不要等到工具已经写了一堆，前端也已经给模型输出适配好了，才开始补工具多模态的统一处理。

更好的做法是：

- 从一开始就规定：**所有内容（无论来自模型还是工具），在后端统一变成标准 `content_blocks`**；
- 前端与日志系统只消费这一个统一结构；
- MCP 服务器的实现细节，全部被屏蔽在 LangChain + MCP 适配层。

### 6.2 工具返回尽量「结构 + 多模态」并存

如果工具本身就需要返回结构化数据（如 JSON），不要把所有东西都塞进图片里，让模型去「看图写 JSON」。

更推荐的模式：

- 工具返回：
  - 文本描述（关键结论）；
  - JSON 结构（可执行的数据）；
  - 图片（辅助理解的截图或图表）。
- `content_blocks` 里可以混合：
  - `type == "text"`：描述；
  - `type == "image"`：截图；
  - `type == "json"` 或专门的结构化块（视具体实现而定）。

这样做有两个好处：

- 业务逻辑可以直接消费 JSON，而不必再靠模型「看图解释数据」；
- 画像与审计系统可以对结构和多模态分别做分析。

### 6.3 把工具多模态纳入统一的安全策略

工具返回的图片，同样存在隐私与安全风险，例如：

- 截图中可能包含用户个人信息、内部系统地址；
- 某些截图不应该被发送到第三方。

在架构上，我们应该：

- 在 middleware 层对 `ToolMessage.content_blocks` 做统一检查；
- 对敏感工具返回的图片块，支持：
  - 不落盘；
  - 模糊化处理后再存储；
  - 仅对特定角色开放查看权限。

在实践中，你可以像第 13 篇那样，把「图片 → ChatOllama(deepseek-ocr) → 文本」这一段视为系统级能力，然后：

- 在日志/审计管线里对所有工具图片统一跑一遍 OCR，将结果写入文本索引；
- 在 Agent 状态或中间件里，把 OCR 结果追加到新的 `text` 内容块中，供后续模型使用。

---

## 七、小结：从 MCP 到全局多模态基础设施

这一篇我们把重点从「模型多模态」转向了「工具多模态」，核心结论是：

- MCP 工具返回的多模态内容，同样会被 LangChain 适配成标准 `content_blocks`；
- 只要你在 Agent 层统一从 `ToolMessage.content_blocks` 读取数据，就可以让前端、日志、审计、搜索都基于同一套结构工作；
- 把工具多模态当成第一等公民，是未来构建复杂 Agent & MCP 生态时很关键的一步。

下一篇（第 15 篇），我们会把视角再往外扩一层：  
**当你希望前端或其他服务也直接消费标准 `content_blocks` 时，如何通过 `LC_OUTPUT_VERSION` / `output_version` 把这些块序列化进消息 `content`，并在调试和跨服务调用里保持一致性。**
