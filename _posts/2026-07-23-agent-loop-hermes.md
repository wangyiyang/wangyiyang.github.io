---
layout: post
title: "从 Agent Loop 到自进化：Hermes 有哪些是我们可以抄的"
categories: [AI Agent]
description: "承接《Agent Loop 的文章好写》结尾对 OpenClaw/pi 的推荐，回答"真要给 OPc 自研执行 core 时为什么参照物换成 Hermes"：一是 agent + skill 形态太黑盒，要把可控执行程序化；二是要前后端分离，不被前端 TS 体系主导。正文拆 Hermes 自研 loop 和两层自进化（运行时闭环 + DSPy/GEPA 离线进化），落点是"哪些直接抄、哪些反着做""
keywords: AI Agent
mermaid: false
sequence: false
flow: false
mathjax: false
mindmap: false
mindmap2: false
---

![](/images/posts/2026-07-23-agent-loop-hermes/01.png)
最近 Nous Research 的 Hermes Agent 挺火，官网把它称为“会随你成长”的 Agent。我不太关心这句宣传语，真正让我停下来翻源码的是两个问题：它的 loop 到底怎么跑？它说的“自进化”，最后改动的究竟是什么？
这件事还有一点前情。在 <mention-page url="https://app.notion.com/p/75f3e1592f914d7eaf7db5ab235a81cc"/> 结尾，我建议想学 Agent Loop 的人先看 OpenClaw 和它的内核 pi，不要急着从零手搓。这个建议没变。但轮到我给 OPc 做执行 core 时，主要参照物却换成了 Hermes。
先说最现实的问题。OpenClaw 和 Hermes 都大量依赖 agent + skill：Skill 是自然语言，缺少稳定契约，也很难做回归；Hermes 还允许后台 LLM 自己判断何时创建或修改技能。出了问题，排查链路会很长。我在 <mention-page url="https://app.notion.com/p/e18d94f9068d41ae93d0f6f46728ec8e"/> 里已经踩过这类坑，所以这次更想把能确定的执行过程写成程序，把模型留在真正需要判断的位置。
另一个原因是系统形态。pi 是 TS monorepo 里的嵌入式库，和前端运行时靠得很近。我的设想则是把 core 做成 headless 服务，CLI、IM 和 Web 只是不同入口。以后 OPc 真要从自用工具变成多人系统，也不用再拆一次前后端。Hermes 的 Python `AIAgent` 正好提供了一个更接近这个方向的样本。
下面不是一份完整的 Hermes 源码导读。我只拆跟这次架构选择有关的部分，也会明确写出哪些地方准备借鉴，哪些地方我不会照搬。
# 一、Loop：它没有"pi"
OpenClaw 的核心 loop 来自独立的 pi（pi-agent-core + pi-ai）：Read、Write、Edit、Bash 四个基础工具，再加一套扩展系统。Hermes 没有抽出一个对应的“pi”，loop 就写在主仓库里。顺着调用链看，核心集中在两处：
- `run_agent.py` 里的 `AIAgent` 类，负责整个 "Think–Act–Observe" 循环，而且平台无关——CLI、消息网关、ACP 共用同一个 loop
- `agent/conversation_loop.py` 里的 `run_conversation`，管单轮对话的主循环（模型调用、工具分发、重试、fallback、上下文压缩）
一轮 loop 大致是这样走的：
1. 把用户消息追加到会话历史
2. 构建 / 复用缓存的 system prompt
3. 上下文超过 50% 就先做一次压缩
4. 按三种 API 模式之一组装消息：`chat_completions` / `codex_responses` / `anthropic_messages`（内部统一成 OpenAI 兼容格式）
5. 注入临时 prompt 层（预算警告、上下文压力等），Anthropic 模式下加 prompt caching 标记
6. 发起一次"可中断的" API 调用
7. 看响应：有 tool_calls 就执行工具、把结果塞回历史、回到第 4 步继续循环；纯文本就持久化会话、必要时刷新记忆，然后返回
画成流程图更直观：
![](/images/posts/2026-07-23-agent-loop-hermes/02.png)
落到代码上，主循环大致长这样（基于 `agent/conversation_loop.py` 的源码做了简化，非逐行原文）：
```python
# agent/conversation_loop.py · run_conversation 主循环（简化版）
while api_call_count < agent.max_iterations and (
    agent.iteration_budget.remaining > 0 or agent._budget_grace_call
):
    api_call_count += 1

    # ① 调模型前先看上下文要不要压缩
    if agent.compression_enabled and _compressor.should_compress(_real_tokens):
        messages = agent._compress_context(messages)

    # ② 发起一次可中断的 API 调用（内部统一成 OpenAI 兼容格式）
    response = client.chat.completions.create(
        model=..., messages=messages, tools=...)
    assistant_message = response.choices[0].message

    # ③ 有 tool_calls → 执行工具，把结果塞回历史，回到循环顶部
    if assistant_message.tool_calls:
        results = agent._execute_tool_calls(assistant_message.tool_calls)
        messages.extend(results)
        continue

    # ④ 纯文本 → 持久化会话、必要时刷新记忆，返回最终回复
    break
```
工具系统也是自己写的：中央注册表 `ToolRegistry` 在 `tools/registry.py` 里，`model_tools.py` 启动时扫描 `tools/` 目录并 import，每个工具文件在 import 时自注册（`registry.register()`）。注册入口就是模块顶层的一次函数调用：
```python
# tools/clarify_tool.py —— 模块顶层直接自注册
registry.register(
    name="clarify",
    toolset="clarify",
    schema=CLARIFY_SCHEMA,
    handler=lambda args, **kw: clarify_tool(
        question=args.get("question", ""),
        choices=args.get("choices"),
        callback=kw.get("callback")),
    check_fn=check_clarify_requirements,
    emoji="❓",
)
```
发现机制也很直白：先用 AST 静态判断文件里有没有顶层 `registry.register()` 调用，再 import——import 即注册：
```python
# tools/registry.py —— 扫描 tools/ 目录，import 即注册（节选）
def discover_builtin_tools(tools_dir: Optional[Path] = None) -> List[str]:
    module_names = [
        f"tools.{path.stem}"
        for path in sorted(tools_path.glob("*.py"))
        if path.name not in {"__init__.py", "registry.py", "mcp_tool.py"}
        and _module_registers_tools(path)  # AST 判断，不用真的 import
    ]
    for mod_name in module_names:
        importlib.import_module(mod_name)  # import 时触发 registry.register()
```
两条路线的差别很直接。OpenClaw 把独立的 pi 包起来，接到多个渠道；Hermes 自己维护整套平台无关的 loop。pi 更小、更容易复用，Hermes 则把多 provider 和多平台的控制权留在自己手里。代价也摆在明面上：后者要维护的东西更多。
# 二、自进化：两层，别混为一谈
“Self-improving”很容易说成玄学。源码里的实现没有那么神秘：一套机制在运行时整理技能和记忆，另一套机制离线读取轨迹、做优化，再走人工审核。先看它们怎么接在一起：
![](/images/posts/2026-07-23-agent-loop-hermes/03.png)
## 第一层：运行时学习闭环（内置）
日常对话中的“学习”，主要发生在后台复盘里。
- 默认每 10 条用户消息，或者单轮累计 10 次工具调用，`_spawn_background_review` 会启动一个 daemon 线程。线程里另起 `review_agent`，用专门的 prompt 回看这段对话，寻找用户纠错、可复用技巧和已经过时的技能。
- 这个 fork 只能使用 memory 和 skill 管理工具，而且设置了 `_persist_disabled=True`。它的复盘过程不会混进用户会话，只能把结果写到技能或记忆存储。
- 发现值得保留的做法后，它会通过 `skill_manage` 创建或局部修改技能，文件放在 `~/.hermes/skills/`。只有后台复盘创建的技能才会标记为 `created_by: agent`；用户在前台主动创建的不会被算进去：
	```python
# tools/skill_manage 内部（简化）
if is_background_review():
    mark_agent_created(name)  # Curator 后续只巡检这些 agent-created 技能
	```
