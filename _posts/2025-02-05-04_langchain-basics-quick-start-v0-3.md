---
layout: post
title: 04 | LangChain 快速入门
categories: [AI, LangChain]
description: 本文将介绍如何使用 LangChain 快速入门。    
keywords: AI, LangChain, LangChain-OpenAI,
mermaid: false
sequence: false
flow: false
mathjax: false
mindmap: false
mindmap2: false
---

## 1. 引言

在之前的分享中，我们讨论了如何利用 OpenAI Python SDK 开发定制的 GPT 模型、优化 Prompt 工程、实现基于嵌入的推荐系统。这些内容为我们搭建了一个强大的基础，但在实际应用中，复杂的业务需求往往需要多个任务的协同处理，如何高效地整合这些功能成为了一大挑战。

LangChain 正是为了解决这一问题而生。它作为一个专为大语言模型服务的开发框架，提供了灵活的模块化架构，能够将不同任务和工具有机地串联起来，使我们能够轻松构建复杂的任务链、扩展模型的能力，并与外部系统无缝集成。通过 LangChain，我们不仅可以进一步优化现有的 GPT 应用，还可以实现更复杂的多步骤自动化操作，提升智能化应用的开发效率。

接下来，我们将快速介绍 LangChain 的核心概念和架构。

![image.png](/images/posts/2025-02-05-04_langchain-basics-quick-start-v0-3_1.png)

## 2. LangChain 的核心概念

基于最新的 LangChain 架构图，LangChain 通过模块化的设计，涵盖了从任务链管理到部署的全方位功能。其核心概念不仅包括任务链的构建与管理，还涉及多种工具集成和上下文处理。以下是几个关键部分的概述：

### 2.1 LangChain 与 LangGraph（架构层）

**LangChain** 和 **LangGraph** 位于架构层，构成了整个系统的基础。LangChain 是整个框架的核心，它提供了构建和管理任务链的工具，并支持与大语言模型的交互。LangGraph 则负责处理更复杂的数据结构和依赖管理，适合需要跟踪和管理复杂任务流的应用场景。

- **LangChain**：用于构建链式任务，允许开发者将多步骤任务分解为多个独立的组件。这种链式架构可以处理输入的多次流转，生成更为复杂的输出。
- **LangGraph**：则是 LangChain 的扩展，用于处理复杂的任务图（DAG）。当任务存在分支或者并行任务时，LangGraph 可以通过图结构追踪依赖关系，确保任务流按照预期顺序执行。

### 2.2 Integrations（组件层）

在组件层，LangChain 提供了**Integrations**模块，用于将外部系统、API 和工具与任务链集成。这一层次允许开发者将外部工具（例如数据库、API 或计算工具）无缝集成到任务链中，进一步增强大语言模型的功能。

- **工具集成**：通过 Agents 实现与外部工具的交互，支持诸如 Python 执行、Web 搜索等操作。
- **API 集成**：允许模型在生成内容的同时调用外部 API 完成特定的操作，如数据查询、计算任务等。

### 2.3 LangGraph Cloud（部署层）

**LangGraph Cloud** 位于架构的顶层，负责商业部署。这是 LangChain 的云端服务，提供了企业级的任务链部署和管理平台。通过云部署，用户可以将模型与任务链快速应用于实际业务场景，享受更高的可靠性与可扩展性。

### 2.4 LangSmith（辅助工具）

**LangSmith** 作为开发者辅助工具，包含了一系列用于调试、优化和监控的工具。它为 Prompt 管理、注释、测试和监控提供了一站式的解决方案，帮助开发者更高效地设计和调优任务链。

- **Debugging**：调试任务链，检查错误或逻辑问题。
- **Playground**：提供实验环境，允许开发者在真实环境前模拟不同的任务链。
- **Prompt Management**：用于管理和优化不同任务中的 Prompt 模板。
- **Testing & Monitoring**：确保部署后任务链的可靠性和性能。

这一架构使得 LangChain 不仅适用于简单的任务链处理，还能够通过 LangGraph 处理复杂的并行任务和依赖管理，并且提供了企业级的云端解决方案以及开发者友好的工具支持。

### 3. LangChain 的主要组件

