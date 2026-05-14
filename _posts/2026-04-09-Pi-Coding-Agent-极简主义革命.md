---
layout: post
title: "大道至简：一个 Claude Code 用户的 Pi 救赎"
date: 2026-04-09 08:00:00 +0800
categories: [AI, 技术]
description: "当 Claude Code 变成了一艘宇宙飞船，有人选择造一艘自己的独木舟。"
keywords: 大道至简,Claude,Code,Pi,救赎
mermaid: true
sequence: false
flow: false
mathjax: false
mindmap: false
mindmap2: false
cover: "/images/posts/post_claude-code-vs-cursor-breakthrough_001.webp"
permalink: /2026/04/09/Pi-Coding-Agent-极简主义革命/
---


![封面图](assets/pi-article-cover.jpg)

> 当 Claude Code 变成了一艘"宇宙飞船"，有人选择造一艘自己的独木舟。

## 引言：我的 Claude Code 越来越慢

2025 年，AI 编程助手已经成为开发者的日常工具。从最早的 ChatGPT 复制粘贴，到 GitHub Copilot 的自动补全，再到 Cursor 的 IDE 集成，最后到 Claude Code、Codex、Amp 这类全新的 Coding Agent Harness——这个领域在短短三年内完成了三次范式转移。

但就在这个看似已经"尘埃落定"的市场里，一个叫 **Mario Zechner** 的开发者（你可能用过他写的 libGDX 游戏框架）站出来说：**"这些工具都在教我适应它们，而不是适应我。"**

这句话说到我心坎里了。

我的 Claude Code 最近卡得像 10 年前的机械硬盘。上下文越来越满，每次等它响应，我都能泡杯咖啡。更烦的是，我不知道它在想什么——系统提示词是黑箱，工具集每个版本都在变，昨天能用的 workflow，今天可能就 broken。

于是我找到了 **Pi**。

装了 3 个包：`superpowers`、`pua`、`oh-pi`。没有权限弹窗，没有计划模式，没有子 Agent，没有 MCP。比 Claude Code "少"了 80% 的功能。

但正是这些"少"，让我第一次感觉：**这个工具是我的，不是我在适应它。**

---

## 核心哲学：少即是多，但你说了算

Pi 的官网写着一句很酷的话：

> **"There are many agent harnesses but this one is yours."**
> （有很多 Agent 框架，但这个是你的。）

这句话的背后是一套明确的产品哲学：

### 1. 默认极简，但极度可扩展

Pi 的核心非常小。它**主动放弃**了其他 Agent 视为标配的功能：

- **没有 MCP 支持** —— Mario 认为 CLI 工具 + README 就够了
- **没有子 Agent** —— 需要的话用 tmux 开多个窗口，或者自己写扩展
- **没有权限弹窗** —— 默认"YOLO 模式"，信任开发者知道自己在做什么
- **没有计划模式** —— 需要计划？写个 TODO.md，或者装个扩展
- **没有后台 Bash** —— 用 tmux，全透明，可直接交互
- **没有内置待办** —— 用文件系统，或者自己造

听起来很反直觉？但这正是 Pi 的核心卖点：**它不替你决定什么功能重要，而是给你原语（primitives），让你自己组合。**

### 2. 上下文工程，而不是上下文黑箱

Mario 在使用 Claude Code 时最痛苦的一点：**系统提示词和工具集每个版本都在变**，而且用户看不到、控制不了。

Pi 的做法完全相反：

- **AGENTS.md**：从 `~/.pi/agent/`、父目录、当前目录自动加载项目指令
- **SYSTEM.md**：每个项目可以替换或追加默认系统提示词
- **最小化系统提示词**：默认 prompt 极其精简，给用户最大的上下文窗口控制权
- **Compaction 策略可定制**：上下文满了怎么压缩？你自己决定。可以按主题压缩、按代码感知压缩、甚至换用不同的总结模型

这背后是 Mario 的一个核心洞察：**"上下文工程（Context Engineering）比提示词工程（Prompt Engineering）重要 10 倍。"**

### 3. 树状历史，时间旅行

这是 Pi 最独特的设计之一。

所有会话都以**树结构**存储。你可以随时用 `/tree` 跳转到任意历史节点，从那里继续对话。所有分支保存在单个文件里，可以按消息类型过滤、给关键节点打书签。

更妙的是：
- `/export` 导出 HTML
- `/share` 上传到 GitHub Gist，生成可分享的 URL

