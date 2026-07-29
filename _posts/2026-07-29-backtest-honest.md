---
layout: post
title: "回测最大的风险，是写出一个会骗人的回测器"
categories: [AI 量化学习笔记]
description: "《AI 量化学习笔记》第 4 篇：回测最大的风险不是写不出来，而是写出一个会骗人的。不用现成框架，自己写一个五层结构（数据/信号/组合/成交/绩效）的简易回测器，显式处理未来函数、成本假设、现金约束和 T+1，并用 510300 完整历史跑通买入并持有、双均线与成本加倍基线。"
keywords: AI 量化学习笔记
mermaid: false
sequence: false
flow: false
mathjax: false
mindmap: false
mindmap2: false
---

![](https://www.wangyiyang.cc/images/posts/2026-07-29-backtest-honest/01.png)

> AI 量化学习笔记 · 第 4 篇

研究环境跑通之后，下一步自然是回测。但我得先泼自己一盆冷水：最危险的情况，是写出一个**会骗人的**回测器。曲线很漂亮，逻辑里却藏着未来函数或不切实际的成本假设；等到实盘发现，学费已经交了。

这篇先不讨论策略能赚多少。我只搭一个自己能逐笔核对的简易回测器，再配一套固定检验清单。

## 为什么不直接用 backtrader

backtrader、`vn.py` 这类框架当然成熟，但对我现在的阶段有两个问题。

一是黑箱。框架替你处理了成交假设、费用和撮合细节，恰恰是这些细节最容易骗人。用别人的默认值，等于把最危险的假设交给了不了解的代码。

二是过重。我的第一阶段目标是 4—6 只宽基 ETF 的月度轮动，每月调仓一次，计算量很小。为它引入一整个事件驱动框架，会增加当前阶段不需要的工程复杂度。

自己写一个两三百行的简易回测器，每个假设都摆在明面上，这才是这个阶段该做的事。等策略复杂到自己写不动，再换框架不迟。

## 五层结构

回测器按学习大纲拆成五层，每层只做一件事：

1. 数据层：价格、复权因子、交易日历、标的信息。上一篇已经就绪。
2. 信号层：策略在收盘后用当天及之前的数据生成信号。这一层的铁律是：不许碰未来的数据。
3. 组合层：把信号翻译成目标仓位，包括持有几只、各占多少、留多少现金和单标的上限。
4. 成交层：信号在下一交易日成交，扣佣金和滑点。所有「今天收盘看信号、今天收盘价买入」的写法都是自欺。
5. 绩效层：净值、年化、最大回撤、夏普、换手率、费用，以及全部交易明细。

当前两个基线都只有一个标的，所以组合层暂时收敛成一列 `target_weight`，直接表达 0 到 1 之间的目标仓位。等进入多 ETF 轮动，再把组合层拆成独立模块。胜率也暂时不算：按交易、按持仓周期还是按交易日计算，含义完全不同，在口径明确前不放一个容易误导的数字。

五层之间靠两个约定连接：**信号只能由 T 日及以前的数据决定**，**T 日信号只在 T+1 生效**。约束要落进代码和测试，不能只留在注释里。

数据层沿用上一篇的 `load_daily`，直接从 DuckDB 读取后复权日线。仓库版本会校验价格、日期顺序和窗口参数；这些属于防御性代码，正文只保留信号如何生成：

```python
# src/backtest/signals.py（核心逻辑）
import pandas as pd


def sma_cross(df: pd.DataFrame, fast: int = 20, slow: int = 60) -> pd.Series:
    fast_ma = df["close"].rolling(fast).mean()
    slow_ma = df["close"].rolling(slow).mean()
    return (fast_ma > slow_ma).astype(float).rename("target_weight")


def buy_and_hold(df: pd.DataFrame) -> pd.Series:
    return pd.Series(1.0, index=df.index, name="target_weight")
```

`rolling` 只使用当前行和之前的值。测试里还会修改未来价格，确认过去的信号完全不变。风险更容易出现在信号接到价格的那一步，所以成交层统一执行一次显式的 `shift(1)`。

## 成交层：T+1、成本和可买数量

第一版示例里有一个很隐蔽的问题：先按收盘价算满仓份数，再加滑点和佣金，可能让现金变成负数。真实订单不可能借出这笔不存在的钱。修正版会把滑点、最低佣金和整手约束一起纳入最大可买数量。

另一个细节是逐笔复现。成交价保留 6 位小数，佣金和现金按分取整；CSV 里的 `shares`、`fill`、`fee` 和 `cash_after` 可以直接用计算器复算。

仓库里的成交模块还包含完整的参数校验、空交易表结构和错误信息。正文只展开三件会改变结果的事：T+1、成交成本和现金约束。

```python
# src/backtest/engine.py（核心逻辑）
from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Costs:
    commission: float = 0.0003
    min_commission: float = 5.0
    slippage: float = 0.001


def trade_fee(shares, fill, costs):
    return round(max(abs(shares) * fill * costs.commission,
                     costs.min_commission), 2)


def affordable_buy(cash, desired, fill, costs, lot=100):
    shares = desired
    while shares > 0:
        if shares * fill + trade_fee(shares, fill, costs) <= cash:
            return shares
        shares -= lot
    return 0


def run_backtest(df, signal, costs=Costs(), init_cash=100_000, lot=100):
    target = signal.shift(1, fill_value=0.0)  # T 日信号，T+1 生效
    cash, shares = float(init_cash), 0
    equity, trades = [], []

    for i, row in enumerate(df.itertuples(index=False)):
        price = float(row.close)
        nav_before = cash + shares * price
        desired = int(nav_before * target.iat[i] / price // lot) * lot
        delta = desired - shares

        if delta:
            fill = round(price * (1 + costs.slippage * np.sign(delta)), 6)
            if delta > 0:
                delta = affordable_buy(cash, delta, fill, costs, lot)
            if delta:
                fee = trade_fee(delta, fill, costs)
                cash = round(cash - delta * fill - fee, 2)
                shares += delta
                trades.append({"date": row.date,
                               "side": "buy" if delta > 0 else "sell",
                               "shares": abs(delta), "fill": fill,
                               "fee": fee, "cash_after": cash})

        equity.append({"date": row.date, "close": price,
                       "shares": shares, "cash": cash,
                       "nav": cash + shares * price})

    return pd.DataFrame(equity), pd.DataFrame(trades)
```

这里没有为了向量化牺牲可读性。完整历史只有 3291 行，单次回测不到一秒；现阶段更重要的是让每一笔交易都可以解释。

## 绩效层：先把口径写清楚

绩效层负责算术，解释留给研究环节：

仓库版本同样保留输入校验。指标本身只需要这段算术：

```python
# src/backtest/metrics.py（核心逻辑）
def summary(equity, trades, freq=252):
    nav = equity["nav"]
    returns = nav.pct_change().dropna()
    years = (len(nav) - 1) / freq
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1 / years) - 1
    drawdown = (nav / nav.cummax() - 1).min()
    sharpe = returns.mean() / returns.std() * np.sqrt(freq)
    turnover = trades["shares"].mul(trades["fill"]).sum() / nav.iloc[0]

    return {
        "年化": round(cagr, 4),
        "最大回撤": round(drawdown, 4),
        "夏普": round(sharpe, 2),
        "累计换手": round(turnover, 2),
        "交易笔数": len(trades),
        "总费用": round(trades["fee"].sum(), 2),
    }
```

夏普使用零无风险利率，年化按每年 252 个交易日计算。累计换手是所有成交额除以初始净值，是单边累计口径。年化区间使用 `len(nav) - 1` 个收益周期，不把第一天误算成一段收益。

## 三个最容易骗人的地方

未来函数是第一个。用当天收盘价计算信号又按当天收盘价成交、用后视才知道的成分股名单回测历史，都属于这一类。我的防线是双重的：信号函数只使用因果窗口，成交层再强制 T+1。

成本假设是第二个。我目前使用佣金万分之三、单笔最低 5 元和单边千一滑点；ETF 不计印花税。滑点没人给你保证，所以还要把佣金和滑点加倍再跑一遍。

成交可行性是第三个。当前代码已经处理现金上限和 100 份整手约束。涨跌停无法成交、停牌顺延暂未实现，因为这两个宽基 ETF 基线没有用到；进入 A 股个股阶段时，再把成交状态作为明确接口加入，不能提前假装已经处理。

## 这次检查到哪一步

这版先验证了两件事：

- [x] 把成本加倍，看看结果会变成什么样
- [x] 抽一笔交易，从信号到成交手算一遍

另外三项暂时没做：

- [ ] 划分样本内和样本外
- [ ] 扰动均线参数，观察结果是否稳定
- [ ] 分别查看上涨、下跌和震荡阶段的表现

它们更适合留到正式研究轮动策略时再做。这一篇先确认回测器算得对，不急着证明某个策略有效。

## 先跑两个不性感的基线

回测器写完，先不跑轮动策略，而是跑两个「无聊」的基线：一次性买入并持有，以及双均线。

这里特意改掉“定投”的叫法。`buy_and_hold` 是初始资金一次性买入，此后持续持有；真正的定投还需要定义每期外部现金流、投入日期和收益率口径，不能混为一谈。

它们是两把尺子。买入并持有给出被动基准，双均线暴露趋势策略的滞后和换手成本。以后任何策略扣完成本还跑不过被动基准，就不值得继续增加复杂度。

正文里的运行脚本也只保留实验本身。路径处理、目录创建和封装函数仍在仓库版本中：

```python
# scripts/run_baseline.py（核心逻辑）
df = load_daily("510300", adjust="hfq")

cases = [
    ("buy_and_hold", buy_and_hold(df), Costs()),
    ("sma_20_60", sma_cross(df), Costs()),
    ("sma_20_60_double_cost", sma_cross(df),
     Costs(commission=0.0006, slippage=0.002)),
]

for name, signal, costs in cases:
    equity, trades = run_backtest(df, signal, costs=costs)
    print(name, summary(equity, trades))
    if name != "sma_20_60_double_cost":
        equity.to_csv(f"data/{name}_equity.csv", index=False)
        trades.to_csv(f"data/{name}_trades.csv", index=False)
```

脚本从项目根目录直接运行：

```bash
.venv/bin/python scripts/run_baseline.py
```

每个基线输出一份净值 CSV 和一份交易 CSV：

- `data/buy_and_hold_equity.csv`
- `data/buy_and_hold_trades.csv`
- `data/sma_20_60_equity.csv`
- `data/sma_20_60_trades.csv`

## 510300 实际运行结果

这次使用仓库 DuckDB 中的 510300 后复权日线，区间为 2013-01-04 至 2026-07-24，共 3291 个交易日。初始资金 100,000 元，每手 100 份。

- 买入并持有
  - 年化：6.12%
  - 最大回撤：-44.37%
  - 夏普：0.39
  - 累计换手：1.00
  - 交易笔数：1
  - 总费用：29.99 元
- SMA 20/60
  - 年化：0.82%
  - 最大回撤：-47.42%
  - 夏普：0.13
  - 累计换手：73.32
  - 交易笔数：70
  - 总费用：2,199.54 元
- SMA 20/60（佣金与滑点加倍）
  - 年化：0.13%
  - 最大回撤：-50.01%
  - 夏普：0.08
  - 累计换手：69.96
  - 交易笔数：70
  - 总费用：4,197.74 元

结果并不漂亮，但这正是基线的价值。这个区间里，双均线扣除成本后明显跑输买入并持有；佣金和滑点加倍后，年化从 0.82% 进一步降到 0.13%，最大回撤扩大到 50.01%。这说明当前的 20/60 参数没有提供足够厚的收益缓冲，不能因为它“看起来像一个策略”就继续包装。

成本加倍后的累计换手略低，不是成交次数减少，而是更高成本持续侵蚀净值，在整手约束下后续可成交份数变少。

### 抽查第一笔交易

买入并持有的首日信号在下一交易日成交：

| 字段 | 数值 |
|---|---|
| 信号日 | 2013-01-04 |
| 成交日 | 2013-01-07 |
| 成交方向 | 买入 |
| 成交份数 | 38,900 |
| 模拟成交价 | 2.569567 元 |
| 佣金 | 29.99 元 |
| 成交后现金 | 13.85 元 |

手算结果为：

```text
100000 - 38900 × 2.569567 - 29.99 = 13.8537
按分取整后为 13.85 元
```

完整结果还通过了这些机器检查：

- 7 个回归测试全部通过；
- 两条净值序列都恰好有 3291 行；
- 所有持仓数量都是 100 的整数倍；
- 买入并持有、双均线的最低现金分别为 13.85 元和 10.99 元，没有负现金；
- `nav = cash + shares × close` 的最大误差约为 `1e-11`，属于浮点表示误差；
- 修改未来价格不会改变过去的双均线信号；
- T 日信号只会在 T+1 产生持仓变化。

## 这一阶段的完成标准

完成标准只有一条：对一个简单策略，输出可复现的回测报告和全部交易明细。换一台机器，在相同数据和依赖版本上重跑，数字一致。

这一步已经跑通。更重要的结论不是“双均线赚了多少”，而是这套回测器已经能主动暴露一个策略在成本、回撤和成交约束下的问题。下一篇再开始做月度动量轮动。

> 本系列不构成投资建议。回测收益不代表实盘收益，历史数据不保证未来表现。
