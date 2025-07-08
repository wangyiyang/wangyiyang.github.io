---
layout: post
title: 放弃Cursor，我依然选择了Claude断供后的Windsurf
categories: [AI, Programming Tools, Code Generation, Controversial]
description: 逆风而行的选择：为什么在整个科技圈都唱衰Windsurf时，我却坚持认为它比Cursor更强？一个程序员的反潮流宣言
keywords: Cursor, Claude Code, Windsurf, AI编程, 代码生成, GitHub Copilot, MCP
mermaid: false
sequence: false
flow: false
mathjax: false
mindmap: false
mindmap2: false
---


在Claude断供Windsurf服务后，整个开发者社区都在唱衰Windsurf，仿佛它已经是明日黄花。Twitter上、Reddit上、各种技术群里，清一色的声音。

![最近一个月的Cursor使用情况](/images/posts/2025-07-07-cursor-analytics.png)

但是看到上面这张图了吗？这是我最近一个月的Cursor使用情况。各种限制让我活干到一半就"跑路"，结果就是：**Cursor的输出基本为0，钱却一分没少花！**

忍无可忍之下，我直接给Cursor发邮件要求年费退款。既然大家都觉得我的选择有问题，那我就用数据来证明。

**在所有人都在吹捧Cursor的时候，我为什么敢反其道而行？** 因为数据不会说谎！

📉 **之前的组合：Cursor + Claude Code**

- Cursor：200刀/年 ≈ 16刀/月 （贵得离谱，还经常被限制）
- Claude Code：280元/月（国内镜像）
- **总成本：约56刀/月** （花钱买罪受）

🎆 **现在的组合：Claude Code + Windsurf**

- Claude Code：280元/月(国内镜像) （最强的AI编程助手）
- Windsurf：10刀/月 （被众人嘲弃的宝藏）
- **总成本：50刀/月**

🏆 **不仅仅是节约成本6刀/月，更重要的是打破了Cursor的各种限制！**

## 💣 Cursor的“拉地毯”事件：为什么说它毫无诚意？

**这里必须说说最近发生的Cursor“拉地毯”事件。** 如果你还在纠结于Cursor是否值得信任，这个事件就是最好的答案，下面是在社交平台上的一些案例：

- 一个用户发现自己正常能用20-25天的订阅，突然在仅3天内就耗尽了。当他检查使用统计时，**发现只用了…8次请求**。这就是传说中的“无限制”？

- 更让人愤怒的是，Cursor在没有任何提前通知的情况下，将用户从明确的“500次请求”模式，**自动“升级”到“无限制但有速率限制”模式**。听起来像升级，实际上是降级。

- 有Reddit用户报告：**“我被自动添加到新计划（速率限制），我的350个高级请求在20个Claude 4提示中就没了。”**

**候选方案对比：**

- ✅ **Windsurf**：10刀/月
- ✅ **GitHub Copilot**：10刀/月  
- ❌ **Augment Code**：50刀/月（太贵，暂不考虑）

| 📊 对比维度 | 🌊 Windsurf | 🐱 GitHub Copilot |
|------------|-----------|----------------|
| 💰 **价格** | 10刀/月 | 10刀/月 |
| 🤖 **模型** | DeepSeek免费 + Gemini 2.5 + o3 | Claude 4 + GPT 4o + o3 mini |
| 🚫 **限制** | 大文件改写 | 高级模型300次/月 |
| 🎆 **特色** | 浏览器插件 + Workflow | CodeSpace集成 |
| 🏆 **综合评分** | ★★★★★ | ★★★★☆ |

接下来详细分析这两个主要候选者：

## 🌊 Windsurf：性价比之王

**价格：** 10刀/月（早期用户优惠）

🚨 **所谓的“致命弱点”：Claude已断供Windsurf服务！**

在**Claude Code + Windsurf**组合下，这反而成了优势——不用再为两个不同的Claude服务之间的冲突和重复而烦恼！Windsurf只需要做好自己最擅长的事：IDE集成和浏览器插件功能。

### 😈 Cursor的“虚假无限制” vs Windsurf的真实透明

