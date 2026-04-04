---
layout: post
title: "15 | LangGraph v1 实战：LC_OUTPUT_VERSION：序列化与前后端对齐的关键开关"
categories: ["LangGraph", "LangChain", "AI"]
description: "在前两篇里，我们一直在用一个看似「理所当然」的属性："
keywords: "LangGraph, LangChain, AI, 15 | LangGraph v1 实战：LC_OUTPUT_VERSION：序列化与前后端对齐的关键开关"
mermaid: false
sequence: false
flow: false
mathjax: false
mindmap: false
mindmap2: false
---
## 一、一个容易被忽略的问题：content_blocks 到底存在哪里？

在前两篇里，我们一直在用一个看似「理所当然」的属性：

```python
response.content_blocks
tool_message.content_blocks
```

但如果你去读 LangChain v1 的迁移指南，会发现有这样一句话（非常关键）：

> 标准 content blocks **默认不会**序列化到 `content` 属性中。  
> 如果应用需要在 LangChain 之外访问标准表示，可以选择将它们序列化进去。

这句话背后隐藏着几个工程上的现实考量：

- 在很多情况下，LangChain 内部访问 `content_blocks` 就够了，没有必要把完整块结构再「复制」一份到 `content`；
- 一旦你把块结构完整地塞进 `content`，消息体积会明显变大，对存储/网络/日志都有成本；
- 但如果你有「前端 / 其他服务 / 日志平台」需要拿到标准化的 `content_blocks`，又不能直接依赖 LangChain 的 Python/JS 类型，那就必须要有一个可序列化的版本。

这一篇就围绕这个问题展开：

1. `content_blocks` 默认是「延迟解析」的，它们是如何从 `content` 中被解析出来的；
2. 什么时候需要把标准 `content_blocks` 序列化回 `content`，以及如何开启；
3. 前后端协同、跨服务调用与调试时，如何利用这套机制搭建「统一消息格式」。

---

## 二、默认模式：content_blocks 是懒解析视图，而不是持久字段

先看一个极简例子（Python）：

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("gpt-4o-mini")
response = model.invoke("用一句话介绍一下你自己。")

print("content:", response.content)
print("has content_blocks:", hasattr(response, "content_blocks"))
```

在 v1 模式下，这里的行为大致是：

- `response.content`：是 provider 原生的内容（可能是字符串，也可能是 JSON 结构）；
- `response.content_blocks`：是一个**懒解析属性**，第一次访问时，LangChain 会把 `content` 转成标准块结构。

可以简单理解为：

```python
class AIMessage(...):
    @property
    def content_blocks(self):
        # 伪代码：第一次访问时解析 content
        if not hasattr(self, "_content_blocks"):
            self._content_blocks = parse_to_standard_blocks(self.content)
        return self._content_blocks
```

这有两个直接好处：

- 对于不关心 `content_blocks` 的用户，不会平白多做一次解析；
- 对于语义搜索 / 存储 / 日志，只要存 `content`，就可以在回放时重新解析出标准块。

问题在于：**一旦你跨出了 LangChain 的运行时环境（比如通过 HTTP 把消息传给前端），对端就无法再调用这个属性，也就拿不到标准化结构**。

这就是「序列化 standard content 」的需求来源。

---

## 三、开启标准 content_blocks 序列化：LC_OUTPUT_VERSION / output_version

LangChain v1 提供了两种方式，让你可以显式「把标准 content_blocks 序列化进消息内容」。

### 3.1 方式一：全局环境变量 LC_OUTPUT_VERSION

最简单的方式是在环境里加一行：

```bash
export LC_OUTPUT_VERSION=v1
```

然后你的应用在这个环境下启动，所有通过 LangChain 初始化的模型，都会默认启用 v1 序列化行为。

这种方式适合：

- 你有一个统一的服务入口（如后端 API），希望所有模型输出都遵循统一版本；
- 你不想在每个模型初始化处都手动传版本参数。

### 3.2 方式二：在初始化模型时显式指定 output_version

如果你只想对某些模型开启序列化，可以在初始化时显式传入版本。

Python 版示例：

```python
from langchain.chat_models import init_chat_model

model = init_chat_model(
    "gpt-5-nano",
    output_version="v1",
)
```

JS/TS 版示例：

```ts
import { initChatModel } from "langchain";

const model = await initChatModel("gpt-5-nano", {
  outputVersion: "v1",
});
```

开启之后，LangChain 会在内部做两件事：

1. 按照 v1 规范组织 `content` 字段（包括标准化的 content blocks 表示）；  
2. `content_blocks` 属性仍然可用，只不过这次它可以直接从 `content` 中「完美还原」。

换句话说：

> v1 模式让 `content` 成为一个「可跨服务传输的标准消息体」，  
> `content_blocks` 则是这个消息体在 LangChain 运行时内的「对象视图」。

---

## 四、一个前后端协同示例：服务端调用 LangChain，前端直接渲染 content_blocks

假设我们有这样的需求：

- 服务端用 LangChain v1 调用模型和 MCP 工具；
- 前端需要展示：
  - 模型的推理过程（reasoning blocks）；
  - 工具返回的图片和文字（image/text blocks）；
  - 最终给用户的回答；
- 前端不希望依赖 LangChain 的 SDK，只希望拿到一份「标准 JSON」。

### 4.1 服务端：开启 v1 输出，并返回标准消息结构

服务端可以这样组织代码（简化示例）：

```python
from typing import Any, Dict

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage

model = init_chat_model(
    "gpt-4o-mini",
    output_version="v1",  # 关键：开启 v1 序列化
)

