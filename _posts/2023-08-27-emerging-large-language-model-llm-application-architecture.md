---
layout: post
title: 【翻译】新兴的大型语言模型 （LLM） 应用程序体系结构
categories: [LLM, NLP, 机器学习, AI]
description: 由于大型语言模型（LLM）的高度非结构化性质，关于如何实现LLMs，思想和市场正在发生变化。
keywords: LLM, NLP, 机器学习, AI
mermaid: false
sequence: false
flow: false
mathjax: false
mindmap: false
mindmap2: false
---

原文：[Emerging Large Language Models (LLM) Application Architecture](https://www.ihttps://cobusgreyling.medium.com/emerging-large-language-model-llm-application-architecture-cba0e7862037)

作者：[Cobus Greyling](https://cobusgreyling.medium.com/)

![Alt text](/images/posts/2023-08-27-emerging-large-language-model-llm-application-architecture/image.png)

Due to the highly unstructured nature of Large Language Models (LLMs), there are thought and market shifts taking place on how to implement LLMs.

由于大型语言模型（LLM）的高度非结构化性质，关于如何实现LLMs，思想和市场正在发生变化。


I’m currently the Chief Evangelist @ HumanFirst. I explore & write about all things at the intersection of AI & language; ranging from LLMs, Chatbots, Voicebots, Development Frameworks, Data-Centric latent spaces & more.

我目前是首席布道者@HumanFirst。我探索和写作人工智能和语言交叉点的所有事物;范围从LLM，聊天机器人，
语音机器人，开发框架，以数据为中心的潜在空间等等。

Why do I say LLMs are unstructured? LLMs are to a large extent an extension of Conversational AI.

为什么我说LLM是非结构化的？LLM在很大程度上是对话式AI的扩展。

Due to the unstructured nature of human language, the input to LLMs are conversational and unstructured, in the form of Prompt Engineering.

由于人类语言的非结构化性质，LLM的输入是会话和非结构化的，以提示工程的形式。

And the output of LLMs is also conversational and unstructured; a highly succinct form of natural language generation (NLG).

LLM的输出也是对话和非结构化的;一种高度简洁的自然语言生成 （NLG） 形式。

LLMs introduced functionality to fine-tune and create custom models. And an initial approach to customising LLMs was creating custom models via fine-tuning.

LLM引入了微调和创建自定义模型的功能。定制LLM的最初方法是通过微调创建自定义模型。

This approach has fallen into disfavour for three reasons:

由于三个原因，这种方法不受欢迎：

As LLMs have both a generative and predictive side. The generative power of LLMs is easier to leverage than the predictive power. If the generative side of LLMs are presented with contextual, concise and relevant data at inference-time, hallucination is negated.

由于LLM既有生成性的一面，也有预测性的一面。LLM的生成能力比预测能力更容易利用。如果在推理时向LLM的生成方面提供上下文，简洁和相关的数据，则幻觉被否定。

Fine-tuning LLMs involves training data curation, transformation and cost. Fine-tuned models are frozen with a definite time-stamp and will still demand innovation around prompt creation and data presentation to the LLM.

微调LLM涉及训练数据管理，转换和成本。微调的模型被冻结在明确的时间戳上，并且仍然需要围绕提示创建和向LLM呈现数据进行创新。

When classifying text based on pre-defined classes or intents, NLU still has an advantage with built-in efficiencies.

在根据预定义的类或意图对文本进行分类时，NLU 仍然具有内置效率的优势。

The aim of fine-tuning of LLMs is to engender more accurate and succinct reasoning and answers. This also solves for one of the big problems with LLMs; hallucination, where the LLM returns highly plausible but incorrect answers.

微调LLM的目的是产生更准确，更简洁的推理和答案。这也解决了LLM的一个大问题;幻觉，LLM返回非常合理但不正确的答案。

The proven solution to hallucination is using highly relevant and contextual prompts at inference-time, and asking the LLM to follow chain-of-thought reasoning.

经过验证的幻觉解决方案是在推理时使用高度相关和上下文提示，并要求LLM遵循思维链推理。

As seen below, there has been an emergence of vector stores / databases with semantic search, to provide the LLM with a contextual and relevant data snippet to reference.

如下所示，出现了具有语义搜索的向量存储/数据库，为LLM提供上下文和相关的数据片段以供参考。

Vector Stores, Prompt Pipelines and/or Embeddings are used to constitute a few-shot prompt. The prompt is few-shot because context and examples are included in the prompt.

向量存储、提示管道和/或嵌入用于构成几个镜头提示。提示是少数镜头，因为提示中包含上下文和示例。

In the case of Autonomous Agents, other tools can also be included like Python Math Libraries, Search and more. The generated response is presented to the user, and also used as context for follow-up or next-step queries or dialog turns.

对于自治代理，还可以包含其他工具，例如Python Math Libraries，Search等。生成的响应将呈现给用户，并用作后续或下一步查询或对话周转的上下文。

![Alt text](images/posts/2023-08-27-emerging-large-language-model-llm-application-architecture/image.png)

The process of creating contextually relevant prompts are further aided by Autonomous Agents, prompt pipelines where a prompt is engineered in real-time based on relevant available data, conversation context and more.

创建上下文相关提示的过程得到了自治代理的进一步帮助，提示管道根据相关的可用数据、对话上下文等实时设计提示。

Prompt chaining is a more manual and sequential process of creating a flow within a visual designer UI which is fixed and sequential and lacks the autonomy of Agents. There are advantages and disadvantages to both approaches; and both can be used in concert.

提示链接是在可视化设计器 UI 中创建流的更手动和顺序的过程，该流程是固定和顺序的，缺乏代理的自治性。这两种方法都有优点和缺点;两者都可以协同使用。

Lastly, an emerging field is testing different LLMs against a prompt; as opposed to in the past where we would focus on only testing various prompts against one single LLM. These tools include LangSmith, ChainForge and others.

最后，一个新兴领域正在根据提示测试不同的LLM;与过去相反，我们将专注于仅针对一个LLM测试各种提示。这些工具包括LangSmith，ChainForge等。

The importance of determining the best suited model for a specific prompt addresses the notion that within enterprise implementations, multiple LLMs will be used.

为特定提示确定最适合的模型的重要性解决了在企业实现中将使用多个LLM的概念。