这意味着你的 AI 编程会话可以像 Git 仓库一样被浏览、分叉、分享。

---

## Pi 的"推背感"

![极简对比图](assets/pi-simplicity.png)

装完 oh-pi 后，第一个明显感觉：**快**。

不是"优化后的快"，是"本来就该这么快"的快。Claude Code 越来越慢，我已经习惯了等它"思考"——其实它是在处理越来越长的系统提示词和隐藏指令。

Pi 的最小化 prompt 带来了三个直接好处：

**1. 响应更快**

首 token 延迟明显更低。同样的代码补全请求，Claude Code 可能要等 2-3 秒"预热"，Pi 几乎是即时响应。这种"推背感"让我想起了第一次用 SSD 替代机械硬盘的感觉——不是"稍快一点"，是"原来可以这么流畅"。

**2. 上下文更干净**

我的指令不会被系统提示词"挤掉"。在 Claude Code 里，经常遇到"我刚告诉它的业务规则，下一轮就忘了"——因为上下文满了，它被压缩掉了。Pi 的精简系统 prompt 意味着留给我的代码和业务逻辑的空间更多，关键信息更不容易丢失。

**3. 更省钱**

这是最实在的。我算过一笔账：同样的代码重构任务，Claude Code 动辄几千 token 的系统开销，Pi 只有几百。长期用下来，**API 账单能差出几倍**。

这不是"抠门"，是"精确"——我只为我需要的东西付费，不为厂商的"智能推荐"和"最佳实践"买单。

---

## 技术架构：四个原语包

Pi 不是单文件脚本，而是由四个精心设计的包组成：

### 1. pi-ai：统一 LLM API

支持 **15+ 提供商**：Anthropic、OpenAI、Google、Azure、Bedrock、Mistral、Groq、Cerebras、xAI、Hugging Face、Kimi、MiniMax、OpenRouter、Ollama...

关键特性：
- **跨提供商上下文移交**：在 Claude 和 GPT 之间无缝切换，不丢失上下文
- **结构化工具结果**：用 TypeBox 定义 schema，不是脆弱的 JSON 拼接
- **Token 和成本追踪**：精确到每次调用的花费计算
- **自托管友好**：不依赖 Vercel AI SDK 这种对自托管模型支持不佳的库

Mario 在博客里吐槽：OpenAI 的 Completions API、Responses API、Anthropic Messages API、Google Generative AI API——这四套 API "都差不多，但每家理解都不一样"。比如 Cerebras 和 xAI 不喜欢 `store` 字段，Mistral 用 `max_tokens` 而不是 `max_completion_tokens`，Grok 模型不支持 `reasoning_effort`...

pi-ai 的解决方案：为每个提供商写适配器，外加一个覆盖所有功能的测试套件。

### 2. pi-agent-core：Agent 循环

处理工具执行、验证、事件流的最小化核心。

### 3. pi-tui：终端 UI 框架

采用**保留模式 UI（Retained Mode）** + **差分渲染（Differential Rendering）**，实现几乎无闪烁的更新。

这和其他 Agent 的即时模式 UI 形成对比——Pi 的 UI 更像 React，有组件树和状态管理，而不是每帧重绘。

### 4. pi-coding-agent：CLI 入口

把上面三个包连起来，加上会话管理、自定义工具、主题、项目上下文文件。

---

## 四种使用模式

Pi 不只是一个聊天界面：

| 模式 | 用法 | 场景 |
|------|------|------|
| **Interactive** | `pi` | 日常 TUI 交互 |
| **Print/JSON** | `pi -p "query"` / `--mode json` | 脚本集成、事件流 |
| **RPC** | JSON over stdin/stdout | 非 Node.js 集成 |
| **SDK** | 编程嵌入 | 如 OpenClaw 的集成 |

OpenClaw（另一个开源项目）就是基于 Pi 的 SDK 模式构建的，证明了这种架构的可扩展性。

---

## oh-pi：Pi 的"oh-my-zsh"

我装的 3 个包里，`oh-pi` 是最关键的。它是 Pi 生态的"oh-my-zsh"——一条命令把 Pi 从裸机变成全配置。

```bash
npx oh-pi  # 配置一切
pi         # 开始编码
```

就这样。oh-pi 会自动检测环境、引导配置，并写入 `~/.pi/agent/`。已有配置？会先备份，再覆盖。

### 你会得到什么

