---
layout: post
title: "使用Claude Code 开发一个图表分析MCP Server[MCP开发入门04]"
categories: [MCP, AI, Claude Code, Data Visualization]
description: "通过实战案例，展示如何利用Claude Code和FastMCP，快速开发一个支持柱状图、饼图、折线图的智能图表分析MCP服务器。"
keywords: MCP, Claude Code, FastMCP, Pyecharts, AI开发, 数据可视化
mermaid: true
sequence: false
flow: false
mathjax: false
mindmap: false
mindmap2: false
---

今天趁着周末，来实现一个图表分析的MCP工具。一个多月前，这个MCP Server在我们公司内部我已经使用 Gemini CLI实现了一套，支持了pyecharts 中16种常用的图表类型。因为这个工具还是非常实用的，今天我们使用Claude Code 再实现一遍，一来可以让大家直观的感受一下Claude Code的能力, 而来也算是MCP 开发的一次最佳实践,受限于篇幅我们在本文仅实现了柱状图、饼图、线状图， 其他的实现也是类似的套路。最后我们的全部代码以及所有Claude Code 的交互我都已经上传到了Github。

我们这个小项目主要使用到的依赖：FastMCP、pyecharts、MinIO、Dynaconf、loguru 等。

主要的开发工具：

- Claude Code + Context7
- Windsurf：主要用于 Code Review，不参与开发

测试的MCP Client: Cherry Studio

开发过程：

- 使用 Claude Code 安装 Context7 MCP Server
- 使用 Claude Code Plan 模式将项目的基本需求进行输入
- 使用 Claude Code 进行代码编写和调试
- 在 Cherry Studio 中集成编写好的 MCP

## Claude Code 安装 Context7 MCP Server

因为 Claude sonnet 4 发布的时候FastMCP 的资料还是非常少，另外FastMCP 的更新还是非常快的，我们使用 Context7 可以获得各个依赖的最近的文档。

**安装命令**

```bash
claude mcp add --transport http context7 https://mcp.context7.com/mcp
# Added HTTP MCP server context7 with URL: https://mcp.context7.com/mcp to local config
# File modified: /Users/wangyiyang/.claude.json [project: XXXX]
```

**检查是否安装成功**

```bash
claude mcp list                                                      
# Checking MCP server health...

# context7: https://mcp.context7.com/mcp (HTTP) - ✓ Connected
```

### 开发前准备

**创建项目目录**

```bash
mkdir charts_mcp_server
cd charts_mcp_server

claude
```

![alt text](/images/posts/2025-08-17-mcp-dev-intro-04/image.png)

### 需求分析

使用 `shift`+`tab` 切换到 Claude Code 的Plan 模式，如上图，输入下面的Prompt:

```text
我们使用FastMCP（HTTP Transport）、pyecharts实现一个MCP Server, 大模型通过加工用户输入的信息，传入的图表类型调用我们不同的 MCP 工具来生成不同的图表，返回图表的URL。我们现在需要支持柱状图、饼图、折线图。我们的流程：

1. 大模型调用MCP 某个图形生成工具，传入响应的参数
2. Pyecharts 根据参数生成图表并渲染成html, 保存到临时文件夹
3. 将html文件渲染或通过一些工具截图生成图片（请注意如果使用截图注意截图的尺寸， 不要截取的不完整也不能过度留白）
4. 将生成的图片上传到MinIO并返回URL

如果你不清楚 FastMCP、pyecharts 如何使用，请使用/context7 进行文档搜索

另外：

- 配置文件我们使用Dynaconf 进行管理
- 日志我们使用loguru
```

在 Claude Code 执行过程中，我们可能会遇到一些提示，询问我们是否执行指令或者执行修改，这种情况下我一般选择第二个（在本项目或本次会话默认是直接执行）

![alt text](/images/posts/2025-08-17-mcp-dev-intro-04/image-1.png)

大概过了2-3分钟，Claude Code 完成了初步的设计以及开发计划，如下图。这里我们一样选择第二个，如果觉得它的计划不够完善，我们选择第三个`No. keep planning`。

![alt text](/images/posts/2025-08-17-mcp-dev-intro-04/image-2.png)

![alt text](/images/posts/2025-08-17-mcp-dev-intro-04/image-3.png)

之后Claude Code 进入了开发阶段，并且给出了一个Task List逐步执行，如下图。