我们打开网页：https://python.langchain.com/docs/integrations/platforms/，可以看到左侧的目录：

![image.png](/images/posts/2025-02-05-04_langchain-basics-quick-start-v0-3_2.png)

我们可以看到，LangChain 提供了多个关键组件，帮助开发者构建灵活的语言模型应用。以下是一些主要组件的概述：

### 3.1 提供商（Providers）

LangChain 支持多个主流提供商，包括：

- **Anthropic**
- **AWS**
- **Google**
- **Hugging Face**
- **Microsoft**
- **OpenAI（**因为 G2M 的大模型服务模拟了 OpenAI 的服务，所以也是可以使用 LangChain 的**）**
- ……

### 3.2 组件（Components）

1. **聊天模型（Chat Models）**：支持多种聊天交互的模型。
2. **大语言模型（LLMs）**：连接到各种语言模型的接口。
3. **嵌入模型（Embedding Models）**：用于处理文本数据的嵌入表示。
4. **文档加载器（Document Loaders）**：用于从不同格式加载文档的工具。
5. **向量存储（Vector Stores）**：用于存储和检索文本嵌入的数据库。
6. **检索器（Retrievers）**：从文档或数据库中提取相关信息的工具（RAG）。
7. **工具/工具包（Tools/Toolkits）**：提供额外功能的模块。

### 3.3 其他组件（Other）

- **文档转换器（Document Transformers）**：用于处理和转换文档的工具。
- **模型缓存（Model Caches）**：用于提高模型响应速度的缓存机制。
- **图（Graphs）**：用于表示和处理复杂关系的数据结构。
- **消息历史（Message Histories）**：存储会话历史以便后续使用。
- **回调（Callbacks）**：用于实现事件驱动编程的回调机制。
- **聊天加载器（Chat Loaders）**：用于从外部源加载聊天数据。
- **适配器（Adapters）**：用于在不同组件之间进行适配的工具。

这些组件的组合使得咱们开发者能够灵活地构建和扩展应用，满足各种业务需求。接下来，我们将探讨如何利用这些组件在实际项目中实现业务逻辑。

## 4. LangChain 实践示例

首先我们还是要安装一下我们后面要使用到的依赖：

```python
%pip install openai  # 安装 OpenAI 库，用于与 OpenAI API 交互
%pip install langchain  # 安装 LangChain 库，用于构建和管理语言模型链
%pip install langchain-openai  # 安装 LangChain-OpenAI 库，用于将 LangChain 与 OpenAI 集成
```

### 4.1 使用 LangChain 进行简单问答

在本示例中，我们将使用 LangChain 的 `ChatOpenAI` 类进行简单问答。通过定义用户消息并调用 OpenAI API，我们可以对比一下前面的第一节课，代码量要少很多。

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o")

messages = [
    {"role": "user", "content": "简单介绍一下人工智能"},
]

