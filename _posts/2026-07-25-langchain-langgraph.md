---
layout: post
title: "很多人还是分不清 LangChain 和 LangGraph"
categories: [LangChain, AI Agent]
description: "很多人还是分不清 LangChain 和 LangGraph"
keywords: LangChain, AI Agent
mermaid: false
sequence: false
flow: false
mathjax: false
mindmap: false
mindmap2: false
---

![很多人还是分不清 LangChain 和 LangGraph](https://www.wangyiyang.cc/images/posts/2026-07-25-langchain-langgraph/01.png)
前几天又看到有人问：「都 2026 年了，入门该学 LangChain 还是 LangGraph？听说前者已经过时了。」
这个问题我从 2024 年看到现在。
也不能全怪提问的人。官方的说法确实变过。2024 年 1 月 LangGraph 发布时，博客里的原话是「LangGraph is built on top of LangChain」；到 2025 年 10 月两个项目同时发布 1.0，定位成了「LangChain agents are built on LangGraph」。名字没变，上下层关系却在一年半里掉了个头。
我想把这段历史理顺，再给出一套现在能直接用的选型方法。
## 一、1.0 之前，边界为什么这么模糊
2022 年 10 月，LangChain 刚出现时，解决的是一个很具体的问题：不用每个人都重写模型调用和字符串拼接。`LLMChain`、`SequentialChain` 把 prompt、模型和解析器接成固定流水线，开箱就能跑。
2023 年，预制链逐渐显得太僵，官方推出 LangChain Expression Language（LCEL）。开发者可以用 `|` 把组件接成 `RunnableSequence`，也能做流式和批量处理。不过它仍然擅长线性或 DAG 控制流：数据从左往右走，很少回头。跨调用状态也不是原生能力，`RunnableWithMessageHistory` 更像后来补上的一块。
Agent 把问题暴露了出来。它不是单向流水线，而是一个循环：模型选择动作，工具执行，模型观察结果，再决定下一步。当时的 `AgentExecutor` 把循环包在黑盒里。想替换其中一步，或者增加持久化、人工介入和回退重试，都不轻松。线性管道很难承接这种需求。
2024 年 1 月，LangGraph 随 LangChain v0.1 发布，目标就是处理带状态的循环图。`StateGraph` 用节点和边描述应用，`add_conditional_edges` 允许流程往回跳。当时它确实是 LangChain 上层的扩展库：`langgraph` 依赖 `langchain-core`，工具使用 `BaseTool`，消息使用 `BaseMessage`，模型也走 LangChain 的聊天模型接口。LangChain 提供组件，LangGraph 增加执行引擎。
真正让人困惑的是 2024 年 5 月。LangChain 0.2 将 `initialize_agent`、`AgentExecutor` 标为 deprecated，并建议 Agent 用户转向 LangGraph。「LangGraph 是 LangChain 的升级版」也从那时流传开来。这个误解很容易理解：旧入口刚被弃用，官方紧接着让大家换另一个库。
接下来的几个月，LangGraph v0.1、LangGraph Cloud 和 LangGraph Studio 陆续发布。两套文档频繁互相引用。我写《LangChain 大模型应用开发·入门总览》时，也专门用了一段解释它们的关系。
### 1.0 之前，Agent 代码换了三代
时间线有点抽象，代码更直观。同样是让模型调用工具，1.0 之前先后出现过三种主流写法。
第一代是 `initialize_agent` + `AgentType`。模型在 prompt 中输出 `Action: ...`，框架再解析字符串：
```python
from langchain.agents import initialize_agent, AgentType

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
)
agent.run("when was langchain made")
```
循环藏在 `agent.run()` 里面，开发者几乎碰不到。
第二代是 `create_tool_calling_agent` + `AgentExecutor`。模型原生支持 tool calling 后，调用变得更结构化，但 prompt 需要自己搭，`agent_scratchpad` 也是固定配置：
```python
from langchain.agents import AgentExecutor, create_tool_calling_agent

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])
agent = create_tool_calling_agent(model, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)
executor.invoke({"input": "what is magic_function(3)?"})
```
它比第一代可靠，但循环仍由 `AgentExecutor` 管着，局部改造依然麻烦。
第三代由 LangGraph 接管。简单场景可以使用 `langgraph.prebuilt.create_react_agent(model, tools)`，复杂场景则自己写状态图：
```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)   # 模型决策
workflow.add_node("tools", tools_node)   # 执行工具
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
workflow.add_edge("tools", "agent")      # 回到模型节点，形成循环

app = workflow.compile()
```
变化就在这几行代码里：原本藏在执行器里的循环，被拆成了可以查看和修改的图。1.0 的 `create_agent` 又把这张图封装起来，但保留了中间件入口，底层仍使用 LangGraph 运行时。
## 二、1.0 之后，分层终于稳定
2025 年 10 月，`langchain` 和 `langgraph` 同时发布 1.0。此前模糊的边界基本定了下来。
LangGraph 1.0 成为底层运行时。图原语和执行模型保持稳定，durable execution、checkpointer 持久化、human-in-the-loop 仍是一等能力。它不再只是 LangChain 上面的扩展，而是整个 Agent 栈的执行底座。
LangChain 1.0 则收缩了包的表面积。旧链和 `AgentExecutor` 被移入 `langchain-classic`，新的核心入口是：
```python
from langchain.agents import create_agent

agent = create_agent(
    model="claude-sonnet-4-6",
    tools=[search_web, analyze_data],
    system_prompt="You are a research assistant.",
)
```
`create_agent` 取代了 `langgraph.prebuilt.create_react_agent`，内部生成 LangGraph 的 `CompiledStateGraph`。所以，用 LangChain 写出的 Agent 实际运行在 LangGraph 上，streaming、持久化和 HITL 中断都来自这层运行时。
需要定制时，也不必再改执行器黑盒。`before_model`、`wrap_model_call`、`wrap_tool_call`、`after_agent` 等中间件钩子可以插入执行过程。
两者现在的分工如下：
<table header-row="true">
<tr>
<td>维度</td>
<td>LangChain（高层框架）</td>
<td>LangGraph（底层运行时）</td>
</tr>
<tr>
<td>定位</td>
<td>有明确默认方案的 Agent 框架</td>
<td>低层编排运行时</td>
</tr>
<tr>
<td>控制流</td>
<td>标准 Agent 循环 + 中间件钩子</td>
<td>`StateGraph` 自定义循环状态图（Pregel 超步模型）</td>
</tr>
<tr>
<td>状态</td>
<td>复用底层能力，开箱即用</td>
<td>原生 channel + checkpointer，可精细控制</td>
</tr>
<tr>
<td>上手成本</td>
<td>几行代码即可启动</td>
<td>需要理解图、节点、边和状态规约</td>
</tr>
<tr>
<td>能力来源</td>
<td>运行在 LangGraph 上</td>
<td>提供执行能力</td>
</tr>
</table>
它们不是互相替代的两个框架，而是同一套技术栈的两层。LangChain 给出默认做法，LangGraph 允许开发者接管控制流。
## 三、现在怎么选
我的判断标准很简单：当前需求能不能被「模型调用工具的标准循环」覆盖。能，就留在 LangChain；不能，再下沉到 LangGraph。
![](https://www.wangyiyang.cc/images/posts/2026-07-25-langchain-langgraph/02.png)
如果根本不是 Agent，比如单次问答、批量翻译或固定流程的数据处理，LCEL 已经够用。有些任务直接调用模型 SDK 反而更省事。没必要为了使用 Agent 而增加一层抽象。
大多数 Agent 业务都属于标准循环。先用 `create_agent`，遇到定制需求再加中间件。我不建议一开始就手写图，因为每多一分控制权，也会多一分开发和维护成本。
当流程包含自定义拓扑、多智能体协同、回退纠错或复杂状态机时，标准循环就装不下了。这时再用 LangGraph 手写 `StateGraph`，理由会更充分。
旧项目不用立刻重写。`langchain-classic` 可以先兜底，但它只维护关键 bug，迁移到 `create_agent` 应该放进计划里。
还有一点很实用：`create_agent` 的产物本身就是一张编译图，可以作为节点嵌入自定义 LangGraph 工作流。项目完全可以从高层起步，复杂以后再下沉，不必推倒重来。