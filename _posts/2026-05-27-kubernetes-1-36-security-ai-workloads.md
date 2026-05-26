---
layout: post
title: "Kubernetes v1.36 深度解读：安全默认收紧与 AI 工作负载支持的成熟化"
categories: [Kubernetes, Cloud Native, AI/ML]
description: "Kubernetes v1.36（代号 Haru）带来 70 项增强，安全默认全面收紧，AI/ML 工作负载支持从实验走向生产就绪。"
keywords: Kubernetes, v1.36, AI Workload, Security, DRA, Gang Scheduling, Cloud Native
mermaid: false
sequence: false
flow: false
mathjax: false
mindmap: false
mindmap2: false
---

> **发布日期**：2026-05-14 | **代号**：Haru | **贡献者**：491 人，来自 106 家公司

Kubernetes v1.36 的发布标志着这个云原生编排平台正在经历一次重要的范式转变——从"灵活框架"走向"有主见的默认配置"。本次release包含 **70 项增强**（18 项 Stable、25 项 Beta、25 项 Alpha），核心聚焦三大方向：**安全加固**、**AI/ML 工作负载成熟化**、以及**大规模集群的 API 可扩展性**。

本文将深入解读其中对工程师日常影响最大的几个关键特性。

---

## 一、安全默认收紧：从"可选"到"必须"

### 1.1 User Namespaces 正式 GA

这是容器安全领域的一个里程碑。User Namespaces 将容器内的 root 用户映射到宿主机上的非特权用户，意味着**即使进程成功逃逸容器，也无法获得宿主机的管理员权限**。

```bash
# 启用 User Namespaces 的 Pod 配置示例
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  hostUsers: false  # 启用 user namespace
  containers:
  - name: app
    image: nginx:latest
```

此前，容器逃逸往往意味着直接获得宿主机 root 权限。User Namespaces 的 GA 让"纵深防御"从最佳实践变成了默认行为。

### 1.2 Mutating Admission Policies 替代 Webhook

传统上，自定义准入控制需要维护独立的 webhook 服务器，带来额外的延迟和运维复杂度。v1.36 引入的 Mutating Admission Policies 使用 CEL（Common Expression Language）直接在 Kubernetes 原生对象中定义策略，**无需额外的 webhook 基础设施**。

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: MutatingAdmissionPolicy
metadata:
  name: enforce-security-context
spec:
  matchConstraints:
    resourceRules:
    - apiGroups: [""]
      apiVersions: ["v1"]
      resources: ["pods"]
      operations: ["CREATE"]
  mutations:
  - patchType: "ApplyConfiguration"
    applyConfiguration:
      expression: |
        {
          "spec": {
            "securityContext": {
              "runAsNonRoot": true,
              "seccompProfile": {"type": "RuntimeDefault"}
            }
          }
        }
```

这一变化对于需要严格安全合规的企业环境意义重大——策略执行不再依赖外部服务的可用性。

### 1.3 细粒度 Kubelet API 授权

过去，访问 kubelet API 需要宽泛的 `nodes/proxy` 权限。v1.36 引入了精确的、最小权限的访问控制，遵循**零信任架构**的原则，将权限粒度细化到具体的 API 端点。

### 1.4 SELinux Volume Labeling 优化

传统的递归文件重标记（`chcon -R`）在大型卷上可能导致显著的 Pod 启动延迟。v1.36 改为在挂载时直接应用正确的 SELinux 标签：

```bash
mount -o context=system_u:object_r:container_file_t:s0:c123,c456 /dev/vdb /mnt/data
```

这一改动将 SELinux 强制启用系统上的 Pod 启动时间从秒级缩短到毫秒级。

---

## 二、AI/ML 工作负载：从"能跑"到"跑好"

### 2.1 DRA（Dynamic Resource Allocation）增强进入 Beta

AI 工作负载对 GPU 等加速器的调度需求与传统应用截然不同。v1.36 中 DRA 的三项关键增强默认启用：

| 特性 | 解决的问题 |
|------|-----------|
| **DRA Partitionable Devices** | GPU 分区表达（如 MIG 配置） |
| **DRA Consumable Capacity** | 共享资源（如 GPU 显存）的用量追踪 |
| **DRA Device Taints & Tolerations** | 故障设备隔离 |

此前，GPU 调度采用整数分配模型——无论实际利用率如何，一整张 GPU 被分配给单个 Pod。DRA 的成熟让**细粒度的加速器资源共享**成为可能，这对于提高 GPU 集群利用率至关重要。

> "以前请求复杂资源通常需要不透明的、供应商特定的配置，调度器难以优化。" —— VMware Cloud Foundation 团队

### 2.2 Workload-Aware Preemption（Alpha）

分布式训练任务的一个经典痛点：**调度器抢占单个 Pod，导致 8 卡训练任务中 7 个 rank 仍在运行，但无法继续推进**。

v1.36 引入的 Workload-Aware Preemption 将 PodGroup 视为单一抢占单元，只有在确认高优先级组确实能完整调度后，才会执行驱逐。

```yaml
apiVersion: scheduling.x-k8s.io/v1alpha1
kind: PodGroup
metadata:
  name: training-job-8gpu