![alt text](/images/posts/2025-08-17-mcp-dev-intro-04/image-4.png)

大概过了10分钟，Claude Code 完成了初步的开发工作。下图是Claude Code 生成的代码结构, 以及总结。

![alt text](/images/posts/2025-08-17-mcp-dev-intro-04/image-5.png)

![alt text](/images/posts/2025-08-17-mcp-dev-intro-04/image-6.png)

到此 我们一条指令执行了12分钟，完成了初步的开发,如果计算官方成本大概$20,但是在我使用的镜像站，成本$1.86 折合RMB 0.93(没有算错，前一段搞活动充一送一， 细节可以私信我)
![alt text](/images/posts/2025-08-17-mcp-dev-intro-04/image-7.png)
![alt text](/images/posts/2025-08-17-mcp-dev-intro-04/image-8.png)

接下来我们执行 `/init`，生成 `CLAUDE.md` 文件，让后续的开发更加顺利。接着我们执行`/clear`开启一个新的对话，避免上下文过大，减少后面的使用成本。

既然是vibe coding，我们尽可能的使用Claude Code 执行我们的想法。

接下来我们执行下面 Prompt 创建我们的虚拟环境:

```text
Input: 请创建一个虚拟环境，并安装相关依赖

Output:
#  Update Todos
#  ⎿ ☒ 创建Python虚拟环境                    
#     ☒ 激活虚拟环境并安装requirements.txt依赖
#     ☒ 安装Playwright浏览器
#
# ⏺ 虚拟环境创建完成！已成功：
# 
#   1. ✅ 创建了名为 charts_env 的Python虚拟环境
#   2. ✅ 安装了 requirements.txt 中的所有依赖包，包括：
#     - fastmcp (2.11.2) - MCP服务器框架
#     - pyecharts (2.0.8) - 图表生成库
#     - minio (7.2.16) - 对象存储客户端
#     - playwright (1.54.0) - 浏览器自动化
#     - 以及其他相关依赖
#   3. ✅ 安装了Playwright的Chromium浏览器（用于截图功能）
# 
#   现在可以使用以下命令激活虚拟环境并启动服务器：
#
#   source charts_env/bin/activate
#   python main.py
#
#   记得先在 config/.secrets.toml 文件中配置MinIO认证信息。
```

使用Docker 启动一个minio, 并且修改我们的配置文件

```text

Input:让我们在本地使用docker启动minio 并将相关信息写入config/.secrets.toml

Output:
  Update Todos
  ⎿  ☒ 启动MinIO Docker容器            
     ☒ 获取MinIO连接信息
     ☒ 创建config/.secrets.toml配置文件

⏺ 完成！我已经成功启动了本地MinIO Docker容器并配置了相关信息：

  已完成的配置

  MinIO容器信息：
  - 容器名称：minio-charts
  - API端口：9000 (对象存储API)
  - 控制台端口：9001 (Web管理界面)
  - 访问密钥：minioadmin
  - 秘密密钥：minioadmin123

  配置文件更新：
  - 已更新 config/.secrets.toml 文件中的MinIO凭证
  - 密码已设置为与容器一致的 minioadmin123

  访问地址：
  - MinIO API: http://localhost:9000
  - MinIO控制台: http://localhost:9001
  - 用户名/密码: minioadmin / minioadmin123

  现在你可以使用 python main.py 启动MCP服务器，它将自动连接到本地MinIO实例进行图表存储。
  ```

当然直接运行还是遇到了一些问题，最后直接把遇到的问题复制粘贴给 Claude Code 也是完美解决，这里就不做过多描述，接着我们运行我们的MCP Server:

![alt text](/images/posts/2025-08-17-mcp-dev-intro-04/image-13.png)

最后我们在Cherry Studio中集成编写好的 MCP:

![alt text](/images/posts/2025-08-17-mcp-dev-intro-04/image-9.png)

最后我们进行验证：

![alt text](/images/posts/2025-08-17-mcp-dev-intro-04/image-12.png)
![alt text](/images/posts/2025-08-17-mcp-dev-intro-04/image-10.png)

最后的成本也在40刀左右（实际花费2元）。

**完整的代码实现已上传至GitHub，[mcp-quickstart-guide](https://github.com/wangyiyang/mcp-quickstart-guide)包含详细Claude Code 交互。如果喜欢这篇文章的话，请推荐给身边的朋友们。**
