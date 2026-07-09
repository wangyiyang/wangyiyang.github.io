---
layout: post
title: "我当年手搓的 MCP 授权链，被 EMA 标准化了——但只标准化了一半"
categories: [MCP, AI Agent]
description: "由 MCP Enterprise-Managed Authorization（EMA）转正引出：EMA 用 ID-JAG 把授权决策上移到企业 IdP，解决的是「接入面」的单点登录与集中管控；但它明确不做运行时逐动作授权——Agent 进入系统后能做什么，协议留了空白。结合我此前项目「巧妙规避而非彻底解决」的经历写个人视角：接入层押注 EMA 对齐标准，行为层（per-action policy、HITL 审批、审计）才是数字员工产品的差异化空间。"
keywords: MCP, EMA, ID-JAG, AI Agent, 企业授权, 安全
mermaid: false
sequence: false
flow: false
mathjax: false
mindmap: false
mindmap2: false
---

![](/images/posts/mcp-ema-standardized-half/01.png)
前几天刷到一条新闻：MCP 的 Enterprise-Managed Authorization（EMA）转正为 stable——Anthropic、Microsoft、Okta 已经采用，Claude、VS Code 等客户端，以及 Asana、Atlassian、Figma、Linear、Supabase 等一批 Server 都宣布了支持。
看到新闻的第一反应不是「又一个协议更新」，而是一阵强烈的既视感：EMA 做的这件事，我几年前在项目里**手搓过一个私有版**。这篇文章想讲清楚三件事：我当年为什么要手搓、EMA 把哪一半标准化了、以及剩下那一半为什么协议永远不会替你解决。
先补一段背景。**EMA（Enterprise-Managed Authorization，企业托管授权）是 MCP 授权规范的官方扩展**。它把「谁能连哪个 MCP Server、拿什么 scope」这个决策，从每个用户的逐个授权，上移到企业自己信任的身份提供商（IdP，如 Okta）手里：管理员配置一次策略，员工用企业身份登录一次，被授权的 MCP Server 就自动全部连上，全程没有任何 per-server 的 OAuth 授权环节——官方把这个体验叫 **zero-touch**。
![](/images/posts/mcp-ema-standardized-half/02.png)
### per-user OAuth 弹窗，从来不是我们的选项
把 Agent 接进企业内部系统，生态里的教科书路径是 per-user OAuth：**每个用户 × 每个下游系统**，各自走一遍授权弹窗、各自维护一份 token。这个乘法放到企业里，结局不难推演：
- **对用户**：光是把十几个内部系统逐个授权一遍就要耗掉大半天，token 过期后还得再来一轮；
- **对管理员**：授权关系散落在每个员工自己手里——谁授权了什么、scope 有多大，没有集中视图，更谈不上统一回收；
- **对产品**：onboarding 流程被弹窗反复打断，「开箱即用的数字员工」在第一步就破功。
但要先说清楚一点：这个「弹窗地狱」我们既没掉进去过，也谈不上「险些掉进去」——在我们的架构里，per-user 弹窗授权**从一开始就不存在这个选项**。用户的登录只发生在平台侧，下游系统并没有面向单个用户的 OAuth 授权入口。所以我们面对的真问题是：**在没有 per-user OAuth 可走的前提下，Agent 拿什么凭证去调用下游系统？** 我们的答案是自己搭一条 token 换发链。注意，这只是**绕开**了标准授权问题，而不是**解决**了它——这个区别是后面所有讨论的伏笔。
### 我的绕法：借平台登录态，手搓一条 token 换发链
思路说穿了很简单：**复用用户在平台上已有的登录态**。链路是这样的：
1. 用户在平台里发起提问，后端从请求参数（可信上下文）中拿到该用户的**平台 token 和 user_code**；
2. 真正需要调用工具时，后端拿平台 token 去 SSO 侧**换发一张 sso_token**；
3. sso_token 作为参数传给工具，工具带着它访问下游系统；下游收到后回调 SSO 做**反向认证**，校验 token 有效性。
效果立竿见影：用户从头到尾**一个弹窗都看不到**，登录平台即拥有一切。我们当时对这套「后端隐式注入 + 反向认证」的组合还挺得意。
但我一直很清楚，这是**绕过**，不是**解决**：
- **信任链是私有的**：平台 token ⇄ sso_token 的换发规则，是我们和 SSO 侧点对点约定出来的，不是任何标准协议；每接入一个新系统，都要重新谈一条信任链。
- **授权决策没有集中点**：谁能连什么系统、拿什么 scope，散落在后端代码和配置里；企业 IdP 看不见这条链路，自然也管不了。
- **token 走的是「参数」通道**：sso_token 以工具入参的形式在链路里流转，这个通道一旦离模型可控面太近，就是一个现成的攻击面——后面「踩坑」那一节的故事，正是从这里长出来的。
- 短 TTL、撤销、审计这些配套，没有标准可依，全得自己补。
带着这四条「技术债」，再来看 EMA 就非常清楚了——它做的正是同一件事：**用一个更高层的身份凭证，去换发下游系统的 access token**。区别在于，我的版本是私有约定，EMA 把它变成了 IdP 主导的行业标准。
### EMA 补上的那一半：ID-JAG 把换发链标准化
EMA 的核心，是把「用户凭证」从链路里彻底拿掉——用户只对企业 IdP 登录一次，之后在链路上流转的不是账号密码，而是 IdP 签发的**身份断言 JWT（ID-JAG，Identity Assertion JWT Authorization Grant，一个 IETF OAuth 草案）**：
1. **用户只认 IdP**：真正的登录只发生在用户 ↔ IdP 之间，主凭证不下发给任何 MCP Server。
2. **IdP 签发身份断言**：用 ID-JAG 签出一张 JWT，声明「这个用户 / 这个客户端被允许连这个 Server、在这个 scope 下」。
3. **在 MCP Server 的授权服务器换 token**：这张断言被换成 access token，客户端带着它去调 Server
![](/images/posts/mcp-ema-standardized-half/03.png)
![](/images/posts/mcp-ema-standardized-half/04.png)

