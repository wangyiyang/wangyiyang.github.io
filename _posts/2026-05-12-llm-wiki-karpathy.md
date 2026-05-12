---
layout: post
title: "Karpathy 的 LLM Wiki 模式：让 AI 替你维护知识库"
date: 2026-05-12 09:00:00 +0800
categories: [AI, Agent, Knowledge Management]
tags: [LLM Wiki, RAG, Karpathy, Obsidian, 知识管理, Agent]
author: 王翊仰
description: "传统 RAG 每次都在重新发现知识。Karpathy 的 LLM Wiki 模式让 AI 增量维护一个持久化的知识库——Cross references 已建好、矛盾已标记、综合分析已完成。本文详解三层架构、三大操作、以及如何用 Claude Code 落地这套工作流。"
keywords: "LLM Wiki, RAG对比, Karpathy, Obsidian, 知识管理, Agent工程, 个人知识库, Claude Code"
---

最近 Karpathy 发了一个 [gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)，提出了一个他认为更适合个人知识管理的模式：**LLM Wiki**。

我看完之后觉得这是继 MCP 之后，又一个值得写进工具箱的理念。

## RAG 的问题：每次都在重新发现知识

大多数人和 LLM 处理文档的方式是 RAG：

1. 上传一堆文件到某个知识库
2. 问问题时，LLM 检索相关片段
3. 生成答案

这套流程能跑，但有一个根本缺陷：**LLM 在每次问答时都要从零发现知识**。

- 问一个需要综合 5 份文档的问题？LLM 必须每次都去找、去拼凑那些相关片段
- 没有积累。问过了，下次再问，还是从零开始
- NotebookLM、ChatGPT 文件上传、大多数 RAG 系统，都是这个逻辑

## LLM Wiki 的核心思想

Karpathy 的想法不一样：

> Instead of just retrieving from raw documents at query time, the LLM **incrementally builds and maintains a persistent wiki** — a structured, interlinked collection of markdown files that sits between you and the raw sources.

翻译成人话：**LLM 不只是在查询时检索，而是**增量维护**一个持久化的 Wiki**。

当你添加一篇新文档时，LLM 不会只是索引它供后续检索。它会：
- 阅读文档
- 提取关键信息
- 把这些信息**整合进现有的 Wiki**
- 更新相关实体页面
- 修订主题摘要
- 标记新数据与旧说法矛盾的地方

**知识被编译一次，然后持续保持最新。**

Cross references 已经建好。矛盾已经被标记。综合分析已经完成。Wiki 随着每次添加源和每个问题而变得越来越丰富。

## 三层架构

LLM Wiki 模式有三个层：

| 层 | 作用 | 谁操作 |
|------|------|--------|
| **Raw Sources** | 原始文档（文章、论文、图片），不可变，这是你的事实来源 | 你（只读） |
| **Wiki** | LLM 生成和维护的 Markdown 文件（摘要、实体页、概念页、综合分析） | LLM（完全掌控读写） |
| **Schema** | 指令文件（如 CLAUDE.md / AGENTS.md），告诉 LLM Wiki 的结构、约定、工作流 | 你和 LLM 共建 |

```
Raw Sources（不可变）→ LLM 读取 → Wiki（LLM 增量维护）
                            ↑
                        Schema（指令）
```

关键：**Wiki 完全由 LLM 读写。你只读 Wiki，LLM 写 Wiki。** 这和传统笔记软件完全不同——不是你在整理，是 AI 在帮你维护。

## 三个核心操作

### Ingest：把新文档喂给 Wiki

流程：
1. 把新文档丢进 Raw Sources 目录
2. 告诉 LLM"帮我处理这篇"
3. LLM 读取文档，和你讨论要点
4. LLM 在 Wiki 中写摘要页、更新 index、更新相关实体和概念页、追加 log 记录

**一篇源文档可能涉及 10-15 个 Wiki 页面的更新。** 人类做这件事会累死，但 LLM 可以轻松搞定。