spec:
  schedulePolicy:
    preemptionPolicy: PreemptLowerPriority
  minMember: 8  # 必须同时调度 8 个 Pod
```

### 2.3 Gang Scheduling API 晋升 Beta

Gang Scheduling 确保一组关联 Pod 要么全部调度成功，要么全部不调度。v1.35 的 Alpha 特性在 v1.36 中进入 Beta，与 Workload-Aware Preemption 配合，构成了 AI 工作负载调度的基础设施。

### 2.4 挂起作业的可变资源（Beta）

队列控制器现在可以：
1. 挂起正在运行的作业
2. 调整 CPU/内存/GPU 资源请求
3. 恢复作业而无需销毁/重建 Pod

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: adaptive-training
spec:
  suspend: true  # 挂起
  template:
    spec:
      containers:
      - name: trainer
        resources:
          requests:
            nvidia.com/gpu: 4  # 从 8 卡调整为 4 卡
```

这消除了自定义控制器或完全重启作业的需求，对于**动态资源配额调整**场景（如夜间批处理让位于在线服务）非常实用。

---

## 三、大规模集群的 API 可扩展性

### 3.1 Sharded List and Watch Streams（Alpha）

超大规模集群中，单一资源类型的 watch 流可能成为瓶颈。v1.36 引入的分片机制将 watch 负载分布到多个流上，解决了"单连接单资源类型"的架构限制。

> "这是解决超大规模部署中 watch 流瓶颈的关键痛点。" —— Palark 团队

### 3.2 内存 QoS 与原地垂直扩缩容

cgroup v2 的分层内存保护机制与 Pod 的 request/limit 对齐，提供了更可预测的内存性能隔离。

原地垂直扩缩容（In-Place VPA）在 v1.36 中进入 Beta 并默认启用，允许调整 Pod 级别的 CPU/内存上限而无需重启容器。新增的 `ResizeDeferred` 事件类型确保在容量不足时 Pod 继续以现有规格运行，kubelet 在资源可用时自动重试。

---

## 四、移除与弃用：清理技术债

| 移除项 | 弃用版本 | 迁移路径 |
|--------|---------|---------|
| `gitRepo` volume 插件 | v1.11 | Init 容器或外部 git-sync 工具 |
| kube-proxy IPVS 模式 | v1.35 | iptables 或 nftables 模式 |
| Flex-volume kubeadm 支持 | — | CSI 驱动 |
| Portworx 内置驱动 | — | 外置 CSI 驱动 |

`gitRepo` 的移除尤其值得关注——它"允许攻击者以 root 身份在节点上运行代码"，是一个长期存在的安全隐患。

---

## 五、关键运维提醒：Ingress NGINX 已退役

**2026 年 3 月 24 日**，Kubernetes SIG Network 和安全响应委员会宣布 Ingress NGINX 控制器退役。自该日期起：

- 不再发布新版本
- 不再提供 bug 修复
- 不再提供安全补丁

使用 Ingress NGINX 的集群需要尽快迁移到替代方案（如 Traefik、Istio Gateway、或 Cilium Gateway API）。

---

## 六、总结：Kubernetes 的"成人礼"

v1.36 的发布反映了 Kubernetes 社区的成熟判断：**安全不再是可选配置，AI 工作负载不再是边缘场景，大规模运维不再是少数巨头的专利**。

对于平台工程师，这意味着：
1. **升级计划需要纳入安全默认变更的影响评估**
2. **AI 工作负载的调度策略需要重新设计**
3. **Ingress NGINX 的迁移不能再拖**

对于应用开发者，User Namespaces 和 Mutating Admission Policies 的 GA 意味着可以在不牺牲安全性的前提下获得更大的部署灵活性。

Kubernetes 正在从一个"你可以做任何事"的灵活框架，演变为一个"默认就做对的事"的生产级平台。这个转变，正是云原生技术走向成熟的标志。

---

**参考链接**：
- [Kubernetes v1.36 Release Notes](https://kubernetes.io/releases/notes/v1.36/)
- [InfoQ: Kubernetes v1.36 Released](https://www.infoq.com/news/2026/05/kubernetes-1-36-released/)
- [Ingress NGINX Retirement Announcement](https://kubernetes.io/blog/2026/03/24/ingress-nginx-retirement/)
