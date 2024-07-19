---
layout: post
title: 在 OpenAI SDK 和 LangChain OpenAI 中使用代理
categories: [OpenAI, LangChain]
description: "本文介绍了如何在 OpenAI SDK 和 LangChain OpenAI 中使用代理。通过设置环境变量或在代码中直接配置代理，可以确保在进行 API 调用时，所有请求都会通过指定的代理服务器。这种方法可以帮助开发者在受限的网络环境中正常使用 OpenAI 的服务，并且提高网络请求的安全性和灵活性。" 
keywords: OpenAI, LangChain, 代理, SDK, API, 网络请求
mermaid: false
sequence: false
flow: false
mathjax: false
mindmap: false
mindmap2: false
---

# 在 OpenAI SDK 和 LangChain OpenAI 中使用代理

在开发过程中，使用代理服务器可以帮助你控制网络请求的流向、提高安全性或遵循公司的网络政策。本文将介绍如何在 OpenAI SDK 和 LangChain OpenAI 中使用代理。

## 在 OpenAI SDK 中使用代理

### 安装必要的库

确保你已经安装了 OpenAI SDK 和 `httpx` 库。如果尚未安装，可以使用以下命令进行安装：

```bash
pip install openai httpx
```

### 使用代理配置 OpenAI SDK

以下是一个使用代理配置 OpenAI SDK 的代码示例：

```python
import httpx
from openai import OpenAI

# 配置 OpenAI 客户端，使用代理
client = OpenAI(
    api_key="sk-xxx",
    http_client=httpx.Client(
        proxies="http://127.0.0.1:8118",  # 代理服务器的URL
        transport=httpx.HTTPTransport(local_address="0.0.0.0"),  # 本地地址配置
        verify=False  # 禁用SSL证书验证（不推荐在生产环境中使用）
    )
)

# 创建一个聊天完成请求
completion = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[
        {"role": "user", "content": "你可以做什么."}
    ]
)

# 打印返回的消息
print(completion.choices[0].message)
```

### 解释

1. **导入库**：
   - `httpx` 是一个用于发出 HTTP 请求的库。
   - `OpenAI` 是 OpenAI SDK 中的主要类，用于与 OpenAI API 进行交互。

2. **配置 OpenAI 客户端**：
   - `api_key`：你的 OpenAI API 密钥。
   - `http_client`：一个自定义的 `httpx.Client` 实例，用于配置代理。
     - `proxies`：代理服务器的 URL，例如 `http://127.0.0.1:8118`。
     - `transport`：配置本地地址为 `0.0.0.0`。
     - `verify`：设置为 `False` 以跳过 SSL 证书验证（不推荐在生产环境中使用）。

3. **创建聊天完成请求**：
   - 使用 `client.chat.completions.create` 方法创建一个聊天完成请求。
   - `model`：使用的模型名称，例如 `gpt-4-turbo`。
   - `messages`：消息列表，其中包含用户输入的内容。

4. **打印返回的消息**：
   - 打印返回的消息内容。

### 备注

- **安全性**：在生产环境中，不建议禁用 SSL 证书验证（`verify=False`），这样可能会导致安全问题。
- **API 密钥管理**：确保妥善管理和保护你的 API 密钥，不要在公共代码库中泄露。

## 在 LangChain OpenAI 中使用代理

LangChain 是一个构建基于语言模型的应用程序的库，可以与 OpenAI 的 Chat API 进行交互。下面介绍如何在 LangChain 中配置代理。

### 安装必要的库

确保你已经安装了 LangChain 和 OpenAI SDK：

```bash
pip install langchain openai
```

### 使用代理配置 LangChain 的 `ChatOpenAI`

以下是一个示例，展示了如何在使用代理的情况下配置和使用 LangChain 的 `ChatOpenAI`：

```python
import os
import requests
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage

# 设置 API 密钥
os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"

# 配置代理
proxy = "http://127.0.0.1:8118"

# 创建一个带有代理的请求会话
session = requests.Session()
session.proxies = {
    "http": proxy,
    "https": proxy
}

# 定义一个自定义的 ChatOpenAI 类来使用带代理的请求会话
class ProxyChatOpenAI(ChatOpenAI):
    def _call_openai(self, messages, stop=None):
        openai_requestor = self._get_requestor()
        openai_requestor.session = session
        return super()._call_openai(messages, stop=stop)

# 实例化带代理的 ChatOpenAI 类
chat = ProxyChatOpenAI(
    model="gpt-4-turbo", 
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# 示例对话
messages = [
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content="Hello, how are you?")
]

response = chat(messages)
print(response.content)
```

### 解释

1. **设置 API 密钥和代理**：
   - 使用环境变量 `OPENAI_API_KEY` 设置 OpenAI 的 API 密钥。
   - 定义代理 URL，例如 `http://127.0.0.1:8118`。

2. **创建带代理的请求会话**：
   - 使用 `requests.Session()` 创建一个会话，并设置代理。

3. **自定义 `ChatOpenAI` 类**：
   - 继承 `ChatOpenAI` 类，并重写 `_call_openai` 方法，使用带代理的请求会话。
   - 在 `_call_openai` 方法中，设置 `openai_requestor` 的会话为带代理的会话。

4. **实例化自定义的 `ChatOpenAI` 类**：
   - 使用自定义的 `ProxyChatOpenAI` 类，传入所需参数，例如模型名称和 API 密钥。

5. **示例对话**：
   - 创建一个消息列表，并调用自定义的 `ChatOpenAI` 实例进行对话。

## 总结

本文介绍了如何在 OpenAI SDK 和 LangChain OpenAI 中使用代理。通过设置环境变量或在代码中直接配置代理，可以确保在进行 API 调用时，所有请求都会通过指定的代理服务器。这种方法可以帮助开发者在受限的网络环境中正常使用 OpenAI 的服务，并且提高网络请求的安全性和灵活性。
