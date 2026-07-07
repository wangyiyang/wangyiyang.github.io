---
layout: post
title: Agent Loop 的文章好写
categories: [AI Agent]
description: Agent Loop 的代码只有 20 行，但它的「高级感」不在循环本身，而在循环外面的四道工程题：三层嵌套结构（工具环/主环/任务环）、每一圈的上下文重排、可验证的停机条件、循环里的人（HITL）。把这四件事拆清楚，就能解释为什么同一个 while 循环，有人跑出生产级 Agent，有人跑出无限烧钱机器。Loop Engineering 正在成为下一个 Prompt Engineering。
keywords: AI Agent, Loop Engineering, Agent Loop, Prompt Engineering, 停机条件, HITL, 上下文管理
mermaid: false
sequence: false
flow: false
mathjax: false
mindmap: false
mindmap2: false
---

诶，我写「Agent Loop 就是感知-决策-行动闭环」那种文章，说实话，分分钟写出来。不用一星期，三天。都不用三天，让模型生成，半小时。画一个圈，标四个箭头——Perceive、Think、Act、Observe——再配一句「未来已来」。好写，太好写了。
为什么我不写？爺们儿要脸。

![](/images/posts/2026-07-08-agent-loop/01.png)

要脸的写法，得回答那个圈回答不了的问题：同样一个循环，凭什么有人跑出生产级 Agent，有人跑出一台无限烧钱机器。下面开拆。

## 一段让人不敢相信的源码

我第一次把 Pi 拆开看源码的时候，愣了很久。

每天替我烧几亿 token、跑得又快又稳的那个 Coding Agent，核心就是一个 while 循环：拼上下文，调一次模型，模型说要用工具就执行工具、把结果塞回去，再转一圈，直到它自己说「我干完了」。没有调度器，没有状态机，没有消息总线。就这么点东西。

觉得 20 行已经够极端了？还有更狠的。2025 年底，澳大利亚一个养羊的老哥 Geoffrey Huntley，在铲羊粪的间隙写了五行 Bash：

```bash
while :; do cat PROMPT.md | claude -p; done
```

没有 SDK，没有框架，连 Python 都没有。把提示词文件塞给 claude，跑完再塞一遍，无限循环——错了也不要紧，上一圈的烂摊子会原封不动地喂给下一圈，磨到对为止。就这么个被命名为「Ralph Wiggum」的傻子循环（典出《辛普森一家》里那个吃浆糊的小孩），火遍了硬佩克斯的硬盘和硅谷的时间线，最后逼得 Claude Code 官方把它包装成了内置插件。梗归梗，它验证了一件严肃的事：**循环本身就是生产力。哪怕模型每一圈都可能犯错，只要失败被喂回下一圈，笨办法也能磨出正确答案。**

所以后来我发现这不是 Pi 偷懒，也不是羊农胡闹，而是整个行业的共识。Anthropic 给 Agent 的定义干脆得近乎粗暴：**LLMs autonomously using tools in a loop**——模型在循环里自主地用工具。ReAct 论文 2022 年把这个模式定下来之后，你今天能叫得上名字的 Agent，Claude Code、Codex、Cursor，骨架全是它。

讲到这我想起我在生产里撞见的第一个 Loop，比这些都土。最早那版 LangChain 的 Agent，连循环的「协议」都是用 Prompt 写的：模板里教模型按 `Thought:`（想）→ `Action:`（选工具）→ `Action Input:`（填参数）的格式吐字，框架拿正则把 Action 抠出来、执行工具，再把结果以 `Observation:` 开头拼回 Prompt，让模型接着想；直到模型吐出 `Final Answer:` 这个字符串——对，停机条件就是一次字符串匹配——循环结束。那时候模型还没有原生 function calling，整个 Agent Loop 就是文本生成 + 正则解析 + 字符串拼接，分隔符是几个大写英文单词。后来的一切——function calling、tool schema、middleware——只是把这套字符串约定升级成了结构化接口，循环的形状从第一天起就没变过。

于是问题来了：如果核心真的只有 20 行，那 Agent 工程师到底在忙什么？

先把结论摆这：**大家都在说的 Agent Loop，本身真没什么了不起的。** 它不神秘、不高级，一说就明白——从当年 LangChain 的 Prompt 模板到今天的 Claude Code，它一直就是那个转圈。真正花功夫的，全在循环外面。

## 根本原理

先把那 20 行摆出来：

```python
def agent_loop(task: str) -> str:
    context = [system_prompt, task]
    while True:
        response = llm(context, tools=tools)
        if response.tool_calls:
            for call in response.tool_calls:
                result = execute(call)      # 行动
                context.append(result)      # 观察
        else:
            return response.text            # 模型自认完成
```