response = llm.invoke(messages)
print(response)
print("------------------")
print(response.content)
```

返回结果：

```python
content='人工智能（AI）是通过计算机系统模拟人类智能的学科，涵盖机器学习、深度学习、自然语言处理、计算机视觉和机器人技术等领域。AI能够执行感知、学习、推理、决策等任务，广泛应用于医疗、金融、交通、教育等行业。尽管AI带来了效率提升和创新，但也引发了隐私、安全、就业等伦理和社会问题。总体而言，AI正在深刻改变我们的生活和工作方式。' additional_kwargs={'refusal': None} response_metadata={'token_usage': {'completion_tokens': 267, 'prompt_tokens': 16, 'total_tokens': 283}, 'model_name': 'gpt-4o', 'system_fingerprint': None, 'finish_reason': 'stop', 'logprobs': None} id='run-cbc5112d-aed6-449b-82ed-4cdfb47d97e4-0' usage_metadata={'input_tokens': 16, 'output_tokens': 267, 'total_tokens': 283, 'input_token_details': {}, 'output_token_details': {}}
------------------
人工智能（AI）是通过计算机系统模拟人类智能的学科，涵盖机器学习、深度学习、自然语言处理、计算机视觉和机器人技术等领域。AI能够执行感知、学习、推理、决策等任务，广泛应用于医疗、金融、交通、教育等行业。尽管AI带来了效率提升和创新，但也引发了隐私、安全、就业等伦理和社会问题。总体而言，AI正在深刻改变我们的生活和工作方式。
```

在 LangChain 中，`invoke` 方法用于执行一个链（如 `LLMChain` 或其他链）的处理。它接收输入参数并将其传递给链中的各个组件（如提示模板和语言模型），最后返回处理结果。

具体而言，`invoke` 方法通常执行以下步骤：

1. **接收输入**：它接收一个字典或其他结构化数据作为输入，例如用户输入的文本。
2. **调用链中的模型**：将输入数据格式化为模型可以理解的格式，并传递给指定的语言模型（如 OpenAI 的 LLM）。
3. **返回结果**：获取模型的输出，并可能进行解析（如将输出文本提取为字符串）。

除了 `invoke` 方法，还有其他一些常用的方法和操作来处理数据和与模型交互，包括：

1. **`call`**：与 `invoke` 类似，通常用于调用链中的模型，并处理输入和输出。
2. **`run`**：用于运行链，通常接受更复杂的输入，并返回结果。
3. **`stream`**：可以用来处理实时输出，适用于长文本生成任务。
4. **`predict`**：专门用于生成预测结果，通常用于分类或回归任务。
5. **`ainvoke`**：这是一个异步版本的 `invoke` 方法，适用于需要非阻塞调用的场景。它允许你在等待结果的同时执行其他操作。
6. **`astream`**：用于处理实时或流式输出的场景。它可以逐步获取模型生成的输出，适合需要实时反馈的应用程序，如聊天机器人或在线生成内容。
7. **`arun`**：这是异步版本的 `run` 方法，适合需要非阻塞执行的场景。它允许你在处理大规模输入或等待模型响应时继续进行其他操作。
8. **`acall`**：这是异步版本的 `call` 方法，通常用于在异步上下文中调用链。它使得处理请求时能够更灵活地管理异步任务。

## 4.2 使用 LLMChain 进行优化

在 LangChain 中，**Chain** 是一个核心概念，表示一系列相互连接的组件或操作。这些组件可以包括模型、提示模板、输出解析器等，形成一个处理流程。Chain 允许将多个步骤串联在一起，以实现复杂的任务，如自然语言生成、数据处理或逻辑推理。用户可以自定义和组合这些链，以满足特定需求，从而构建更为灵活和强大的应用程序。

**LLMChain** 是 LangChain 中的一个基础组件，专门用于将大语言模型（LLM）与提示模板结合起来。它的主要功能是创建一个处理链，允许用户定义输入、处理逻辑和输出格式。LLMChain 将用户的输入通过提示模板传递给 LLM，生成的响应可以进一步解析或处理。这种结构化的链式设计使得构建复杂的自然语言处理应用变得更加简单和高效。

还有一些其他的 Chain，例如：

- **SequentialChain**：顺序执行多个链，将前一个链的输出传递给下一个链。
- **ConversationalChain**：管理对话状态和上下文，适合构建对话系统。
- **MapChain**：并行处理多个输入，通过映射生成输出。
- **ReduceChain**：将多个输出合并为单个结果。
- **RouterChain**：根据输入条件选择不同的子链，灵活处理多条路径。

下面是一个使用 **LLMChain** 的例子：

```python
from langchain_openai import ChatOpenAI  # 导入 ChatOpenAI 类，用于与 OpenAI API 交互
from langchain_core.prompts import ChatPromptTemplate  # 导入 ChatPromptTemplate 类，用于创建聊天提示模板
from langchain.chains.llm import LLMChain  # 导入 LLMChain 类，用于创建语言模型链
from langchain_core.output_parsers import StrOutputParser  # 导入 StrOutputParser 类，用于解析输出

llm = ChatOpenAI(model="gpt-4o")

# 创建聊天提示模板，定义消息格式
template = ChatPromptTemplate.from_messages(
    [
        ("human", "{text}")  # 定义人类消息的格式
    ]
)

# 创建 LLMChain 实例，将提示模板和语言模型连接起来
chain = LLMChain(llm=llm, prompt=template)

