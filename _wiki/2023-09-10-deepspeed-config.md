---
layout: wiki
title: DeepSpeed 配置文件说明
cate1: LLM
cate2: DeepSpeed
description: DeepSpeed 配置文件说明
keywords: LLM, DeepSpeed
type:
link:
mermaid: false
sequence: false
flow: false
mathjax: false
mindmap: false
mindmap2: false
---


1. Batch Size Related Parameters（批大小相关的参数）

>注意：train_batch_size必须等于`train_micro_batch_size_per_gpu * gradient_accumulation * GPU`的数量。为简单起见，您可以选择只指定其中两个参数，DeepSpeed将自动推断出最后一个参数。

#### 1.1 _**train_batch_size（训练批大小）**_: [integer]

有效的训练批大小。这是导致一次模型更新步骤的数据样本数量。train_batch_size由单个GPU在一个前向/反向传递中处理的批大小（即`train_micro_batch_size_per_gpu`）、梯度累积步骤（即`gradient_accumulation_steps`）和GPU的数量累加而成。如果提供了`train_micro_batch_size_per_gpu`和`gradient_accumulation_steps`，则可以省略train_batch_size。

#### 1.2 _**train_micro_batch_size_per_gpu**_: [integer]

在一次步骤中由一个GPU处理的批大小（不包括梯度累积）。如果提供了`train_batch_size`和`gradient_accumulation_steps`，可以省略此参数。

默认值： `train_batch_size`

#### 1.3 _**gradient_accumulation_steps（梯度累积步骤）**_: [integer]

在对梯度进行平均和应用之前累积梯度的训练步骤数。这个功能有时对于提高可扩展性很有用，因为它减少了步骤之间梯度通信的频率。此功能的另一个影响是可以使用更大的每个GPU批大小进行训练。如果提供了`train_batch_size`和`train_micro_batch_size_per_gpu`，则可以省略此参数。

默认值：1

### 2. Optimizer Parameters（优化器参数）

#### 2.1 _**optimizer（优化器）**_: [dictionary]

**type**

DeepSpeed原生支持Adam、AdamW、OneBitAdam、Lamb和OneBitLamb优化器（详见此处以获取详细信息），并且会从torch中导入其他优化器。

**params**

用于实例化优化器的参数字典，参数名称必须与优化器构造函数的签名匹配（例如，对于Adam优化器）。

**Example of  optimizer with Adam**

```json
"optimizer": {
    "type": "Adam",
    "params": {
      "lr": 0.001,
      "betas": [
        0.8,
        0.999
      ],
      "eps": 1e-8,
      "weight_decay": 3e-7
    }
  }
```


### 3. Scheduler Parameters

执行`model_engine.step()`时，DeepSpeed会在每个训练步骤中调用调度器的`step()`方法。

#### 3.1 scheduler: [dictionary]

**type**