def ask_model(question: str) -> Dict[str, Any]:
    """返回一个适合直接给前端消费的标准消息结构。"""
    response = model.invoke(
        [HumanMessage(content=question)]
    )

    # v1 模式下，response.content 已经是结构化消息体
    return {
        "role": "assistant",
        "content": response.content,
    }
```

注意这里的设计：

- 我们直接把 `response.content` 原样返回给前端；
- 不在中间层做任何「猜测」或「拆分」；
- 约定前后端都遵守这套 v1 标准结构。

### 4.2 前端：只依赖 v1 标准 JSON，渲染不同类型块

前端拿到的是这样的 JSON（示意）：

```jsonc
{
  "role": "assistant",
  "content": [
    { "type": "reasoning", "id": "rs_abc123", "summary": [ ... ] },
    { "type": "text", "text": "这是给用户看的最终回答..." }
  ]
}
```

前端代码就可以像处理普通 JSON 一样，分类型渲染：

```ts
type ContentBlock =
  | { type: "text"; text: string }
  | { type: "reasoning"; summary: any[] }
  | { type: "image"; url?: string; base64?: string; mime_type?: string }
  // ... 其他类型块

function renderBlocks(blocks: ContentBlock[]) {
  return blocks.map((block, idx) => {
    switch (block.type) {
      case "text":
        return <p key={idx}>{block.text}</p>;
      case "reasoning":
        return (
          <details key={idx}>
            <summary>推理过程（开发者模式）</summary>
            {/* 展示 summary 内容 */}
          </details>
        );
      case "image":
        const src =
          block.url ??
          `data:${block.mime_type ?? "image/png"};base64,${block.base64}`;
        return <img key={idx} src={src} />;
      default:
        return null;
    }
  });
}
```

整个过程里，前端完全不需要知道「什么是 LangChain」，只要知道「我们约定使用 v1 标准内容块结构」即可。

---

## 五、调试视角：让日志和回放也直接用标准 content_blocks

在有一定复杂度的 Agent 系统里，调试通常会涉及：

- 离线回放某个会话的所有消息；
- 重放某次出错的工具调用；
- 把某些「经典错误案例」录入测试用例。

如果日志里只有 provider 原生字符串/JSON，你在回放时就需要：

- 再写一堆 provider-specific 的解析代码；
- 很难利用 LangChain 提供的 `content_blocks` 工具链。

开启 v1 序列化之后，你可以：

- 在日志中直接记录整个 `content` 字段（它本身就是标准结构）；
- 在回放脚本里，直接构造 `AIMessage(content=logged_content)`，然后让 LangChain 帮你恢复 `content_blocks` 视图：

```python
from langchain_core.messages import AIMessage

def replay_from_log(logged_content):
    msg = AIMessage(content=logged_content)
    # 现在可以直接用 content_blocks 做进一步分析
    for block in msg.content_blocks:
        print(block["type"], "->", str(block)[:100])
```

这在构建「灰度回放」「失败案例分析」等工具时非常有价值。

---

## 六、何时该开，何时不该开？实践中的取舍

最后一个关键问题是：**是不是应该一上来就全局打开 v1 序列化？**

从工程实践角度，我的建议是：

### 6.1 适合开启的场景

- 你有前端/其他服务需要直接消费标准 content_blocks；
- 你要把消息存入长期日志/审计系统，并希望以统一结构来回放和分析；
- 你准备构建一套跨语言的调试/观测工具（例如用 Go/Java 写一个 trace 处理器）。

在这些场景下，全局 `LC_OUTPUT_VERSION=v1` 是合理的：

```bash
export LC_OUTPUT_VERSION=v1
uv run python app.py
```

### 6.2 可以暂时不开的场景

- 你的应用完全在一个 LangChain 运行时里，不需要跨进程/跨语言传输消息；
- 日志量非常大，对消息体积敏感，而你又不需要长期保存完整的 content_blocks；
- 你只把模型/工具当成内部组件，不对外暴露通用 API。

这种情况下，保持默认懒解析模式即可：

- 内部需要时用 `message.content_blocks`；
- 日志里根据需要只记录少量摘要字段。

### 6.3 混合策略：按产品线/接口粒度开启

更精细的做法是：

- 对「面向前端/第三方的 API」所用的模型，显式设置 `output_version="v1"`；
- 对纯内部使用的模型，保持默认行为，以减少不必要的体积膨胀。

这可以在你的模型工厂/依赖注入层统一配置，而无需在业务代码到处 if/else。

---

## 七、小结：把 content_blocks 变成系统级协议，而不只是 SDK 功能

到目前为止，content_blocks 系列三篇已经覆盖了三个层面：

1. 第 12–13 篇：从 DeepSeek 推理可视化到多模态输入输出——解决「模型层面」的问题；
2. 第 14 篇：MCP 工具多模态返回统一解析——解决「工具层面」的问题；
3. 第 15 篇（本文）：标准 content_blocks 序列化与 v1 输出——解决「跨服务/前后端协同与调试」的问题。

如果只用一句话总结这一篇：

> `LC_OUTPUT_VERSION` / `output_version` 让标准 content_blocks  
> 从「LangChain SDK 内部的便利工具」，  
> 变成了「整个系统的统一消息协议」。

接下来，我们会在 Middleware 专题里，基于这套统一协议，继续往前走一步：

- 在 `before_model` / `after_model` 里，对标准化的 content_blocks 做输入脱敏、输出审查、推理过程审计；
- 让安全、可观测性、版本控制不再是「附加功能」，而是整个 Agent 架构的内建能力。