# 调用链，传入文本进行处理
chain.invoke({"text": "简单介绍一下人工智能"})
```

输出：

```python
{'text': '人工智能（AI）是通过计算机系统模拟人类智能的学科，涵盖机器学习、深度学习、自然语言处理、计算机视觉和机器人技术等领域。AI能够执行感知、学习、推理、决策等任务，广泛应用于医疗、金融、交通、教育等行业。尽管AI带来了效率提升和创新，但也引发了隐私、安全、就业等伦理和社会问题。总体而言，AI正在深刻改变我们的生活和工作方式。'}
```

### 4.3 LCEL 表达式

**LCEL**（LangChain Expression Language）是一种表达方式，用于在 LangChain 中构建和组合链。通过使用 LCEL，用户可以以简洁的方式定义多个组件的连接，包括模型、提示、解析器等。LCEL 允许用户以管道形式组织这些组件，使得处理流程更加直观和灵活。这种方法有助于简化链的构建，并提高代码的可读性和维护性。

这里我们使用 LCEL 对 Chain 的定义进行优化：

```python
from langchain_openai import ChatOpenAI  # 导入 ChatOpenAI 类，用于与 OpenAI API 交互
from langchain_core.prompts import ChatPromptTemplate  # 导入 ChatPromptTemplate 类，用于创建聊天提示模板
from langchain_core.output_parsers import StrOutputParser  # 导入 StrOutputParser 类，用于解析输出

llm = ChatOpenAI(model="gpt-4o")

# 创建聊天提示模板，定义消息格式
template = ChatPromptTemplate.from_messages(
    [
        ("human", "{text}")  # 定义人类消息的格式
    ]
)

# 创建链，将提示模板、模型和输出解析器连接起来
chain = template | llm | StrOutputParser()

# 调用链，传入文本进行处理
chain.invoke({"text": "简单介绍一下人工智能"})
```

输出：

```python
'人工智能（AI）是通过计算机系统模拟人类智能的学科，涵盖机器学习、深度学习、自然语言处理、计算机视觉和机器人技术等领域。AI能够执行感知、学习、推理、决策等任务，广泛应用于医疗、金融、交通、教育等行业。尽管AI带来了效率提升和创新，但也引发了隐私、安全、就业等伦理和社会问题。总体而言，AI正在深刻改变我们的生活和工作方式。'
```

在 LangChain 中，**OutputParser** 是用于解析模型输出的组件。它负责将生成的结果转换为适合后续处理或使用的格式。不同的 OutputParser 可以根据需要进行定制，适用于特定类型的输出解析，如字符串解析、JSON 解析等。通过使用 OutputParser，用户可以更灵活地处理和利用模型的输出，提高整体应用的可用性和准确性。

主要的 **OutputParser** 及其功能包括：

1. **StrOutputParser**：将模型输出解析为字符串，适用于简单文本输出。
2. **JsonOutputParser**：将输出解析为 JSON 格式，适合需要结构化数据的场景。
3. **CompletionsOutputParser**：专门用于解析语言模型的完成结果，提供更丰富的输出处理功能。
4. **RegexOutputParser**：使用正则表达式解析输出，适合从文本中提取特定信息。
5. **PydanticOutputParser**：将输出解析为 Pydantic 模型，适合需要数据验证和结构化的应用。
6. ……

更多的大家可以查看：https://python.langchain.com/docs/concepts/#output-parsers

## 总结

在我们的文章中，虽然涵盖了 LangChain 的基础知识和核心组件，但仍有一些重要主题未涉及，包括：

1. **Agent**：如何使用智能代理与外部环境互动。
2. **Memory**：链的状态管理和记忆机制。
3. **Tools**：集成和使用外部工具的能力。
4. **扩展性**：如何自定义链和组件以适应特定需求。
5. **性能优化**：提高链性能和响应速度的方法。
6. 等等

这些我们将在后面的章节结合实例进行说明。我们讨论了 Chain 的概念，列举了如 LLMChain、SequentialChain 和 RouterChain 等多种链的类型。此外，介绍了 OutputParser 的主要类型及其功能，最后强调了 LCEL 的重要性。这些内容为使用 LangChain 进行大语言模型应用开发提供了全面的基础，旨在帮助读者更好地理解和应用该框架。