**让我们来看看这两者在透明度上的巨大差异：**

**Cursor的问题：**

- 宣传“无限制”，实际上有“速率限制”
- 后台隐藏的Token算法，用户永远不知道下一次请求会花多少钱

**Windsurf的透明做法：**

- 明确显示你用了多少、还能用多少
- DeepSeek模型完全免费，不用担心“意外消费”
- 没有隐藏成本，没有意外惊喜
- 即使付费模型也有明确的积分消耗（Gemini 2.5 Pro仅需0.75积分/次）

**优点：**

- 🎆 **免费模型太香了**：DeepSeek R1、DeepSeek V3完全免费，Gemini 2.5 Pro仅需0.75积分/次
- 🌐 **浏览器插件黑科技**：可以直接选中网页元素发送到上下文，比截图更准确
- ⚙️ **Workflow自动化**：定义工作流，告别重复劳动

## 🐱 GitHub Copilot

**价格：** 10刀/月，100刀/年

**优点：**

- 🤖 **模型阵容豪华**：
  - 高级模型包含Claude 4
  - GPT 4o和GPT 4.1免费（但个人感觉没DeepSeek香）
  - o3 mini：0.33积分/次
- 🌐 **Web支持全面**：浏览器中可用各种高级模型进行对话和Agent操作
- ☁️ **CodeSpace集成**：云端开发体验更佳

**缺点：**

- 🚫 **高级模型有限额**：每月只有300次
- 🔄 **上下文太短**：经常需要总结，Agent执行速度慢

相比Windsurf，Github Copilot 明显还是有一些差距，所以最终我还是选择了Claude Code + Windsurf的组合。

## 🔧 加餐：必备MCP服务推荐

这套组合拳的最后一块拼图——**MCP服务**，让你的AI助手功能爆表！

**配置除备注：**
📁 Gemini CLI配置文件：`~/.gemini/settings.json`  
🌐 为了最大兼容性，以下MCP服务都使用SSE协议

### 1️⃣ Tavily MCP Server - 免费搜索神器

🎁 **免费额度**：1000次/月（对于个人开发者绝对够用）

配置方法：

Corsor/Windsurf/Gemini CLI：

```json

{
  "mcpServers": {
    "tavily-mcp": {
      "command": "npx",
      "args": ["-y", "tavily-mcp@0.1.4"],
      "env": {
        "TAVILY_API_KEY": "你的Tavily API Key"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

Claude Code:

```bash
claude mcp add-json tavily-mcp '{
      "command": "npx",
      "args": ["-y", "tavily-mcp@0.1.4"],
      "env": {
        "TAVILY_API_KEY": "你的Tavily API Key"
      },
      "disabled": false,
      "autoApprove": []
    }'
```

使用方法：

主要用于Claude Code没有Web搜索功能

```text
请搜索有关 xxx 的信息/用法，来编写xxx
```

### 2️⃣ Context7 - 编程知识库

配置方法：

Cursor/Windsurf/Gemini CLI：

```json

{
  "mcpServers": {
    "context7": {
      "serverUrl": "https://mcp.context7.com/sse"
    }
  }
}
```

Claude Code:

```bash
claude mcp add --transport http context7 https://mcp.context7.com/mcp
```

使用方法：

```text
我们这个服务是使用FastMCP 开发的MCP服务，请开发一个XXX 功能，如果你不清楚请使用 /context7 进行搜索
```

### 3️⃣ DeepWiki - 技术文档助手

配置方法：

Cursor/Windsurf/Gemini CLI：

```json
{
  "mcpServers": {
    "deepwiki": {
      "serverUrl": "https://mcp.deepwiki.com/sse"
    }
  }
}
```

Claude Code:

```bash
claude mcp add -s user -t http deepwiki https://mcp.deepwiki.com/mcp
```

使用方法：

```text
/deepwiki 请参考Dify 的XXX 模块的实现，编写我们项目的XXX模块
```


---

## 💬 写在最后

**如果你也对主流观点有疑问，如果你也想走出自己的路，欢迎留言分享你的“疯狂”选择！**