Karpathy 个人偏好一次 Ingest 一篇、保持参与——他读摘要、检查更新、引导 LLM 强调什么。但你也可以批量 Ingest，取决于你的风格。

### Query：向 Wiki 提问

流程：
1. 你向 LLM 提问
2. LLM 读取 index.md 找到相关页面
3. 深入阅读相关页面
4. 综合答案，并附上引用

答案可以是：Markdown 页面、对比表格、幻灯片（Marp）、图表（matplotlib）。**重要的是：如果一个答案有价值，它应该被写回 Wiki 成为新页面。** 你探索出的关联、分析、对比——这些不应该消失在对话历史里，应该累积进知识库。

### Lint：让 Wiki 保持健康

定期让 LLM 做健康检查：
- 页面间是否有矛盾？
- 是否有被新源文档更新的过时说法？
- 是否有孤儿页面（没有内链指向它）？
- 重要概念被提到了但没有自己的页面？
- 是否有缺失的交叉引用？

LLM 擅长提出新的问题和建议新的信息源。这个维护成本接近零，人类则会因为成本增长太快而放弃 Wiki。

## 两个关键文件

**index.md** — 内容目录
- 按分类组织（实体、概念、源文档等）
- 每页一行摘要 + 链接
- LLM 在每次 Ingest 时更新
- 查询时 LLM 先读 index 再深入相关页面
- 在中等规模下（~100 源，~数百页）效果出奇好，不需要 Embedding RAG 基础设施

**log.md** — 时间线日志
- append-only 的操作记录
- 格式：`## [2026-04-02] ingest | Article Title`
- `grep "^## \[" log.md | tail -5` 快速查看最近活动
- 追踪 Wiki 演化时间线

```
index.md  ← 内容导向（是什么）
log.md   ← 时间导向（发生了什么）
```

## 实战：用 Claude Code 落地 LLM Wiki

以下是 Karpathy 给出的工作流（我补充了实操细节）：

### 1. 建好三层目录

```bash
llm-wiki/
├── raw/           # 源文档（PDF、文章、图片）
├── wiki/          # LLM 生成和维护的页面
│   ├── index.md
│   ├── log.md
│   ├── entities/  # 实体页面（人、项目、概念）
│   ├── concepts/  # 概念页面
│   └── sources/   # 源文档摘要页
└── CLAUDE.md      # Schema（LLM 的指令文件）
```

### 2. 写好 Schema（CLAUDE.md）

```markdown
# LLM Wiki Schema

## Wiki 结构
- /wiki/index.md       — 内容目录
- /wiki/log.md         — 操作日志
- /wiki/entities/      — 实体页（人/项目/公司）
- /wiki/concepts/      — 概念页（技术/方法/理论）
- /wiki/sources/       — 源文档摘要页

## Ingest 工作流
1. 读取源文档，提取关键信息
2. 写摘要页到 /wiki/sources/
3. 更新 index.md
4. 更新相关实体/概念页面（可能涉及 10-15 个文件）
5. 追加 entry 到 log.md

## Query 工作流
1. 读 index.md 找到相关页面
2. 深入阅读相关页面
3. 综合答案，附上引用
4. 如果答案有价值 → 写回 Wiki 成为新页面

## Lint 检查项
- 跨页面的矛盾说法
- 被新源更新的过时内容
- 孤儿页面（无内链）
- 缺失的交叉引用

## 输出格式
答案可以是：Markdown / 对比表格 / Marp 幻灯片 / matplotlib 图表
```

### 3. 用 Claude Code 操作 Wiki

```bash
# 启动 Claude Code，明确 Wiki 上下文
claude --prompt "
我在维护一个 LLM Wiki，目录在 ~/llm-wiki。
Schema 文件是 ~/llm-wiki/CLAUDE.md。

今天我想：
1. Ingest 这篇新文章：~/Downloads/article.pdf
2. 检查 Wiki 健康度

请按 CLAUDE.md 的工作流执行。"
```

