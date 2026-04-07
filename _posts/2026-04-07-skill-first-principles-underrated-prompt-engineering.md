---
layout: post
title: "Skill 的第一性原理：被低估的 Prompt 工程"
categories: [Agent, AI, Prompt-Engineering, Tooling]
description: "为什么 Codex、Windsurf、Claude Code 都在往 Skill / Workflow 收敛？从第一性原理看，Skill 不是提示词边角料，而是 Prompt Engineering 走向工程化后的任务封装。"
keywords: Skill, Prompt Engineering, Codex, Claude Code, Windsurf, Workflow, Agent
mermaid: false
sequence: false
flow: false
mathjax: false
mindmap: false
mindmap2: false
---

最近我注意到一个很有意思的变化：**Codex 官方已经明确把 custom prompts 标成 deprecated，建议直接用 skills 来承载可复用指令。**

这件事本身看起来像个产品细节，但我第一反应不是“噢，功能改版了”，而是：**终于，连产品层也开始承认，可复用 prompt 的终点，其实不是 prompt 收藏夹，而是 skill。**

过去一年里，我自己在用这些 AI coding / agent 工具时，已经反复遇到同一种变化：

- 一开始，大家都在教模型“这次怎么做”
- 用久了，就开始沉淀“这类事以后怎么做”
- 再往后，就会发现：真正值钱的不是某一句 prompt，而是那套可复用的方法、边界和路径

所以我越来越觉得：**Skill 不是 Prompt Engineering 的边角料，而是 Prompt Engineering 开始工程化之后的重要产物。**

## 为什么现在重新谈 Skill？

因为这已经不是某一个产品在改名，而是几条产品线在一起收敛。

### Codex：从 custom prompts 走向 skills

Codex 官方文档已经明确写了：

> **Custom prompts are deprecated. Use skills for reusable instructions and workflows instead.**

这背后的变化，其实非常关键：

- 从**一次性 prompt** 走向 **长期复用能力**
- 从**手动触发文案** 走向 **结构化任务单元**
- 从**个人习惯** 走向 **团队共享和工程治理**

它不再把“可复用经验”理解成几段收藏起来的文字，而是开始把它理解成：

**一个可被显式调用、也可被系统自动选中的能力单元。**

### Windsurf：从 Rules 走向 Workflows

Windsurf 的 Workflows 也很能说明问题。

它本质上不是让你“多存几段提示词”，而是在鼓励你把一类重复动作沉淀成一条结构化路径。

比如：

- 拉代码 → 改配置 → 部署到测试环境 → 生成 PR
- 拉 PR 评论 → 逐条处理 → 修复 → 汇总结果
- 更新依赖 → 跑测试 → 修复问题 → 提交变更

这些都不是单轮问答，而是一组有顺序、有上下文、有目标结果的动作。

它真正鼓励的是：

> 把组织里反复出现的工作方法沉淀下来，而不是每次都临场发挥。

### Claude Code：从项目说明走向 instructions + skills + hooks

Claude Code 这边的演化也很典型。

它不是单独强调某一个功能点，而是在逐步把任务执行所需的几个层次拆清楚：

- `CLAUDE.md`：项目级长期说明和约束
- skills：可复用任务能力封装
- hooks：更确定性的自动化执行点

这套设计背后的逻辑很清楚：

- 什么是长期有效的上下文
- 什么是某类任务的可复用经验
- 什么又应该被固化成更确定的自动化行为

也就是说，Agent 的稳定执行，本来就不该只靠一段大 prompt 硬扛。

## Skill 和 Prompt 的根本区别，到底是什么？

很多人第一次听到 Skill，会下意识把它理解成：

- 提示词模板
- 一段 system prompt
- 给 Agent 塞进去的操作说明

这么理解不能说完全错，但太轻了。

因为在真实使用里，Skill 真正承担的，从来不只是“告诉模型怎么说”，而是：

**把一类任务的做事方法、约束边界、调用路径、输出规范，固化成一个可复用、可迭代、可治理的执行单元。**

所以 Prompt 和 Skill 的差别，不只是“长短不同”或者“文件形式不同”。

更本质的区别在于：

### Prompt 更像一次性表达

它通常解决的是：

- 这次你要怎么理解我的需求
- 这次你要按什么风格回答
- 这次你要用什么方式完成

Prompt 对单次效果很重要，但它天然偏即时、偏临场、偏个人化。

### Skill 更像任务级封装

它解决的是：

- 这一类任务以后统一怎么做
- 什么边界必须遵守
- 哪些步骤不能漏
- 结果应该长成什么样
- 这套方法怎么复用、怎么迭代、怎么共享

所以 Skill 的核心，不是“更强的 prompt”，而是：

**把提示从临时技巧，升级成稳定执行资产。**

## 为什么 Skill 会越来越重要？

因为 Agent 一旦开始进入重复任务场景，就迟早会碰到三个问题。

### 第一，重复任务不能每次都重新教

如果你已经在反复做同一类事，比如：

- 写周报
- 改 PR
- 发布文章
- 生成封面图
- 入选题库并补字段

那你迟早会发现，真正浪费时间的，不是模型生成本身，而是你每次都要重新讲一遍规则。

这时候，最自然的动作就是把这类规则沉淀成 Skill。

### 第二，稳定性比惊艳更重要

一次惊艳回答没那么难，难的是：

- 下次还能不能这么做
- 别人拿去能不能复用
- 换个仓库还能不能用
- 规则更新后能不能一起演进

这本质上已经不是提示词技巧问题，而是执行治理问题。

### 第三，团队协作需要共享抽象层

当 Agent 从个人玩具走向团队协作时，Prompt 收藏夹就不够用了。

团队需要的是：

- 可共享
- 可版本化
- 可 review
- 可持续迭代

Skill / Workflow 这类形式，天然比零散 prompt 更接近团队工程实践。

## 被低估的，不是 Skill，而是 Prompt Engineering 的下一阶段

我越来越觉得，很多人低估 Skill，本质上是在用旧眼光看新问题。

如果你把 Prompt Engineering 理解成“写一句更聪明的话让模型听懂”，那 Skill 当然像边角料。

但如果你把 Prompt Engineering 理解成：

**如何把模型放进真实工作系统里稳定做事**，

那 Skill 就不再是附属品，而是一个非常自然的工程产物。

从这个角度看，Skill 其实回答的是一个更关键的问题：

> 当 Agent 不再只做一次性回答，而开始承担重复任务时，我们该如何把经验沉淀成可复用的执行资产？

这就是为什么我越来越觉得：

**Skill 不是 Prompt Engineering 的终点配件，而是它工程化之后的重要中间层。**

## 写在最后

如果只看表面，最近这些产品变化像是在改名：

- custom prompts → skills
- rules → workflows
- instructions + skills + hooks

但如果把这些变化放在一起看，会发现它们都在指向同一个方向：

**Agent 工具正在从“靠临时 prompt 驱动”走向“靠结构化任务封装驱动”。**

这不是细枝末节，而是产品和工程实践都在发生的一次收敛。

所以我现在越来越愿意把 Skill 看成一件更严肃的事：

它不是 prompt 的别名，而是可复用经验开始被工程化之后，自然长出来的那一层。

真正被低估的，也许不是 Skill 本身，而是：

**Prompt Engineering 一旦走向真实执行，迟早都会长出 Skill 这一层。**
