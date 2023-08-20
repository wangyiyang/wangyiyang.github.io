---
layout: post
title: 【翻译】LangChain入门：创建LLM驱动应用程序的初学者指南
categories: [LLM, LangChain, Translation]
description: A LangChain tutorial to build anything with large language models in Python
keywords: LLM, LangChain
mermaid: false
sequence: false
flow: false
mathjax: false
mindmap: false
mindmap2: false
---

原文地址：[Getting Started with LangChain: A Beginner’s Guide to Building LLM-Powered Applications](https://medium.com/towards-data-science/getting-started-with-langchain-a-beginners-guide-to-building-llm-powered-applications-95fc8898732c)



一个LangChain教程，用Python构建任何具有大型语言模型的东西

![Alt text](/images/posts/2023-8-20-getting-started-with-langchain-a-beginners-guide-to-building-llm-powered-applications/image.png)

*“随机鹦鹉对另一只说了什么？“（图片由作者绘制）*


自ChatGPT发布以来，大型语言模型（LLM）已经获得了很大的普及。虽然你可能没有足够的资金和计算资源在地下室从头开始训练LLM，但你仍然可以使用预先训练的LLM来构建一些很酷的东西，例如：

- 个人助理，可以根据您的数据与外部世界进行交互
- 为您的目的定制的聊天机器人
- 分析或总结您的文档或代码

## LLM正在改变我们构建AI驱动产品的方式

随着它们奇怪的API和提示工程，LLM正在改变我们构建AI驱动产品的方式。这就是为什么在“LLMOps”这个术语下，到处都有新的开发者工具出现。

其中一个新工具是[LangChain](https://github.com/hwchase17/langchain)。

## 什么是LangChain？

LangChain是一个框架，它可以通过为您提供以下内容来帮助您更轻松地构建LLM驱动的应用程序：


- 一种通用的接口，用于各种不同的基础模型（见[模型](https://medium.com/towards-data-science/getting-started-with-langchain-a-beginners-guide-to-building-llm-powered-applications-95fc8898732c#bd03)），
- 一个框架，可以帮助您管理您的提示（见[提示](https://medium.com/towards-data-science/getting-started-with-langchain-a-beginners-guide-to-building-llm-powered-applications-95fc8898732c#b1a5)），以及
- 一个中央接口，用于长期记忆（见[记忆](https://medium.com/towards-data-science/getting-started-with-langchain-a-beginners-guide-to-building-llm-powered-applications-95fc8898732c#3bc6)）、外部数据（见[索引](https://medium.com/towards-data-science/getting-started-with-langchain-a-beginners-guide-to-building-llm-powered-applications-95fc8898732c#806f)）、其他LLM（见[链](https://medium.com/towards-data-science/getting-started-with-langchain-a-beginners-guide-to-building-llm-powered-applications-95fc8898732c#fcac)）和其他代理，用于LLM无法处理的任务（例如计算或搜索）（见[代理](https://medium.com/towards-data-science/getting-started-with-langchain-a-beginners-guide-to-building-llm-powered-applications-95fc8898732c#b842)）。

它是由[Harrison Chase](https://twitter.com/hwchase17)创建的开源项目（[GitHub存储库](https://github.com/hwchase17/langchain)）。

因为LangChain有很多不同的功能，所以一开始理解它的功能可能很有挑战性。这就是为什么我们将在本文中介绍LangChain的（当前）六个关键模块，给予您更好地了解其功能。

### 先决条件

要沿着本教程，您需要安装 `langchain` Python包，并准备好所有相关的API密钥。

### 安装LangChain

在安装 `langchain` 包之前，请确保您的Python版本≥ 3.8.1且<4.0。

要安装 `langchain` Python包，您可以 pip 安装它

```bash
pip install langchain
```

在本教程中，我们使用的是0.0.147版本。GitHub仓库非常活跃;因此，请确保您有一个最新版本。

完成安装后，导入 `langchain` Python包。

```python
import langchain
```

### 准备API密钥

使用LLM构建应用程序需要API密钥用于您想要使用的某些服务，并且某些API具有相关的成本。

**LLM提供程序（必填）** -您首先需要一个您想要使用的LLM提供程序的API密钥。我们目前正在经历“人工智能的Linux时刻”，开发人员必须在性能和成本之间进行权衡的基础模型之间进行选择。

![Alt text](/images/posts/2023-8-20-getting-started-with-langchain-a-beginners-guide-to-building-llm-powered-applications/image1.png)

*LLM提供商：专有和开源基础模型（图片由作者提供，灵感来自Fiddler.ai，首次发表在W&B的博客上）*


**专有模型** 是由拥有大型专家团队和大量人工智能预算的公司拥有的闭源基础模型。它们通常比开源模型更大，因此性能更好，但它们也有昂贵的API。专有模型提供商的例子有OpenAI、co：here、AI21 Labs或Anthropic。

大多数可用的LangChain教程都使用OpenAI，但请注意，OpenAI API（对于实验来说并不昂贵，但它）不是免费的。要获得OpenAI API Key，您需要一个OpenAI帐户，然后在API keys下“Create new secret key”。

```python
import os
os.environ["OPENAI_API_KEY"] = ... # insert your API_TOKEN here
```

**开源模型** 通常比专有模型更小，功能更低，但它们比专有模型更具成本效益。开放源代码模型的例子有：

- [BLOOM](https://huggingface.co/bigscience/bloom) by BigScience
- [LLaMA](https://huggingface.co/docs/transformers/main/en/model_doc/llama) by Meta AI
- [Flan-T5](https://huggingface.co/google/flan-t5-xl) by Google  Google Flan-T5
- [GPT-J](https://huggingface.co/EleutherAI/gpt-j-6b) by Eleuther AI

许多开源模型被组织和托管在[Hugging Face](https://huggingface.co/)上作为社区中心。要获得Hugging Face API Key，您需要一个Hugging Face账户，并在[Access Tokens](https://huggingface.co/settings/tokens)下创建一个“New token”。

```python
import os

os.environ["HUGGINGFACEHUB_API_TOKEN"] = ... # insert your API_TOKEN here
```

您可以免费使用Hugging Face用于开源LLM，但仅限于性能较低的较小LLM。


    **我的个人笔记** -让我们在这里诚实一点：当然，您可以在这里尝试开源基础模型。我试图使本教程只使用托管在Hugging Face上的开源模型，这些模型可以通过普通帐户（google/flan-t5-xl和sentence-transformers/all-MiniLM-L 6-v2）使用。它对大多数例子都有效，但让一些例子起作用也是一种痛苦。最后，我扣动了扳机，为OpenAI设置了一个付费账户，因为LangChain的大多数示例似乎都针对OpenAI的API进行了优化。总的来说，为这个教程运行了几个实验花费了我大约1美元。

**矢量数据库（可选）** -如果您想使用特定的矢量数据库，如Pinecone，Weaviate或Milvus，您需要向他们注册以获得API密钥并查看其定价。在本教程中，我们使用Faiss，它不需要注册。

**工具（可选）** -根据您希望LLM与之交互的工具（如OpenWeatherMap或SerpAPI），您可能需要向它们注册以获取API密钥并查看其定价。在本教程中，我们只使用不需要API密钥的工具。

## 你可以用LangChain做什么？

该软件包为许多基础模型提供了通用接口，支持提示管理，并作为其他组件的中央接口，如提示模板、其他LLM、外部数据和其他通过代理的工具。

在撰写本文时，LangChain（版本0.0.147）涵盖了六个模块：

- Models: Choosing from different LLMs and embedding models
- Prompts: Managing LLM inputs
- Chains: Combining LLMs with other components
- Indexes: Accessing external data
- Memory: Remembering previous conversations
- Agents: Accessing other tools


以下部分中的代码示例是从[LangChain文档](https://python.langchain.com/en/latest/index.html)中复制和修改的。

### Models: Choosing from different LLMs and embedding models

目前，许多不同的LLM正在出现。LangChain为各种型号提供集成，并为所有型号提供简化的界面。

LangChain区分了三种类型的模型，它们的输入和输出不同：

- LLM将字符串作为输入（提示）并输出字符串（完成）。

```python
# Proprietary LLM from e.g. OpenAI
# pip install openai
from langchain.llms import OpenAI
llm = OpenAI(model_name="text-davinci-003")

# Alternatively, open-source LLM hosted on Hugging Face
# pip install huggingface_hub
from langchain import HuggingFaceHub
llm = HuggingFaceHub(repo_id = "google/flan-t5-xl")

# The LLM takes a prompt as an input and outputs a completion
prompt = "Alice has a parrot. What animal is Alice's pet?"
completion = llm(prompt)

```

![Alt text](/images/posts/2023-8-20-getting-started-with-langchain-a-beginners-guide-to-building-llm-powered-applications/image2.png)

*LLM模型（作者图片）*

- **聊天模型**类似于LLM。他们将聊天消息列表作为输入并返回聊天消息。
- **文本嵌入模型**接受文本输入并返回浮点数（嵌入）列表，浮点数是输入文本的数值表示。嵌入有助于从文本中提取信息。该信息随后可以被使用，例如，用于计算文本之间的相似性（例如，电影摘要）。


```python
# Proprietary text embedding model from e.g. OpenAI
# pip install tiktoken
from langchain.embeddings import OpenAIEmbeddings
embeddings = OpenAIEmbeddings()

# Alternatively, open-source text embedding model hosted on Hugging Face
# pip install sentence_transformers
from langchain.embeddings import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name = "sentence-transformers/all-MiniLM-L6-v2")

# The embeddings model takes a text as an input and outputs a list of floats
text = "Alice has a parrot. What animal is Alice's pet?"
text_embedding = embeddings.embed_query(text)
```

![Alt text](/images/posts/2023-8-20-getting-started-with-langchain-a-beginners-guide-to-building-llm-powered-applications/image3.png)

*文本嵌入模型（作者图片）*

### Prompts: Managing LLM inputs

LLM有奇怪的API。虽然用自然语言向LLM输入提示应该感觉很直观，但在从LLM获得所需的输出之前，需要对提示进行相当多的调整。这个过程被称为即时工程。

一旦你有了一个好的提示，你可能想把它用作模板用于其他目的。因此，LangChain为您提供了所谓的 `PromptTemplates` ，它可以帮助您从多个组件构造提示符。

```python
from langchain import PromptTemplate

template = "What is a good name for a company that makes {product}?"

prompt = PromptTemplate(
    input_variables=["product"],
    template=template,
)

prompt.format(product="colorful socks")
```

上面的提示可以被看作是一个零问题设置，你希望LLM在足够的相关数据上进行训练，以提供令人满意的响应。

改进LLM输出的另一个技巧是在提示符中添加几个示例，使其成为一个很少的问题设置。

```python
from langchain import PromptTemplate, FewShotPromptTemplate

examples = [
    {"word": "happy", "antonym": "sad"},
    {"word": "tall", "antonym": "short"},
]

example_template = """
Word: {word}
Antonym: {antonym}\n
"""

example_prompt = PromptTemplate(
    input_variables=["word", "antonym"],
    template=example_template,
)

few_shot_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix="Give the antonym of every input",
    suffix="Word: {input}\nAntonym:",
    input_variables=["input"],
    example_separator="\n",
)

few_shot_prompt.format(input="big")
```

上面的代码将生成一个提示模板，并根据提供的示例和输入组成如下提示：


```text
Give the antonym of every input

Word: happy
Antonym: sad



Word: tall
Antonym: short


Word: big
Antonym:
```

### Chains: Combining LLMs with other components

LangChain中的链接简单地描述了将LLM与其他组件组合以创建应用程序的过程。一些例子是：

- Combining LLMs with prompt templates (see this section)
- Combining multiple LLMs sequentially by taking the first LLM’s output as the input for the second LLM (see this section)
- Combining LLMs with external data, e.g., for question answering (see Indexes)
- Combining LLMs with long-term memory, e.g., for chat history (see Memory)


在上一节中，我们创建了一个提示模板。当我们想在LLM中使用它时，我们可以使用 LLMChain ，如下所示：
    
```python

from langchain import LLMChain

from langchain.chains import LLMChain

chain = LLMChain(llm = llm, 
                  prompt = prompt)

# Run the chain only specifying the input variable.
chain.run("colorful socks")
```

如果我们想使用第一个LLM的输出作为第二个LLM的输入，我们可以使用 `SimpleSequentialChain` ：

```python
from langchain.chains import LLMChain, SimpleSequentialChain

# Define the first chain as in the previous code example
# ...

# Create a second chain with a prompt template and an LLM
second_prompt = PromptTemplate(
    input_variables=["company_name"],
    template="Write a catchphrase for the following company: {company_name}",
)

chain_two = LLMChain(llm=llm, prompt=second_prompt)

# Combine the first and the second chain 
overall_chain = SimpleSequentialChain(chains=[chain, chain_two], verbose=True)

# Run the chain specifying only the input variable for the first chain.
catchphrase = overall_chain.run("colorful socks")
```

![Alt text](/images/posts/2023-8-20-getting-started-with-langchain-a-beginners-guide-to-building-llm-powered-applications/image4.png)

*使用LangChain中的PromptTemplates和LLM输出SimpleSequentialChain（作者截图）*

### Indexes: Accessing external data

LLM的一个限制是它们缺乏上下文信息（例如，访问某些特定文件或电子邮件）。您可以通过让LLM访问特定外部数据来解决这个问题。

为此，您首先需要使用文档加载器加载外部数据。LangChain为不同类型的文档提供了各种加载器，从PDF和电子邮件到网站和YouTube视频。

让我们从YouTube视频加载一些外部数据。如果你想加载一个大的文本文档并使用文本拆分器拆分它，可以参考官方文档。

```python
# pip install youtube-transcript-api
# pip install pytube

from langchain.document_loaders import YoutubeLoader

loader = YoutubeLoader.from_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    
documents = loader.load()
```

现在，您已经准备好了作为 documents 运行的外部数据，您可以在向量数据库-VectorStore中使用文本嵌入模型（参见模型）对它进行索引。流行的媒介数据库包括松果、Weaviate和Milvus。在本文中，我们使用Faiss是因为它不需要API密钥。

```python
# pip install faiss-cpu
from langchain.vectorstores import FAISS

# create the vectorestore to use as the index
db = FAISS.from_documents(documents, embeddings)
```

您的文档（在本例中是视频）现在作为嵌入存储在向量存储中。

现在，您可以使用这些外部数据做各种事情。让我们用它来完成一个带有信息检索器的问答任务：

```python
from langchain.chains import RetrievalQA

retriever = db.as_retriever()

qa = RetrievalQA.from_chain_type(
    llm=llm, 
    chain_type="stuff", 
    retriever=retriever, 
    return_source_documents=True)

query = "What am I never going to do?"
result = qa({"query": query})

print(result['result'])
```

![Alt text](/images/posts/2023-8-20-getting-started-with-langchain-a-beginners-guide-to-building-llm-powered-applications/image5.png)

*RetrievalQA的输出（作者截图）*

等等-你刚刚被人碾压了吗？是的你说了

### Memory: Remembering previous conversations

对于像聊天机器人这样的应用程序，它们必须记住以前的对话。但默认情况下，LLM没有任何长期记忆，除非您输入聊天历史。

![Alt text](/images/posts/2023-8-20-getting-started-with-langchain-a-beginners-guide-to-building-llm-powered-applications/image6.png)

*有和没有对话记忆的聊天（图片由作者在ifaketextmessage.com上制作，灵感来自Pinecone）*

LangChain通过提供几种处理聊天历史记录的不同选项来解决这个问题：

- keep all conversations, 
- keep the latest k conversations,
- summarize the conversation.

在这个例子中，我们将使用 `ConversationChain` 来给予这个应用程序会话内存。

```python
from langchain import ConversationChain

conversation = ConversationChain(llm=llm, verbose=True)

conversation.predict(input="Alice has a parrot.")

conversation.predict(input="Bob has two cats.")

conversation.predict(input="How many pets do Alice and Bob have?")
```

这将导致上图中的右手对话。如果没有 `ConversationChain` 来保持对话记忆，对话将看起来像上图左侧的对话。

## Agents: Accessing other tools

尽管LLM非常强大，但也有一些局限性：它们缺乏上下文信息（例如，对训练数据中不包含的特定知识的访问），它们可能很快变得过时（例如，GPT-4是在2021年9月之前根据数据进行训练的），他们的数学很差。

![Alt text](/images/posts/2023-8-20-getting-started-with-langchain-a-beginners-guide-to-building-llm-powered-applications/image7.png)

*法学硕士数学不好*

由于LLM可能会对他们自己无法完成的任务产生幻觉，因此我们需要给予他们访问辅助工具，如搜索（例如，Google搜索）、计算器（例如，Python REPL或Wolfram Alpha）和查找（例如，Wikipedia）。

此外，我们还需要代理人根据LLM的输出来决定使用哪些工具来完成任务。

请注意，一些LLM（如 [google/flan-t5-xl](https://github.com/hwchase17/langchain/issues/1358) ）不适合以下示例，因为它们不遵循 [conversational-react-description](https://github.com/hwchase17/langchain/issues/1358) 模板。对我来说，这就是我在OpenAI上建立一个付费账户并切换到OpenAI API的地方。

下面是一个例子，代理首先在维基百科上查找巴拉克·奥巴马的出生日期，然后用计算器计算出他在2022年的年龄。

```python
# pip install wikipedia
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType

tools = load_tools(["wikipedia", "llm-math"], llm=llm)
agent = initialize_agent(tools, 
                         llm, 
                         agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, 
                         verbose=True)


agent.run("When was Barack Obama born? How old was he in 2022?")
```

![Alt text](/images/posts/2023-8-20-getting-started-with-langchain-a-beginners-guide-to-building-llm-powered-applications/image8.png)

*LLM代理的输出（作者截图）*

## Summary

就在几个月前，我们所有人（或者至少我们中的大多数人）都对ChatGPT的功能印象深刻。现在，像LangChain这样的新开发工具使我们能够在几个小时内在笔记本电脑上构建出同样令人印象深刻的原型-这是一些真正令人兴奋的时刻！


LangChain是一个开源的Python库，它使任何可以编写代码的人都可以构建LLM驱动的应用程序。该软件包为许多基础模型提供了一个通用接口，支持提示管理，并充当其他组件（如提示模板，其他LLM，外部数据和其他工具）的中央接口-在撰写本文时。


该库提供了比本文中提到的更多的特性。以目前的发展速度，这篇文章也可能在一个月内过时。


在撰写本文时，我注意到库和文档都围绕OpenAI的API展开。虽然很多例子都使用开源基础模型 [google/flan-t5-xl](https://github.com/hwchase17/langchain/issues/1358) ，但我在中间切换到了OpenAI API。尽管不是免费的，但在本文中尝试OpenAI API只花费了我大约1美元。

## References
[1] Harrison Chase (2023). LangChain documentation (accessed April 23rd, 2023)