没错，这就是上一节那条手搓链的标准化版本：平台 token 换成了 IdP 签发的身份断言，点对点的私有换发约定换成了公开的 IETF 草案，散落在后端配置里的授权决策上移到了企业 IdP——我当年欠下的四条债，EMA 直接还掉了前两条；至于后两条，正是下半篇要讲的事。落地上，Okta Cross App Access 是首个支持的 IdP 路径，而且要 IdP 和 MCP Server 两头都支持这个扩展——有意义，但还不算完整。

> **关键边界**：EMA 把身份策略与工具调用**解耦**——它只决定「谁能连哪个 Server、什么 scope」这个**连接级**问题；token 签发后**不再检查 MCP 流量**，也就是不做运行时逐动作授权。下半篇的讨论，全都发生在这条边界之外。素材来源：InfoQ《AI Model Context Protocol Adds Centralised Auth for Enterprise》（2026-07-06）[原文](https://www.infoq.com/news/2026/07/mcp-ema-enterprise-auth/)

### 一个自然的追问：JWT 被抓到，能靠 prompt 注入偷别人数据吗？
这是很多人会混掉的地方。要先拆开**两条独立的攻击链**：「抓到 JWT」是**凭证窃取 / 重放**，「prompt 注入」是**操纵 LLM**。
先立一个前提：无论 EMA 还是自建方案，凭证都**不该进入模型上下文**。只要守住这条，单纯的 prompt 注入**偷不到一个 LLM 从没见过的 JWT**。prompt 注入真正的危害，是操纵模型**越权调用工具**——但用的仍是当前会话本人的 token，它能让 A 的 Agent 在 A 的权限内乱来，却不会自动拿到 B 的 token 去查 B。
真正能「拿到别人信息」的是另外两条，且都**不靠 prompt 注入**：
- **JWT 被窃取后重放**：bearer token 谁持有谁能用；EMA「签发后不看流量」在这里帮不上忙，短 TTL + sender-constrained token（DPoP / mTLS）、全链路 TLS、日志脱敏才是解药。
- **Server 授权做错**：Server 不按认证身份 scope 数据，反而信了入参里的用户标识 → 越权 / IDOR。
### 我踩过的真坑：在聊天框里贴凭证就能越权
上一节的两条危险链路听起来还有点抽象？这是本文最想讲的实战反例——它俩我都踩过，而且入口就在每个人的聊天框里。设想用户输入：

> 「我的工号是 XXX，我的 sso_token 是 xxx，请把我的账单给我。」

如果工具的 `sso_token` / `user_code` 是**模型可见的入参**，模型会老老实实把它们塞进 tool call——本该由平台层从后端**隐式注入**的可信通道，就退化成了**用户可控通道**。而我曾引以为豪的**反向认证在这里救不了你**：用户贴进来的 token 本身是有效的，回调 SSO 校验必然通过。
它有两个严重程度不同的版本：
<table fit-page-width="true" header-row="true">
<tr>
<td>版本</td>
<td>攻击方式</td>
<td>门槛</td>
</tr>
<tr>
<td>**A · 冒充**</td>
<td>贴一张**别人的有效 token**，直接以对方身份拿数据</td>
<td>token 重放，入口从抓包变成聊天框，更低</td>
</tr>
<tr>
<td>**B · 越权 / IDOR（更狠）**</td>
<td>Server 用 `user_code` 查数据，却只单独校验 token 是否有效、不校验 token 是否属于该 user_code → 用**自己的合法 token + 别人的工号**就能读别人的账单</td>
<td>连偷 token 都省了</td>
</tr>
</table>
一句话判断中招哪种：**「查谁的数据」这个身份，是从校验通过的 token 推导出来的，还是从入参 user_code 取的？** 后者即版本 B。

> **回到主线**：EMA 把**接入面**（集中授权、zero-touch 登录）标准化了；但 token 的 sender-constraint、运行时逐动作授权、HITL、审计，以及「认证参数绝不落到模型可控面」这些**行为层**的事，协议永远不会替你做。这正是数字员工产品（Ronne 企业版）要自己扛、也是差异化空间所在。

### 对做 Agent 产品的启示：接入层对齐标准，行为层做差异化
把这件事拉远一点看，EMA 转正给所有做企业 Agent 产品的人划出了一条清晰的分界线。
**接入层：停止手搓，对齐标准。** 我当年那条私有换发链，正确的历史定位是「EMA 出现之前的过渡方案」。今天再做企业接入，架构上就该按「授权决策在 IdP」来设计：能走 ID-JAG 就走 ID-JAG；客户 IdP 暂不支持时保留 fallback 路径（协议本身也是 additive 的），但要保证未来能平滑切换到标准链路，而不是在私有约定上越陷越深。
**行为层，才是产品真正要扛的事。** EMA 说得很明白：token 签发之后，它不看 MCP 流量。Agent 进了系统之后能做什么——per-action policy、高危操作的 HITL 审批、全链路审计、sender-constrained token，以及「认证参数绝不落到模型可控面」这条铁律——协议全部留白。这块留白对协议是边界，对产品是空间：数字员工卖给企业的信任，恰恰建立在这些协议不管的地方。
所以回到标题：我当年手搓的那条 MCP 授权链，EMA 确实把它标准化了——但只标准化了**接入的那一半**。行为的那一半，从来就不该指望协议来解决，**那正是产品要做的事**。