```
~/.pi/agent/
├── auth.json          API 密钥（0600 权限）
├── settings.json      模型、主题、思维级别
├── keybindings.json   Vim/Emacs 快捷键（可选）
├── AGENTS.md          角色专属 AI 指南
├── extensions/        8 个扩展
│   ├── safe-guard     危险命令确认 + 路径保护
│   ├── git-guard      自动 stash 检查点 + 脏仓库警告
│   ├── auto-session   从首条消息自动命名会话
│   ├── custom-footer  增强状态栏（token/成本/时间/git/cwd）
│   ├── compact-header 精简启动信息
│   ├── auto-update    启动时检查更新
│   ├── bg-process     后台进程 — 自动后台化长时间运行的命令
│   └── ant-colony/    自主多智能体蚁群系统（可选）
├── prompts/           10 个模板（/review /fix /commit /test ...）
├── skills/            11 个技能（工具 + UI 设计 + 工作流）
└── themes/            6 个自定义主题
```

### 蚁群系统：多智能体协作

![蚁群系统示意图](assets/pi-ant-colony.png)

这是 oh-pi 的核心功能。模拟真实蚁群生态的多智能体系统，深度整合 pi SDK。

```
你: "把认证从 session 重构为 JWT"

oh-pi:
  🔍 侦察蚁（haiku — 快速、低成本）扫描代码库
  📋 生成任务池
  ⚒️ 工蚁（sonnet — 能力强）并行执行
  🛡️ 兵蚁（sonnet — 严谨）审查变更
  ✅ 完成，报告自动注入对话
```

**关键设计：**
- **进程内 Agent**：每只蚂蚁是 `AgentSession`（pi SDK），非子进程，零启动开销
- **自适应并发**：自动找最优并行度，CPU > 85% 自动降速，429 限流自动退避
- **文件安全**：一个文件只有一只蚂蚁，冲突自动阻塞
- **成本透明**：追踪每只蚂蚁和总花费
- **自动触发**：LLM 自己判断什么时候该用蚁群（≥3 文件修改、可并行工作流）
- **信号协议**：结构化通信，状态完全可见
  - `COLONY_SIGNAL:LAUNCHED` → `SCOUTING` → `WORKING` → `REVIEWING` → `COMPLETE`
- **轮次限制**：侦察蚁 8 轮、工蚁 15 轮、兵蚁 8 轮，防止失控

**这和 Claude Code 的本质区别：**

Claude Code 的子 Agent 是黑箱——你不知道什么时候触发、怎么工作、花了多少 token。

Pi + oh-pi 的蚁群是**白箱**——信号协议公开，轮次限制明确，实时 UI 显示进度，成本完全透明。

### 技能系统

oh-pi 附带 11 个技能，分三类：

**工具技能**（零依赖 Node.js 脚本）：
- `context7` — 通过 Context7 API 查询最新库文档
- `web-search` — DuckDuckGo 搜索（免费，无需密钥）
- `web-fetch` — 提取网页内容为纯文本

**UI 设计规范技能**：
- `liquid-glass` — Apple WWDC 2025 半透明玻璃风格
- `glassmorphism` — 毛玻璃模糊 + 透明
- `claymorphism` — 柔和 3D 粘土质感
- `neubrutalism` — 粗边框、偏移阴影、高对比

**工作流技能**：
- `quick-setup` — 检测项目类型，生成 .pi/ 配置
- `debug-helper` — 错误分析、日志解读、性能分析
- `git-workflow` — 分支、提交、PR、冲突解决
- `ant-colony` — 蚁群管理命令和策略

### 提示词模板

| 模板 | 功能 |
|------|------|
| `/review` | 代码审查：bug、安全、性能 |
| `/fix` | 最小改动修复错误 |
| `/explain` | 代码解释，从简到详 |
| `/refactor` | 保持行为的重构 |
| `/test` | 生成测试 |
| `/commit` | Conventional Commit 消息 |
| `/pr` | Pull Request 描述 |
| `/security` | OWASP 安全审计 |
| `/optimize` | 性能优化 |
| `/document` | 生成文档 |

---

## 扩展生态：50+ 示例，无限可能

Pi 的扩展机制是它的杀手锏。扩展是**完整的 TypeScript 模块**，可以访问：

- 工具（Tools）
- 命令（Commands）
- 键盘快捷键
- 事件系统
- 完整 TUI

官方仓库提供了 **50 多个扩展示例**：

