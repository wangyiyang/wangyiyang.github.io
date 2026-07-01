---
title: "从零构建多代理系统：我学到的那些课"
date: 2026-05-14 09:00:00 +0800
categories: [AI, Agent, 工程实践]
tags: [Multi-Agent, Shopify, Claude, SwarmSDK, MCP]
permalink: /2026/05/14/multi-agent-system-lessons/
description: "从一个 Hackday 项目出发，复盘多代理系统从零到一的全过程——架构选型、通信协调、错误处理的实战经验与教训。"
---

![cover](/images/posts/multi-agent-system-lessons_1200x630.jpg)

## 开篇：一个 Hackday 项目如何改变了我对 AI 的认知

2025 年 5 月的 Shopify Hackday，我尝试做一个 Ruby Gem MCP server，给 Claude Code 提供 AST 导航能力。第一次尝试失败了——Claude 不认识 Prism（Ruby 解析器），文档里也没有例子。

我试了一个"老派"方法：自己先读完 Prism 代码库，然后用 Claude Code 在代码库里学习，再把答案复制粘贴过来。

然后我问了自己一个问题：**如果我能把这个过程自动化呢？**

我把一个 Claude Code（放在 Prism 代码库里）和主 Claude Code（正在构建 library）通过 MCP 连接起来。结果：两个 agent 一次性完成了任何一个单独 agent 都做不到的事情。

**一个关键认知诞生了：两个 agent 协作，胜过任何一个单独 agent。**

这个经验最终催生了 Claude Swarm（GitHub 1.4k+ stars）和它的继任者 SwarmSDK。

---

## Shopify 的 AI 采用曲线：从怀疑到全员"氛围编程"

Shopify 的 AI 采用路径很有意思：

**2024 年之前**：与 OpenAI 签约，内部有聊天工具可用，但大量工程师因为早期 GPT-3.5 的糟糕体验而持怀疑态度。

**2024 年**：工具向所有人开放——LibreChat、VSCode Copilot、Cursor 等。但渗透率依然不高。

**2025 年 2 月转折点**：CEO Tobi 发了全员邮件，大意是"在我们雇人之前，先要能证明 AI 做不了这个工作"。这封邮件直接推动了全员 AI 采用。

**结果**：约 6000 名员工的 Shopify，现在连非工程师都在"氛围编程"（vibe coding）原型产品了。

---

## 从"All-in-One"提示词到多代理微服务架构

Shopify 团队观察到一个核心模式：

### ❌ 旧做法：一个 LLM + 巨大提示词

```
问题：无关 token 太多
     LLM 会迷路
     效果差
```

### ✅ 新做法：多个窄专型 agent

```
每个 agent 都是某个领域的专家
结果：效果显著提升
```

SwarmSDK 就是在这一认知下诞生的，核心特性包括：

- **多模型支持**：Claude、Gemini、o3 等
- **YAML / Ruby DSL 定义 agent**：声明式，易维护
- **工作流支持 + 树形结构**：复杂任务分解
- **事件钩子**：可观测性
- **内置成本追踪**：谁在花钱，花了多少
- **插件系统**：包括 memory 插件

---

## 那些让人头疼的问题

### 1. 碎片化危机

每个团队都在构建自己的 agent 系统，用不同的框架（LangChain 等），大量重复造轮子。

### 2. 规模化难题

Shopify 的 AI 团队变成了"AI 特警队"——所有人都有问题来求助。解决方案不是扩大 AI 团队，而是**构建赋能工具，让每个团队的 AI 爱好者自己具备构建能力**。

### 3. 非开发者上手难度

YAML 文件、CLI 命令对这些用户来说太复杂了。开发者自己也不想写 YAML 编程。多模型实现的代码当时是"一大坨 hack"，日志记录更是噩梦。

---

## Agent 微服务架构：一个解决碎片化的思路

当前状态（碎片化）：

```
各团队自己造 agent
      ↓
微服务地狱：
- 网络重试
- 可观测性挑战
- 链路追踪
- 大家只是想通信而已
```

**统一编排策略**：

- 所有人用同一种方式定义 agent
- 不需要 MCP/A2A 互相通话
- 导入定义，单进程运行
- **Ruby + Fibers**：对 I/O 密集的 LLM 工作完美契合（网络请求）

---

## 三个核心教训

### 教训一："最好的解决方案始于我自己的痛点"

先解决自己的问题。你的真实需求是最强的产品牵引力。

### 教训二："把 agent 当成窄专型工具/专家，而不是通才"

- 给 agent 写人物介绍/简介 = 浪费 token
- 除非你想控制 AI 的输出，否则不需要这些
- **用的 token 越少，效果越好**

### 教训三："不要建 AI 特警队，要建赋能工具"

赋能每个团队的 AI 爱好者——他们最了解自己的领域。

---

## 2026 = 有用 Agent 元年？

**MCP 上下文膨胀：房间里的大象**

当前 MCP 的问题：

- 加工具 = 加 token 到上下文
- 参数描述往往与当前任务无关
- 比如用 Gmail MCP 读邮件 = 浪费 token 在"发邮件"功能上

**愿景**：每个 token 都精准投放到当前任务。

---

## 真实数据：从 22 小时到 7 分钟

Shopify 的实际收益：

| 场景 | 之前 | 之后 | 提升 |
|------|------|------|------|
| 主题合规审查 | 22 小时 | 7-20 分钟 | 巨大 |
| 候选人评估 | 多小时 | 不到 1 小时 | 显著 |
| Q2 发版调研 | 巨大提示词 | 15 个专精 agent | 高精度 |
| 供应商评估 | 手动 PDF 审查 | 多 agent 验证 | 可扩展 |

**所有场景都需要人工复核**——不是全自动。

---

## 写在最后

Shopify 的多代理系统演进路径，映射了整个行业对 AI 认知的转变：

1. **从怀疑到接受**：需要 CEO 级别的推动力
2. **从通才到专才**：窄专型 agent 效果远超大一统提示词
3. **从工具到架构**：碎片化问题的解法不是更多特警队，而是赋能
4. **从概念到工程**：2026 年的关键词是"有用"——而不是"酷"

当你的 agent 开始协作，当你的 token 消耗开始下降，当你团队的 AI 爱好者开始自己构建——你就知道走对路了。

---

**参考来源**：[What I Learned Building Multi-Agent Systems From Scratch](https://www.infoq.com/presentations/multi-agent-system-lessons/) - Paulo Arruda, Staff Engineer at Shopify