`MEMORY.md` 和 `USER.md` 保存长期事实与用户信息，每轮都会注入，但规则明确要求它不要记录临时任务进度。跨会话回忆走 FTS5 全文检索，再由 LLM 做摘要。
技能写出来之后也不是放着不管。Curator 会定期检查 agent 自建的技能：长期不用的标成 stale，确认废弃的移入归档，内容重叠的尝试合并。它不直接删除技能，这一点我觉得比“自动清理”四个字听起来克制得多。
所以 Hermes 的在线学习更像维护一套会变化的工作笔记，而不是在运行时训练模型。
## 第二层：DSPy + GEPA 离线进化（独立仓库）
另一套机制放在独立仓库 `hermes-agent-self-evolution`，不参与实时对话。它读取执行轨迹，定位失败原因，生成候选修改，最终以 PR 的形式回到主仓库。
这里我很熟悉。在 <mention-page url="https://app.notion.com/p/1699743cc1d04df88143fdebedc3f30d"/> 里，我用 DSPy 把 Skill 中靠手感调整的措辞变成可以评估、回归和重新编译的参数。Hermes 做的是同一类事，只是目标从单个 Skill 扩大到了 prompt、工具描述和其他 agent 组件。
1. 选定目标（某个技能 / prompt 片段 / 工具）
2. 构建评估数据集（LLM 合成 + 挖真实会话历史 + 人工 golden 集）
3. 把目标文本包装成 DSPy 模块，让"指令"变成可学习参数
4. 跑 `dspy.GEPA`（Genetic-Pareto Prompt Evolution）优化，不可用时降级到 MIPROv2
5. 在留出测试集上和 baseline 比
6. **人工审核后**通过 Git PR 合并，绝不热更新到进行中的对话
GEPA 不只接收一个失败分数，还会分析轨迹里的失败原因，再让推理模型提出有针对性的文本变体。候选结果要经过留出测试集，以及 TBLite、TerminalBench2、YC-Bench 等回归检查。整个过程调整的是文本，不是模型权重，因此只需要 API 调用，不需要自己准备 GPU 训练。
# 三、哪些我会抄，哪些不会
我会抄它的分层：前台 loop 只负责把当前任务跑完；后台复盘负责沉淀技能和记忆；更激进的优化放到离线流程里，经过评估和人工审核再合并。这三件事的风险不同，没必要塞进同一个“自进化”开关。
我也会保留 PR + 人审这条边界。让 agent 生成修改不难，难的是阻止一次看似有效的修改悄悄破坏其他任务。Hermes 不在进行中的会话里热更新，这比“能够自动改自己”更值得抄。
我不会照搬它让 LLM 直接维护自然语言 Skill 的方式。至少在 OPc 里，能写成确定性程序的步骤仍然应该写成程序；Skill 更适合负责判断、选择和解释。否则系统用得越久，技能目录越大，问题只会从“模型偶尔不稳定”变成“没人知道它为什么这么做”。
至于自研 loop，我现在的判断也更保守了。Hermes 证明这条路能换来 provider 和平台层面的控制力，但同时也展示了维护成本：重试、fallback、压缩、工具并发、持久化和中断处理，一个都省不掉。是否值得抄，取决于你究竟需要多少控制权。
# 相关阅读 · 内部关联
- <mention-page url="https://app.notion.com/p/75f3e1592f914d7eaf7db5ab235a81cc"/> —— 已发布，Loop Engineering 四件事；本文开头的"为什么这次不选 pi"直接承接它结尾的推荐，发布时必须互引
- <mention-page url="https://app.notion.com/p/1699743cc1d04df88143fdebedc3f30d"/> —— 已发布，把单个 Skill 用 DSPy 重构成可编译模块的实战，和本文第二层直接呼应，发布时可互引
- <mention-page url="https://app.notion.com/p/e18d94f9068d41ae93d0f6f46728ec8e"/> —— 已发布，Skill 系列开篇，"Prompt 负责想、脚本负责做死"的思路可串进系列
- <mention-page url="https://app.notion.com/p/3b1bdbd3c73b49ae9604afc4e18e4641"/> —— 撰写中，Eval-driven 笔记；GEPA 的"打分函数 + 回归门"正是这套思路，两篇可互相引流
- <mention-page url="https://app.notion.com/p/72612009cac74d7d859d97505031cbd9"/>、<mention-page url="https://app.notion.com/p/90b1d7f7695c4795bcff5111c1c4cbef"/> —— 工作区内的 DSPy 基础笔记，润色时可取材
---