---
layout: post
title: "07 | DeepSeek+LangChain——根据数据报表生成带图表的 PPT"
categories: ["DeepSeek", "LangChain", "AI"]
description: "阅读量：481 发布时间：2025-03-07"
keywords: "DeepSeek, LangChain, AI, 07 | DeepSeek+LangChain——根据数据报表生成带图表的 PPT"
mermaid: false
sequence: false
flow: false
mathjax: false
mindmap: false
mindmap2: false
---
阅读量：481 发布时间：2025-03-07

## LangChain Agent 简介

在深入代码实现之前，我们先来了解一下 LangChain Agent 的核心概念和工作原理。

### 什么是 LangChain Agent？

LangChain Agent 是一个智能代理系统，它能够：

1. 理解用户的自然语言指令
2. 规划完成任务所需的步骤
3. 调用适当的工具来执行这些步骤
4. 整合各个步骤的结果

简单来说，Agent 就像是一个智能助手，它知道如何组合使用各种工具来完成复杂任务。

### Agent 的工作流程

1. **输入解析**：Agent 接收用户的自然语言指令
2. **任务规划**：分析需要完成的任务，并制定执行计划
3. **工具选择**：从可用的工具集中选择合适的工具
4. **执行操作**：按照计划调用工具，执行具体操作
5. **结果整合**：将各个步骤的结果组合成最终输出

### Agent 的核心组件

1. **LLM（大语言模型）**
    - 负责理解用户指令
    - 生成执行计划
    - 决策下一步行动
2. **Tools（工具）**
    - 具体功能的实现
    - 通过装饰器注册
    - 提供标准化接口
3. **Memory（记忆）**
    - 存储对话历史
    - 维护状态信息
    - 支持上下文理解
4. **Agent类型**
    - ZERO_SHOT：直接根据工具描述选择工具
    - REACT：使用思维链进行推理
    - PLAN_AND_EXECUTE：先规划再执行
    - 等等

## 主要功能概述

我们将实现以下核心功能：

1. 数据可视化：支持生成多种类型的图表（柱状图、折线图、饼图、散点图）
2. 文件处理：支持读取多种格式的数据文件（CSV、Excel、Word、网页）
3. PPT 生成：支持多种幻灯片布局（标题页、纯文本页、图文混排页）
4. AI 驱动：使用 LangChain 框架实现智能化的内容生成和排版

整体流程图如下：

