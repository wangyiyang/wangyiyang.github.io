---
layout: post
title: "AI Agent 的版本控制难题，Cloudflare 给了一个解法"
date: 2026-05-11 10:40:00 +0800
categories: [AI, Agent, Engineering]
image: /images/posts/post_cloudflare-artifacts-version-control_001.png
---

如果你用过 AI Agent 生成代码，会遇到一个很具体的问题：**每一次重新生成，都是全新的开始**。

上一次跑出来的不错的结果，点了一下"重新生成"，就没了。没法回滚，没法对比，没法看到两次改了什么。这是 AI Coding 现在的工程状态——产出质量高，但版本控制几乎是零。

Cloudflare 最近内测了一个功能叫 **Artifacts**，就是来解决这个问题的。

<!-- more -->

## 它做了什么

Artifacts 的核心是一个**带版本的文件系统**，兼容 Git 操作语义。简单说：你在 Workers 上跑 AI Agent，它生成的东西可以直接 commit、branch、rollback——就像在管一个正经的代码仓库。

> A versioned filesystem for Workers, APIs, and Git-compatible workflows.

重点不是"文件存储"，是"版本控制"。这才是 AI Agent 真正缺失的基础设施。

## 为什么这件事值得认真对待

AI Agent 的产出和传统代码不一样。传统代码是人写的，版本控制的收益来自"协作"和"审计"；AI Agent 的产出是模型生成的，它的收益来自"对比同一提示词在不同版本模型下的结果差异"。

举个例子：你跑了一次 Prompt A，生成了一个 API 端点，点了一次重新生成，生成了 Prompt B'。你现在想知道 B' 比 A 好在哪，不好在哪——没有版本控制，你只能靠脑子记。

Artifacts 把这个过程变成了：commit A → commit B → `git diff A B`。这才是有意义的对比。

## 技术实现上的几个有意思的点

**1. 基于 Durable Objects**

Cloudflare 的 Durable Objects 是 per-instance 的强一致性存储，Artifacts 底层用它来实现每个 AI Agent 实例的状态隔离。这意味着每一次 commit 都是一个一致的快照，不是"差不多就行"的文件拷贝。

**2. Git-compatible**

不是自己发明一套协议，是直接兼容 Git。这意味着你现有的 CI/CD 流程、代码审查工具、diff 工具——全部可以直接用上。不需要等 Cloudflare 出配套生态，生态现成。

**3. 内嵌在 Workers 运行时**

Agent 运行在 Cloudflare Workers 上，Artifacts 直接作为 Workers 的内置能力暴露，不需要额外部署存储服务。这是 Cloudflare 惯用的方式——把基础设施做成运行时的一部分，而不是附加工具。

## 它没有解决什么

Artifacts 目前是 beta，定位也是文件系统层面的版本控制，不是 AI 层面的"版本控制"。

它不管：

- 不同模型之间的产出对比（这不是它的职责）
- Prompt 的版本化管理（Prompt 工程是另一个话题）
- 多 Agent 协作场景下的版本冲突处理（这个目前没有成熟方案）

所以它解决的是"**产出物**的版本控制"，不是"**决策过程**的版本控制"。这两个之间的差距，目前行业里还没有共识。

## 行业里还有谁在做类似的事

Cursor 的 .cursorrules 是另一种思路——不管版本，而是在每次生成时固化上下文约束，让每次生成都基于同一个规则。

GitHub 的 Agentic Workflows 安全实践则更多关注的是"Agent 在 CI/CD 里能做什么、不能做什么"，不是版本控制本身。

Vercel 的 v0 走的是"生成即部署"，版本控制靠的是平台自己的发布系统，和 Artifacts 的路数不同。

Cloudflare 这个方案是工程层面最彻底的——直接用 Git 语义，而不是发明新概念。

## 一个判断

AI Coding 工具现在普遍缺的不是生成能力，是**工程化基础设施**。

版本控制只是其中一个。调试、测试、审计、权限控制——这些在传统软件开发里是基本功，在 AI Coding 场景里现在几乎都是空白。

Cloudflare Artifacts 的价值不只是它本身，是它代表了一个方向：AI Agent 的工程化基础设施，会从"云厂商的 Workers 平台"这个口子长出来，而不是等 AI Coding 工具自己补课。

*本文同步发布于 [翊行代码](https://www.wangyiyang.cc)*