### 4. 可选工具链

| 工具 | 用途 |
|------|------|
| **Obsidian** | Wiki 的 IDE，LLM 在一边改，你实时浏览结果 |
| **Obsidian Web Clipper** | 把网页文章快速转 Markdown 进 raw 目录 |
| **qmd** | 本地 Markdown 搜索（BM25 + vector 混合搜索 + LLM 重排） |
| **Marp** | 从 Markdown 生成幻灯片 |
| **Dataview** | Obsidian 插件，查询页面 frontmatter 生成动态列表 |

### 5. Wiki 即 Git 仓库

Wiki 就是一个 Markdown 文件的 Git 仓库——**免费获得版本历史、分支、协作**。

```bash
cd ~/llm-wiki
git add .
git commit -m "ingest: Karpathy LLM Wiki pattern"
git push  # 多端同步，协作也轻松
```

## 为什么这比 RAG 更适合个人知识管理

| 维度 | RAG | LLM Wiki |
|------|-----|---------|
| 知识积累 | ❌ 每次从零发现 | ✅ 增量编译，持续保持最新 |
| 交叉引用 | ❌ 需要自己维护 | ✅ LLM 自动建好 |
| 矛盾检测 | ❌ 无 | ✅ LLM 主动标记 |
| 维护成本 | 索引后较低 | **接近零**（LLM 在做） |
| 适合场景 | 简单问答 | **深度研究、个人成长、系统性积累** |
| 人类参与度 | 低 | **高**（但做的是真正的思考工作） |

RAG 是搜索引擎。LLM Wiki 是**记忆养成系统**。

RAG 适合"快速回答一个事实性问题"——答案是现成的，检索出来就行。

LLM Wiki 适合"深度研究一个主题"——需要综合多篇文档、追踪演变、建立关联。这些工作在 RAG 里每次都要从零做，在 Wiki 里已经做好了。

## 适用场景

Karpathy 列了几个：

- **个人成长**：跟踪自己的目标、健康、心理、自我提升——日记、文章、播客笔记
- **研究**：对某个主题深入几周甚至几个月——读论文、文章、报告，逐步建立综合 Wiki
- **读书**：每章归档，建角色页、主题页、情节线页。读完你就有了一本丰富的伴侣 Wiki
- **团队知识库**：内部 Wiki，由 LLM 维护，喂入 Slack 线程、会议记录、项目文档
- **竞争分析、尽职调查、旅行规划、课程笔记**——任何需要**随时间积累知识**的场景

## 核心洞察

> The tedious part of maintaining a knowledge base is not the reading or the thinking — it's the bookkeeping.

人类放弃 Wiki 是因为**维护成本增长比价值快**。交叉引用要更新、摘要要修订、矛盾要标记——这些 bookkeeping 工作会吃掉所有精力。

LLM 不厌倦 bookkeeping。不遗忘更新交叉引用。一次能改 15 个文件。

**人类做不了的维护，LLM 来做。人类做真正有价值的事：提出好问题、思考含义、把碎片变成意义。**

这和 Vannevar Bush 1945 年设想的 Memex（个人 curated 知识库，文档间有关联）一脉相承——Bush 没能解决的是谁来维护。LLM 解决了。

---

*你也在用 Obsidian 或类似工具管理知识吗？LLM Wiki 模式有没有让你想到什么新玩法？*

<!--more-->

**相关阅读：**
- [MCP 协议正在硬化：从玩具到生产基础设施](/2026/04/09/MCP-协议正在硬化/)
- [Pi：Coding Agent 的极简主义革命](/2026/04/09/Pi-Coding-Agent-极简主义革命/)
- [为什么 Agent 真正走进生产，核心不是模型，而是 Harness](/2026/04/09/为什么-Agent-真正走进生产-核心不是模型-而是-Harness/)