[](https://alidocs.dingtalk.com/core/api/resources/img/5eecdaf48460cde5395259c01feae4d8567f775afdcdcf7af76d300fc733ea98f3814ce277c0610265a117e969287064f7edb069501d48c2bb2c01956a98dd9ddb9d4fd43f7732e76855cc18ff7ecc591645801b888aab7a07afbbdd4225fe9b?tmpCode=2a476ec9-bf2d-4623-a110-824a173426e5)

## 核心代码实现

### 1. 图表生成器

首先，我们实现了一个灵活的图表生成器类：

```
class ChartGenerator:
    @staticmethod
    def create_chart(data: pd.DataFrame, chart_type: str, x_column: str, y_column: str,
                     title: str, output_path: str) -> str:
        """生成各种类型的图表"""
        plt.figure(figsize=(10, 6))
        if chart_type == "bar":
            sns.barplot(data=data, x=x_column, y=y_column)
        elif chart_type == "line":
            sns.lineplot(data=data, x=x_column, y=y_column)
        elif chart_type == "pie":
            plt.pie(data[y_column], labels=data[x_column], autopct='%1.1f%%')
        elif chart_type == "scatter":
            sns.scatterplot(data=data, x=x_column, y=y_column)
```

这个类使用 matplotlib 和 seaborn 库来生成各种类型的数据可视化图表。特别注意：

- 支持中文显示配置
- 自动化图表样式设置
- 灵活的图表类型选择

### 2. 文件加载工具

为了处理不同格式的输入文件，我们实现了统一的文件加载接口：

```
@tool
def file_loader(file_path: str) -> str:
    """文件加载工具"""
    file_ext = file_path.split('.')[-1].lower()
    if file_ext == 'csv':
        loader = CSVLoader(file_path)
    elif file_ext in ['xls', 'xlsx']:
        loader = UnstructuredExcelLoader(file_path)
    elif file_ext in ['doc', 'docx']:
        loader = Docx2txtLoader(file_path)
    elif file_path.startswith("http"):
        loader = WebBaseLoader(file_path)
```

这个工具的优点是：

- 支持多种文件格式
- 统一的接口设计
- 异常处理机制
- 可扩展性强

### 3. PPT 生成工具

PPT 生成是本项目的核心功能：

```
@tool
def generate_and_save_ppt(ppt_content: List[dict], output_filename: Optional[str] = "generated_ppt.pptx") -> str:
    """生成PPT的工具"""
    prs = Presentation()
    for slide_info in ppt_content:
        slide_type = slide_info["slide_type"]
        if slide_type == "title":
            # 标题页处理
        elif slide_type == "text_only":
            # 纯文本页处理
        elif slide_type == "text_and_image":
            # 图文混排页处理
```

关键特性：

- 支持多种幻灯片布局
- 灵活的内容配置
- 自动化的图片插入
- 统一的样式管理

## 系统集成

使用 LangChain 框架将所有组件整合成一个完整的系统：

```
def create_ppt_agent(llm):
    """创建PPT生成Agent"""
    tools = [generate_chart, generate_and_save_ppt, file_loader]

    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )

    return agent
```

## 实际应用示例

这里我们还是使用第七课的数据做一个 PPT：

```
agent = create_ppt_agent(llm)
result = agent.run({
    "input": """
    使用 /root/work/llm-notebook/data/07/sales_data.csv 文件创建一个销售分析PPT，包括以下内容：
        1. 按月份绘制销售额的折线图
        2. 分析销售额最高的日期
        3. 按产品类别绘制销售额的柱状图
        4. 异常值检测
        5. 趋势分析
        6. 商业建议
        7. 数据的关键特征
        8. 主要统计指标
        9. 潜在的数据模式
        等等
        内容请使用金字塔原理组织。
    """
})
```

执行过程：

```

[1m> Entering new AgentExecutor chain...[0m
[32;1m[1;3mThought: 首先，我需要加载数据文件以了解数据结构和内容，为后续处理步骤做准备。
Action:
```
{
  "action": "file_loader",
  "action_input": {
    "file_path": "/root/work/llm-notebook/data/07/sales_data.csv"
  }
}
```
[0m
Observation: [38;5;200m[1;3mDate: 2024-09-01
Product Name: Product A
Quantity: 15
Unit Price: 45.00

......

Unit Price: 110.00
Sales Amount: 4950.00[0m
Thought:[32;1m[1;3m根据数据内容，我将按以下步骤创建销售分析PPT：
1. 生成按月份绘制销售额的折线图
2. 分析销售额最高的日期并生成相关图表
3. 生成按产品类别绘制销售额的柱状图
4. 进行异常值检测并生成相关图表
5. 进行趋势分析并生成相关图表
6. 根据分析结果提出商业建议
7. 概述数据的关键特征
8. 提供主要统计指标
9. 描述潜在的数据模式

首先，我将生成按月份绘制销售额的折线图。
Action:
```
{
  "action": "generate_chart",
  "action_input": {
    "data_path": "/root/work/llm-notebook/data/07/sales_data.csv",
    "chart_type": "line",
    "x_column": "Date",
    "y_column": "Sales Amount",
    "title": "Monthly Sales Amount",
    "output_path": "monthly_sales.png"
  }
}
```[0m
Observation: [36;1m[1;3mmonthly_sales.png[0m

......

      {
        "slide_type": "text_only",
        "title": "潜在的数据模式",
        "content": [
          "1. 销售额在周末和节假日通常较高。",
          "2. 某些产品类别在特定时间段内表现更好。",
          "3. 销售额与促销活动呈正相关。",
          "4. 某些日期的销售额异常高，需要进一步调查。"
        ]
      }
    ],
    "output_filename": "sales_analysis.pptx"
  }
}
```[0m
Observation: [33;1m[1;3msales_analysis.pptx[0m
Thought:[32;1m[1;3mI know what to respond
Action:
```
{
  "action": "Final Answer",
  "action_input": "销售分析PPT已成功生成，文件路径为：sales_analysis.pptx。"
}
```[0m

[1m> Finished chain.[0m
PPT已生成: 销售分析PPT已成功生成，文件路径为：sales_analysis.pptx。

```

生成的 PPT 内容如下：

## 总结：

本文介绍的自动化 PPT 生成系统具有以下特点：

1. 对比市面上的 PPT 自动生成工具，我们支持全自动的数据处理和可视化
2. 智能化的内容生成和排版
3. 灵活的配置和扩展能力
4. 专业的展示效果

当然我们这里仅仅实现了一个 Demo，有很多复杂的配置我们为了让大家能够看清主脉络并没有实现，有兴趣的同学可以继续完善一下，来帮助自己工作，我们也希望能够看到有更多的业务能够被大模型赋能。
