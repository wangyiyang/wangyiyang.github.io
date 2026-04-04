---
layout: post
title: "GLM/Qwen/Kimi/Kiro 平替挑战失败记"
categories: ["AI-Coding", "LLM", "Tooling"]
description: "当开源模型以“免费”、“国产”、“高性能”刷屏时，我尝试用 GLM 4.5、Qwen3 Coder、Kimi K2 平替 Claude Code。24 小时后，我默默续费了账单。省米虽好，但效率和时间更贵。"
keywords: "AI-Coding, LLM, Tooling, GLM, Qwen, Kimi, Kiro, GLM/Qwen/Kimi/Kiro 平替挑战失败记"
mermaid: false
sequence: false
flow: false
mathjax: false
mindmap: false
mindmap2: false
---
![alt text](/images/posts/2025-08-08-llm-coding-alternatives-failed/image.png)

**——Claude Code 为何仍是编程战场的“实战王者”**

当开源模型以“免费”、“国产”、“高性能”刷屏时，我尝试用 GLM 4.5、Qwen3 Coder、Kimi K2 平替 Claude Code。24 小时后，我默默续费了账单。**省米虽好，但效率和时间更贵**。

**先说结论：Claude Code** > **GLM 4.5 + CC > Kimi K2 +CC >Qwen3 Coder +CC > Kiro**

1. **GLM 4.5：企业合规的“优等生”**
    - **强项**：
        - 三个模型当中参数量最小的，效果也是最好的，不管是私有化部署还是使用API 性价比比较高，如果有企业合规的编码需求建议部署GLM  4.5。
    - **致命伤**：
        - 长会话失忆症：连续交互超 10 轮对话后，逻辑连贯性骤降，需手动重启对话。
2. **Kimi K2：50元门票的“谜之判官”**
    - **高光宣传**：“超越 Claude 的深度思考者”；
    - **翻车实录**：
        - 批改小学数学题时，**44÷2=22 被判错**，反馈“正确答案应为 22”；
        - 被曝依赖模糊数据库匹配，**逻辑稳定性成谜**
3. **Qwen3-Coder：免费的“闲暇玩具”**
    - 优点：
        - 阿里豪送 **1000 万 tokens**，可以简单测试一下下，如果项目较大半小时烧光
    - **劝退点**：
        - 实测效果大跌眼镜
4. **Kiro：**一个大家现在有些已经用到的或者还在等待的神奇IDE，因为被自媒体的“**定向爆破”**，基本上现在是一个不可用的状态，响应时间长，甚至还会失败，在它刚发布的时候用了一下，实战上属于Cusor 和 Windsurf的平替，。