推理 → 行动 → 观察，转圈直到收工，这就是 Agent Loop 的全部。剩下的根本原理，一段话讲完：workflow 和 agent 的区别只在控制流握在谁手里，workflow 把每一步提前写死，agent 把方向盘交给模型——这既是它的全部威力，也是所有麻烦的总根源。方向盘交出去之后，功夫全在循环外面。看清它其实在三层转圈：最里面是单次工具调用，越「无聊」越好；中间是那 20 行，模型掌舵，智能和失控都在这层；最外面是任务级验收，「真的干完了」的钥匙在你手里——排障时先分清病在哪层，别混在一层里治。管好每一圈的上下文：模型本身无状态，每圈的全部认知就是你拼给它的那坨 token，只进不出的上下文会让 Agent 安静地变蠢，无非压缩、外存、交接三招，prompt 管第一圈，context 管之后的每一圈。定好它凭什么停：「模型自己觉得干完了」是最弱的一档，真正的分水岭是可验证的成功标准——我在 AGENTS.md 里写「目标驱动执行」时讲过，与其说「修个 bug」，不如说「先写一个能复现的测试，再让它变绿」，把停机条件从自由心证升级成机器可判定的谓词，再配上圈数和预算的保险丝，否则账单会替你复习什么叫指数增长。最后给人留个位置：高危操作在执行前拦下，中途能插话，拒绝的原因塞回上下文让它重新想——工具喂环境的反馈，验证器喂标准的反馈，人喂意图的反馈，三种反馈进同一个上下文，驱动同一个循环。

## Loop Engineering，下一个 Prompt Engineering

回到开头的问题：核心只有 20 行，Agent 工程师在忙什么？

现在可以完整地回答了。他们在给三层循环划边界（结构）、在管理每一圈的上下文（状态）、在把停机条件从心证变成谓词（验收）、在给人留刹车和方向盘（协同）。这四件事有个越来越常见的名字：**Loop Engineering**。

我越来越相信，它会走一遍 Prompt Engineering 走过的路：从「这也算工程？」的嘲笑开始，到人人都得会的基本功结束。区别在于，prompt 调的是模型的一次输出，loop 调的是模型和环境之间的整个反馈系统——后者才是 Agent 从 Demo 走到生产的那道坎。

上一篇 Harness 的缘起，是我一位 Z 姓同事的一句话：「师父，你是否可以把你的 Harness 给我。」这一篇写完，我想把当时没来得及说的半句补上：千万别被这些新词吓到——Skill、Harness、Agent Loop，一年能冒出十几个，听着一个比一个玄。你只需要记住一件底层的事：**大模型的全称是大「语言」模型，不是大「数学」模型。** 它的天赋是听懂你的语言、从你的话里判断该调用什么；但你让它自己推算「下周三是几号」去约日程、替你对账算钱（别问我是怎么知道的），它就可能一本正经地踩坑。想通这一层，所有新概念都只是同一句话的注脚：循环里那个 execute()，是把日历、计算、检索这些不该靠「想」的活交给工具；Harness，是把不该现场发挥的步骤写死；停机条件，是别让它自己给自己验收。**让语言模型只干语言的活，剩下的都交给循环里的确定性。**

写 Harness 系列的时候我说过：工具焊死的那层（agent loop、bash、沙箱）你改不动，你能拧的是 AGENTS.md 那层。这篇算是把「焊死的那层」拆开给你看了——看完你会发现一件微妙的事：**焊死的是循环的形状，但循环里流动的每一样东西——上下文怎么排、什么时候停、人在哪介入——都还是你能拧、也必须拧的。**

最简单的代码，配上最认真的工程，这就是 Agent Loop 的全部秘密。

> 一个 while 循环人人会写。知道它在哪三层转、每圈喂什么、凭什么停、人坐哪——这四件事，才是你带得走的。

## 最后，一个推荐

如果你真要动手开发一个带 Agent Loop 的项目，别急着从零手搓，也别一头扎进重型框架——去学学 OpenClaw：这个能清邮箱、管日程的开源个人助理，把 Pi Agent 直接当作自己的 Core。Pi 的作风和本文的论点一脉相承：系统提示词是所有 Agent 里最短的，工具只有四个（Read、Write、Edit、Bash），循环极简，复杂度全部交给扩展系统去长。OpenClaw 拿它当内核，等于给你现场演示了一遍「最简单的循环 + 最认真的工程」在真实产品里长什么样。把这两个仓库（openclaw/openclaw 和 badlogic/pi-mono）丢进 DeepWiki 逛一圈，比读十篇「一文读懂 AI Agent」有用。

![推理 → 行动 → 观察，人在循环里](/images/posts/2026-07-08-agent-loop/02.png)