调度程序名称。有关支持计划程序的列表，请参阅[此处](https://deepspeed.readthedocs.io/en/latest/schedulers.html)。

**params**

用于实例化调度器的参数字典，参数名称应与调度器构造函数的签名匹配。

Example of _**scheduler**_

```json
 "scheduler": {
      "type": "WarmupLR",
      "params": {
          "warmup_min_lr": 0,
          "warmup_max_lr": 0.001,
          "warmup_num_steps": 1000
      }
  }
```

### 4. Communication options 通讯选项

#### 4.1 _**communication_data_type**_: [string]

在梯度平均过程中，使用所选的数据类型进行通信。默认情况下，数据类型由所选的模式确定。

#### 4.2 _**prescale_gradients**_: [boolean]

在执行全局梯度归约之前，进行梯度的缩放处理。

默认值：false

#### 4.3 _**gradient_predivide_factor**_: [float]

在进行梯度平均之前，通过一个指定的因子对梯度进行预除操作，有时可以在将梯度扩展到大量 GPU 时提高 FP16 的稳定性。

默认值：1.0

#### 4.4 _**sparse_gradients**_: [boolean]

启用 torch.nn.Embedding 梯度的稀疏压缩。这个特性基本上已经被弃用，因为我们不再经常看到使用它的情况。需要注意的是，此特性与 torch.sparse 相关的特性不兼容。

默认值：false

### 5. FP16 training options

>注意：此模式不能与下面描述的 amp 模式混合使用。

#### 5.1 _**fp16**_: [dictionary]

用于使用 NVIDIA Apex 包进行混合精度/FP16 训练的配置如下。示例中包含了可用的字典键。请注意：此配置不使用 Apex 的 AMP 模式，后者允许在混合精度训练模式下获得更大的灵活性，该模式类似于 AMP 的 O2 模式。如果您想使用更复杂的混合精度模式，请参考下方的 AMP 支持。当前要使用 ZeRO（目前版本），则必须使用此模式。


```json
"fp16": {
    "enabled": true,
    "auto_cast": false,
    "loss_scale": 0,
    "initial_scale_power": 16,
    "loss_scale_window": 1000,
    "hysteresis": 2,
    "consecutive_hysteresis": false,
    "min_loss_scale": 1
}
```

- "enabled"：布尔值，表示是否启用混合精度（FP16）。默认值：false
- "auto_cast"：布尔值，表示是否启用自动类型转换。如果设置为 True，则会自动将 FP32 张量转换为 FP16，以便在 FP16 模式下执行计算。默认值：false
- "loss_scale"：指定初始的损失缩放因子。设置为0表示使用动态损失缩放。默认值：0.0
- "initial_scale_power"：初始损失缩放因子的幂值。默认值：16
- "loss_scale_window"：用于计算新的损失缩放因子所需的时间窗口大小。默认值：1000
- "hysteresis"：用于控制损失缩放的迟滞量。默认值：2
- "consecutive_hysteresis"：布尔值，表示是否在连续更新时使用迟滞量。默认值：false
- "min_loss_scale"：损失缩放因子的最小值。默认值：1
### 6. BFLOAT16 training options

>注意：此模式不能与下方描述的 amp 模式混合使用。
>注意：此模式不能与上方描述的 fp16 模式混合使用。

#### 6.1 _**bf16**_: [dictionary]

使用 bfloat16 浮点格式作为替代 FP16 的配置如下。BFLOAT16 需要硬件支持（例如，NVIDIA A100）。以下示例包括可用的字典键。使用 bfloat16 进行训练不需要损失缩放。


```json
"bfloat16": {
	"enabled": True
}
```



### 7. Automatic mixed precision (AMP) training options

> 注意：此模式不能与上方描述的 fp16 模式混合使用。此外，该模式目前与 ZeRO 不兼容。

#### 7.1 _**amp**_: [dictionary]

使用 NVIDIA 的 Apex AMP 包进行自动混合精度 (AMP) 训练的配置如下所示。示例中包括可用的字典键。不兼容上方的 fp16 模式或 ZeRO。在 "enabled" 之外的其他参数将传递给 AMP 的 initialize 调用，请查阅 [apex.amp.initialize 文档](https://nvidia.github.io/apex/amp.html#apex.amp.initialize)中的 API 和说明。

```json
"amp": {
    "enabled": true,
    ...
    "opt_level": "O1",
    ...
}
```

#### 7.2 amp:enabled: [boolean]

"enabled" 是 AMP（Automatic Mixed Precision，自动混合精度）训练的一个参数，指示是否启用 AMP 训练。

默认值：false

#### 7.3 **_amp params_**: [various]

在 "enabled" 之外的所有参数将传递给 AMP 的 initialize 调用。请参阅 apex.amp.initialize 文档中的 API 和描述以了解更多信息。


### 参考：

- [https://www.deepspeed.ai/docs/config-json/#gradient-clipping](https://www.deepspeed.ai/docs/config-json/#gradient-clipping)