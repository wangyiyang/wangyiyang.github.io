---
layout: post
title: "我把一个 Skill 从手写 Prompt 重构成了可编译模块——一次 DSPy 实战复盘"
date: 2026-06-12 08:00:00 +0800
categories: ["AI", "AI Agent"]
description: "手写 Prompt 的 Skill 一换模型就翻车，根因是我把措辞当源代码硬编码了。这篇复盘用 DSPy 重构的全过程：只声明契约和打分函数，措辞交给编译器自动生成；换模型重新 compile 一次，当初翻车的 case 全部跑通。"
keywords: "我把一个 Skill 从手写 Prompt 重构成了可编译模"
mermaid: false
sequence: false
flow: false
mathjax: false
mindmap: false
mindmap2: false
permalink: /2026/06/12/我把一个-Skill-从手写-Prompt-重构成了可编译模块-一次-DSPy-实战复盘/
---


![手写 Prompt 重构为 DSPy 可编译模块的封面对比图](/images/posts/2026-06-12-我把一个-Skill-从手写-Prompt-重构成了可编译模块-一次-DSPy-实战复盘/我把一个-Skill-从手写-Prompt-重构成了可编译模块-一次-DSPy-实战复盘_001.png)
> **TL;DR**
> - 手写 Prompt 的 Skill 一换模型就翻车，根因是我把「对某个模型有效的措辞」当成源代码硬编码了；
> - 我用 DSPy 重构：只声明输入输出契约和一个打分函数，措辞交给编译器在评测集上自动生成、自动优化，两百行 YAML 变成四十行 Python；
> - 重新 `compile` 之后，当初在小模型上翻车的 case 全部跑通——换模型从「几乎重写一遍」变成「改一行、重编译一次」；
> - 文末有这套做法的代价和不适用场景。它不是银弹，一次性任务上它就是过度工程。
上个月我干了件后来挺后悔、但收获也最大的事：我把一个已经在生产里跑得好好的 Skill，亲手拆了重写。
起因很蠢——我那个给某前端官网项目用的代码审查 Skill，在 Claude Code 上调了大半天、效果拔群；结果我想省点钱，把底模换成一个开源小模型，同一段 Prompt，输出直接稀碎：该报的 P0 漏报、表格格式崩了、还开始自由发挥写"建议你多喝热水"式的废话。
那一刻我才反应过来：我引以为豪的那两百行 Prompt，根本不是代码，是一堆只对 Opus 这一个模型有效的咒语。模型一换，咒语失灵。
这篇就是那次重构的复盘：我怎么用 DSPy 把咒语变回代码，重构完到底跑没跑通，以及什么场景下你根本不该学我。
## 一、先看看翻车现场：手写 Prompt 的 Skill 长什么样
我原来的 `web.code-review` Skill，本质是一坨结构化的手写 Prompt（我之前还挺得意地把它做成了 DSL 模板）：
```yaml
id: web.code-review
version: 1.2.0
model: claude-opus
role: 你是一名有十年经验的资深前端架构师，精通 Vue3 / TypeScript
context: |
  这段代码来自 某官网项目二期，团队强调可维护性与可访问性。
  审查时请假设读者是中级工程师。
task: 审查下面这段 diff，定位可维护性与性能问题
constraints:
  - 只报 P0 / P1 级别的问题，不要报风格偏好
  - 每条问题必须给出「最小可落地」的改法
  - 不要复述代码，不要写客套话
reasoning: 请先一步步分析每个改动点，再给结论   # CoT
output_format: |
  输出一个 Markdown 表格，四列：问题 | 等级 | 影响 | 改法
  表格之外不要有任何多余文字
few_shot:
  - input: "...一段有内存泄漏的示例 diff..."
    output: "...期望的表格输出..."
```
看起来很工整对吧？我当时也这么觉得。但它有个致命问题：从 `role` 到 `constraints` 到 `few_shot`，每一个字都是我对着 Opus 的脾气一点点试出来的。
- "你是一名有十年经验的资深前端架构师"——这句对 Opus 有用，对小模型可能要写得更直白；
- "只报 P0 / P1"——Opus 拎得清，小模型经常分不清等级；
- few-shot 那个例子——是为 Opus 的注意力挑的，换个模型未必是最优示例。
> 病根在这：我把“对某个特定模型有效的措辞”当成了源代码，一行行硬编码进 Skill。相当于把神经网络训练好的权重手抄成 if-else 写进程序里，模型分布一变，全部作废。
## 二、换个世界观：Prompt 不该是人写的
这时候 DSPy 的主张就显得很有冲击力：
> **DSPy**（Declarative Self-Improving Language Programs，Stanford NLP 出品）：把大模型开发从"手工写 Prompt"变成"写代码、编译、调参"。它的核心信念是：Prompt 不该由人来写，该由系统根据你的代码结构和评估指标「编译」出来。
你只需要做两件事：
1. **声明契约**：这个任务的输入是什么、输出是什么（而不是怎么措辞）；
2. **给出标准**：用一个打分函数告诉系统"什么叫好"。
剩下的"怎么措辞、挑哪几个 few-shot 例子"，全交给编译器在你的评测集上自动搜索。换模型？重新 `compile` 一遍，编译器自动在新模型上把 Prompt 重新优化到最佳。
如果你写过 PyTorch，下面这张对照表基本就把事说完了：
<table fit-page-width="true" header-row="true">
<tr>
<td>PyTorch 概念</td>
<td>DSPy 里对应什么</td>
</tr>
<tr>
<td>网络结构（前向传播）</td>
<td>大模型调用链路（检索 → 推理 → 生成）</td>
</tr>
<tr>
<td>权重 Weights</td>
<td>Prompt 里的指令 + few-shot 样例</td>
</tr>
<tr>
<td>优化器 + Loss</td>
<td>Teleprompter 编译算法 + 你写的打分函数</td>
</tr>
</table>
看懂这张表，我那次翻车的本质就清楚了：**我在手抄权重。** DSPy 让你只定义结构和 Loss，权重交给“训练”。
## 三、重构第一步：把任务拆成「契约」（Signature）
动手。DSPy 里的 `Signature` 就是声明式的输入输出契约。注意它不是 Prompt：只说“要什么”，不说“怎么求”。
我原来那坨 `role` + `task` + `constraints` + `output_format`，重构后变成这样：
```python
import dspy

class CodeReview(dspy.Signature):
    """审查一段代码 diff，定位可维护性与性能问题。"""

    diff = dspy.InputField(desc="待审查的代码 diff")
    context = dspy.InputField(desc="项目背景，例如技术栈、关注点")

    issues = dspy.OutputField(
        desc="只含 P0/P1 问题的列表，每条包含：问题、等级、影响、最小改法"
    )
```
对比一下你会发现一个微妙但关键的差别：
- 手写 DSL 里，我详细规定了“你是十年经验架构师”“请一步步推理”“输出四列表格”这些措辞；
- Signature 里，我只声明了“输入是 diff + context，输出是带四个要素的 issues”。至于要不要先推理、用什么口吻、给几个例子，一个字都没写，全留给编译器。
> 这一步最反直觉，也最解放：你得刻意忍住“我得把话说清楚才放心”的冲动。在 DSPy 里话说太满反而是越权，那是编译器的活。
## 四、第二步：把契约包成可执行的 Module
Signature 只是声明，得用 `Module` 包成能跑的东西。DSPy 提供了一组现成模块，像乐高一样：
- `dspy.Predict`——最朴素，直接出答案；
- `dspy.ChainOfThought`——自动加"分步推理"，对应我原来手写的那句 `reasoning: 请先一步步分析`；
- `dspy.ReAct`——带工具调用的推理。
我这个审查任务需要推理，直接用 `ChainOfThought`。我不用再自己写“请一步步思考”了，模块自带：
```python
class CodeReviewer(dspy.Module):
    def __init__(self):
        super().__init__()
        # ChainOfThought 自动注入推理步骤，无需手写 CoT 咒语
        self.review = dspy.ChainOfThought(CodeReview)

    def forward(self, diff, context):
        return self.review(diff=diff, context=context)
```
到这里，那两百行 YAML 里的 `role` / `reasoning` / `output_format` / `few_shot` 全没了：要么变成 Signature 的字段描述，要么交给模块和后面的编译器。代码量肉眼可见地塌缩。
## 五、第三步：评测集——DSPy 的命门，也是大多数人放弃的地方
讲到这得停一下。DSPy 的“自动优化”全部建立在评测之上：它靠一个打分函数加一个测试集来判断“这版 Prompt 比那版好”，然后才谈得上编译。
没有评测集，`compile` 无从谈起。这也是我一直念叨的那句：先把 Eval 跑起来，再上 DSPy。
我的做法是把过去半年审查里真实漏报、误报过的 case 攒成测试集。这批带伤疤的样本，比任何造出来的例子都值钱：
```python
# 每条样本：一段 diff + 项目背景 + 这次审查"必须命中"的已知问题
trainset = [
    dspy.Example(
        diff=open("cases/leak_01.diff").read(),
        context="某官网项目二期，Vue3 组件，关注内存与可维护性",
        must_catch=["未在 onUnmounted 中清理 setInterval"],
    ).with_inputs("diff", "context"),
    dspy.Example(
        diff=open("cases/false_positive_03.diff").read(),
        context="某官网项目二期",
        must_catch=[],          # 这条是干扰项：理想输出应该「什么都不报」
    ).with_inputs("diff", "context"),
    # ……累计约 30 条真实 case
]
```
然后写打分函数 `metric`，整套系统里唯一需要你认真动脑的地方——它就是你对“好审查”的定义：
```python
def review_metric(example, pred, trace=None):
    text = str(pred.issues)
    # 1) 该报的 P0 必须命中（召回）
    hit = all(k in text for k in example.must_catch)
    # 2) 不该报的别瞎报（精确率）：干扰项要求基本沉默
    if not example.must_catch:
        clean = len(text.strip()) < 80
        return 1.0 if clean else 0.0
    return 1.0 if hit else 0.0
```
> 这一步才是真功夫。`metric` 写歪了，编译器就会朝错误的方向“努力优化”——非常勤奋地把你的 Prompt 调教成一个会做错事的东西。Garbage metric in, garbage prompt out。
## 六、第四步：编译——让系统替我写 Prompt
评测集和 metric 都齐了，就能调 Teleprompter（优化器）来编译。它会自动跑程序、收集表现好的样例、改写指令，"训练"出一版更强的 Prompt：
```python
from dspy.teleprompt import BootstrapFewShot

# 1) 配置底模——注意：要换模型，只动这一行
dspy.configure(lm=dspy.LM("openai/gpt-4o-mini"))

# 2) 编译：optimizer 会自动挑 few-shot、改指令
optimizer = BootstrapFewShot(metric=review_metric, max_bootstrapped_demos=4)
compiled_reviewer = optimizer.compile(CodeReviewer(), trainset=trainset)

# 3) 直接用——内部的 Prompt 已被编译优化过
result = compiled_reviewer(diff=my_diff, context="某官网项目二期")
print(result.issues)
```
关键就在第 1 行那句 `dspy.configure`。当初让我崩溃的换模型，现在只是改一个字符串、重跑一次 `compile`。编译器会在新模型上重新挑 few-shot、重写指令，把 Prompt 优化到这个模型的最佳状态，我一个字的咒语都不用重调。
所谓“换模型也可控”，说的就是这个：不是某段神 Prompt 万能，而是“生成 Prompt 的程序”可以对任何模型重新生成一次。
## 七、回到翻车现场：这次跑通了吗
![DSPy 编译后 Prompt 的翻车验证结果示意图](/images/posts/2026-06-12-我把一个-Skill-从手写-Prompt-重构成了可编译模块-一次-DSPy-实战复盘/我把一个-Skill-从手写-Prompt-重构成了可编译模块-一次-DSPy-实战复盘_002.png)
编译完的第一件事，当然是回到当初翻车的地方：还是那个开源小模型，还是那批让我崩溃的 diff。
这次没有稀碎。几件我最在意的事都对上了：
- 当初被漏掉的 setInterval 泄漏（就是测试集里 leak_01 那条），这次被稳稳抓了出来；
- 干扰项安静了：不该报问题的 diff，它真的什么都不报，“建议你多喝热水”式的凑数建议消失了；
- 表格格式不再崩——编译器挑进 Prompt 的 few-shot 本身就是格式正确的真实样例，小模型照着抄都不会错。
先把丑话说在前面：我没做严格的 A/B 评测。三十条真实 case 的回归全部通过，加上重新接回工作流之后没再出过当初那种翻车，这就是我目前能给出的全部证据。但对这个 Skill 来说够了——当初翻车翻得有多具体，这次跑通就有多具体。
省钱的初衷也达成了：日常审查跑在小模型上，只有重新编译那一下要多烧一笔 token。这笔账怎么算，下一节摊开看。
## 八、重构前后，到底差在哪
<table fit-page-width="true" header-row="true">
<tr>
<td>维度</td>
<td>手写 Prompt DSL（重构前）</td>
<td>DSPy 程序（重构后）</td>
</tr>
<tr>
<td>规模</td>
<td>约 200 行 YAML 咒语</td>
<td>约 40 行 Python + 一份测试集</td>
</tr>
<tr>
<td>谁写措辞</td>
<td>我，反复试错</td>
<td>编译器，自动生成</td>
</tr>
<tr>
<td>换模型成本</td>
<td>几乎重写一遍</td>
<td>改一行 + 重新 compile</td>
</tr>
<tr>
<td>质量保证</td>
<td>靠肉眼和手感</td>
<td>测试集 + metric 客观兜底</td>
</tr>
<tr>
<td>前期成本</td>
<td>低（直接写）</td>
<td>高（要写代码 + 攒评测集）</td>
</tr>
<tr>
<td>可解释性</td>
<td>高，Prompt 一眼能读</td>
<td>偏低，得去看编译产物</td>
</tr>
</table>
这张表也把 DSPy 的代价摆在明面上了：前期更重，可读性更差。
## 九、踩坑清单（拿命换的几条）
- **评测集质量就是天花板。** 我一开始用 AI 造的“完美样本”去编译，编出来的 Prompt 在真实脏数据上一塌糊涂。一定要用带伤疤的真实 case。
- **metric 会被钻空子。** 我第一版只看“P0 是否命中”，编译器很快学会把所有改动都报成 P0：召回 100%，精确率稀烂。后来补上“干扰项必须沉默”才掰回来。优化器永远朝着你写的指标努力，而不是你心里想的那个。
- **编译要花钱花时间。** `compile` 会实打实地反复调模型，几十条样本加多轮 bootstrap，token 和耗时都不便宜。别在主分支上随便触发。
- **可解释性会下降。** 编译出来的 Prompt 是机器写的，出问题时你得专门把编译产物 dump 出来读。手写 Prompt 那种"一眼看懂哪句话有问题"的便利，没了。
- **本地 Coding Agent 别碰这套编译流程。** 这条和我一贯的规矩一致：评测集、metric 这些是"事实源"，让它们读可以，自动改写交给人盯着。
![DSPy 重构 Skill 的收益与取舍总结图](/images/posts/2026-06-12-我把一个-Skill-从手写-Prompt-重构成了可编译模块-一次-DSPy-实战复盘/我把一个-Skill-从手写-Prompt-重构成了可编译模块-一次-DSPy-实战复盘_003.png)
## 十、写在最后
这次重构最值钱的收获，不是省下的那一百多行 YAML，而是脑子里那个开关被掰过来了：
> 以前我在打磨一段对某个模型有效的咒语；现在我在写一个能对任何模型生成咒语的程序。
但得给自己泼盆冷水：如果这个 Skill 从头到尾只在一个模型上跑、也不进 CI，这次重构就纯属给自己找事——手写依然是最聪明的选择。复杂度应该被需求拉上去，而不是被工程热情推上去。我的判断线很短：一次性任务，手写；要复用，结构化；会换模型、错了有真实代价、攒得出评测集，才轮到 DSPy。
这本身就是条很 PDCA 的路：轻方案先跑（Do），撞到“换模型就废”的墙（Check），再决定要不要升级（Adjust）。完整的决策流程图和升级信号，我放在文末那篇速查里了，照着对号入座就行，别像我一样先翻车再领悟。
## 延伸阅读
- DSPy 官方文档：[dspy.ai](http://dspy.ai) —— Signature / Module / Optimizer 的权威说明
- Stanford NLP《DSPy: Compiling Declarative LM Calls》论文 —— 想看原理的看这篇
- 我的内部速查：《从结构化 Prompt 到 DSPy：方法选择指南》 —— 决策路线 + 升级信号表
```plain text
━━━━━━━━━━━━━━━━━━━━
[{翊} 朱红印章 · 60×60px]

翊行代码 · YY
Code, one stroke at a time.

▸ 博客：wangyiyang.cc
▸ GitHub：github.com/wangyiyang
▸ 商务合作：[邮箱]
━━━━━━━━━━━━━━━━━━━━
```