- **子 Agent**：用 tmux 管理多实例
- **计划模式**：自己实现的规划工作流
- **权限门控**：自定义确认流程
- **路径保护**：防止 AI 碰敏感目录
- **SSH 执行**：远程服务器操作
- **沙箱模式**：容器化运行
- **MCP 集成**： ironic——用扩展加上你"不需要"的 MCP
- **自定义编辑器**、状态栏、浮层...

而且扩展可以打包成 **Pi Packages**，通过 npm 或 git 分享：

```bash
pi install npm:@foo/pi-tools
pi install git:github.com/badlogic/pi-doom
```

是的，有人用 Pi 扩展写了 Doom 游戏。

---

## 上下文管理：比 RAG 更激进的思路

Pi 的上下文管理有几个独特设计：

### Skills：按需加载的能力包

不是把所有工具塞进系统提示词，而是**按需加载**。类型 `/name` 触发，避免撑爆 prompt cache。

### Prompt Templates：可复用的 Markdown 模板

把常用提示词写成 Markdown 文件，类型 `/template-name` 直接展开。

### Dynamic Context：扩展注入

扩展可以在每次对话前注入消息、过滤历史、实现 RAG、甚至构建长期记忆系统。

这意味着：**Pi 的上下文管理是开放架构，不是内置功能。**

---

## 对比：Pi vs Claude Code vs Cursor

| 维度 | Pi | Claude Code | Cursor |
|------|-----|-------------|---------|
| **系统提示词** | 完全可见/可替换 | 黑箱，每版变化 | 部分可见 |
| **上下文控制** | 精细到每个 token | 自动管理 | 中等 |
| **会话历史** | 树状，可分叉 | 线性 | 线性 |
| **可扩展性** | 扩展 = 完整 TS 模块 | 有限 | 插件生态 |
| **自托管模型** | 原生支持 | 较差 | 一般 |
| **功能默认** | 极简 | 丰富 | 丰富 |
| **学习曲线** | 陡峭但透明 | 平缓但黑箱 | 平缓 |

Pi 不适合所有人。如果你只想"开箱即用"，Claude Code 可能是更好的选择。但如果你是那种**"想知道每个字节怎么工作"**的开发者，Pi 是 2025 年唯一认真为你设计的工具。

---

## 安装与上手

```bash
# 一键安装 Pi
curl -fsSL https://pi.dev/install.sh | bash

# 安装 oh-pi 增强
npx oh-pi

# 开始编码
pi
```

启动后，Pi 会从当前目录和父目录自动加载 `AGENTS.md` 和 `SYSTEM.md`，你可以立即开始定制自己的工作流。

---

## 结语：大道至简，不是简陋，是恰好足够

我以为 Pi 是"简陋版 Claude Code"，装了 oh-pi 才发现——**它是乐高，Claude Code 是成品玩具**。

成品玩具拆开就坏。乐高你可以拆掉蚁群、只留核心；可以换侦察蚁的模型；可以看每只蚂蚁花了多少 token。

我的 Pi 装了 3 个包，比 Claude Code 少了 20 个功能。但每个功能都是我选的，每个行为都是我控制的。响应更快、上下文更干净、账单更便宜——这不是妥协，是**精确**。

Mario 在博客结尾写道：

> **"It's not much, but it's mine."**
> （东西不多，但它是我的。）

这句话概括了 Pi 的全部精神。

在 AI 工具越来越"智能化"、也越来越"黑箱化"的今天，Pi 代表了一种反潮流的选择：**把控制权还给开发者**，哪怕这意味着更高的学习曲线。

大道至简，不是"少"，是**恰好足够，且你知道每一块的用途**。

如果你也曾因为 Claude Code 的某个更新打破了你的工作流而抓狂，如果你也想看看 AI 编程助手的"引擎盖"下面到底是什么——Pi 值得你一试。

毕竟，正如它的 Slogan 所说：

> **"There are many agent harnesses but this one is yours."**

---

## 参考链接

- **官网**：https://pi.dev/
- **GitHub**：https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent
- **npm 包**：https://www.npmjs.com/package/@mariozechner/pi-coding-agent
- **oh-pi**：https://www.npmjs.com/package/oh-pi
- **Discord 社区**：https://discord.com/invite/3cU7Bz4UPx
- **作者博客**（设计哲学）：https://mariozechner.at/posts/2025-11-30-pi-coding-agent/
- **扩展示例**：https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent/examples/extensions/
- **Pi Packages 市场**：https://pi.dev/packages
- **OpenClaw（基于 Pi SDK 的项目）**：https://github.com/OpenClaw/OpenClaw
