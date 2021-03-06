---
layout: wiki
title: Kubernetes Core (未完)
cate1: Cloud
cate2: Kubernetes
description: Kubernetes Core
keywords: Kubernetes
type:
link:
mermaid: false
sequence: false
flow: false
mathjax: true
mindmap: true
mindmap2: true
---

- Kubernetes Map
	- Cluster Architecture
		- Master
			- Etcd
		- Node
			- 添加方式
				- 节点上的 `kubelet` 向控制面执行自注册；
				- 你（或者别的什么人）手动添加一个 Node 对象
				- 要求
					- 节点名称唯一
			- 组件
				- Kubelet
				- Runtime
					- rkt
					- Docker
				- kube-proxy
			- 状态
				- 地址
					- HostName
					- ExternalIP
					- InternalIP
				- 状况(conditions)
					- Ready
					- DiskPressure
					- MemoryPressure
					- PIDPressure
					- NetworUnavailable
				- 容量与可分配
					- CPU
						- capacity
						- allocatable
					- 内存
						- capacity
						- allocatable
					- Pod个上限
				- 信息（Info)
					- Kubernetes版本
					- kubelet 版本
					- kube-proxy版本
				- 心跳
					- 形式
						- 更新节点的 `.status`
							- 更新默认间隔 5 s
							- 节点不可达事件 40 秒
						- `kube-node-lease` [名字空间](https://kubernetes.io/zh-cn/docs/concepts/overview/working-with-objects/namespaces/)中的 [Lease（租约）](https://kubernetes.io/zh-cn/docs/concepts/architecture/leases/)对象。 每个节点都有一个关联的 Lease 对象
							- 更新间隔 5 s
							- 回退：200 毫秒重试，最长重试间隔 7 秒
					- 获取方式
						- kubelet
				- 节点控制器
					- 作用
						- 节点注册时为它分配一个 CIDR 区段（如果启用了 CIDR 分配）
						- 保持节点控制器内的节点列表与云服务商所提供的可用机器列表同步
						- 监控节点的健康状况
							- 在节点不可达的情况下，在 Node 的 `.status` 中更新 `Ready` 状况。 在这种情况下，节点控制器将 NodeReady 状况更新为 `Unknown`
							- 如果节点仍然无法访问：对于不可达节点上的所有 Pod 触发 [API 发起的逐出](https://kubernetes.io/zh-cn/docs/concepts/scheduling-eviction/api-eviction/)操作。 默认情况下，节点控制器在将节点标记为 `Unknown` 后**等待 5 分钟**提交第一个驱逐请求。
					- 配置
						- 默认情况下，节点控制器每 5 秒检查一次节点状态，可以使用 `kube-controller-manager` 组件上的 `--node-monitor-period` 参数来配置周期。
						- 逐出速率限制
							- 节点控制器把逐出速率限制在每秒 `--node-eviction-rate` 个（默认为 0.1）。 这表示它每 10 秒钟内至多从一个节点驱逐 Pod
							- 如果不健康节点的比例超过 `--unhealthy-zone-threshold` （默认为 0.55）， 驱逐速率将会降低
							- 如果集群较小（意即小于等于 `--large-cluster-size-threshold` 个节点 - 默认为 50）， 驱逐操作将会停止。
							- 否则驱逐速率将降为每秒 `--secondary-node-eviction-rate` 个（默认为 0.01）
				- 资源容量跟踪
					- 通过[自注册](https://kubernetes.io/zh-cn/docs/concepts/architecture/nodes/#self-registration-of-nodes)机制生成的 Node 对象会在注册期间报告自身容量
					- 如果你[手动](https://kubernetes.io/zh-cn/docs/concepts/architecture/nodes/#manual-node-administration)添加了 Node， 你就需要在添加节点时手动设置节点容量
				- 节点拓扑
				- 节点体面关闭
					- 基于 Pod 优先级的节点体面关闭
				- 节点非体面关闭
				- 交换内存管理
				- 
		- 节点与控制面之间的通信
			- 控制面到节点
				- 从API服务器到集群中每一个节点后三个运行的kubelet进程
				- 从API服务器通过它的代理功能链接到任何节点、POD或者服务
			- 节点到控制面
				- Kubernetes 采用的是中心辐射型（Hub-and-Spoke）API 模式。 所有从节点（或运行于其上的 Pod）发出的 API 调用都终止于 API 服务器。 其它控制面组件都没有被设计为可暴露远程服务。 API 服务器被配置为在一个安全的 HTTPS 端口（通常为 443）上监听远程连接请求， 并启用一种或多种形式的客户端[身份认证](https://kubernetes.io/zh-cn/docs/reference/access-authn-authz/authentication/)机制。 一种或多种客户端[鉴权机制](https://kubernetes.io/zh-cn/docs/reference/access-authn-authz/authorization/)应该被启用， 特别是在允许使用[匿名请求](https://kubernetes.io/zh-cn/docs/reference/access-authn-authz/authentication/#anonymous-requests) 或[服务账户令牌](https://kubernetes.io/zh-cn/docs/reference/access-authn-authz/authentication/#service-account-tokens)的时候。
			- API 服务器到 kubelet
				- 作用
					- 获取 Pod 日志
					- 挂接（通过Kubectl)到运行中的Pod
					- 提供kubelet的端口转发功能
			- API 服务器到节点、Pod 和服务
			- SSH 隧道（废弃）
			- Konnectivity 服务（SSH 隧道的替代方案）
		- CRI
		- GC
		- Cgroup
	- 容器
		- 镜像
			- 镜像拉取策略
				- IfNotPresent(default)
				- Always
				- Never
			- 默认镜像拉取策略
				- 如果你省略了 `imagePullPolicy` 字段，并且你为容器镜像指定了摘要， 那么 `imagePullPolicy` 会自动设置为 `IfNotPresent`。
				- 如果你省略了 `imagePullPolicy` 字段，并且容器镜像的标签是 `:latest`， `imagePullPolicy` 会自动设置为 `Always`。
				- 如果你省略了 `imagePullPolicy` 字段，并且没有指定容器镜像的标签， `imagePullPolicy` 会自动设置为 `Always`。
				- 如果你省略了 `imagePullPolicy` 字段，并且为容器镜像指定了非 `:latest` 的标签， `imagePullPolicy` 就会自动设置为 `IfNotPresent`。
		- 容器环境
			- 文件系统，其中包含一个[镜像](https://kubernetes.io/zh-cn/docs/concepts/containers/images/) 和一个或多个的[卷](https://kubernetes.io/zh-cn/docs/concepts/storage/volumes/)
			- 容器自身的信息
			- 集群中其他对象的信息
		- 容器运行时类（Runtime Class）
		- 容器生命周期回调
	- Workloads
		- Pod
			- 生命周期
				- Pending：Pod 已被 Kubernetes 系统接受，但有一个或者多个容器尚未创建亦未运行。此阶段包括等待 Pod 被调度的时间和通过网络下载镜像的时间。
				- Running：Pod 已经绑定到了某个节点，Pod 中所有的容器都已被创建。至少有一个容器仍在运行，或者正处于启动或重启状态。
				- Succeeded：Pod 中的所有容器都已成功终止，并且不会再重启。
				- Failed：Pod 中的所有容器都已终止，并且至少有一个容器是因为失败终止。也就是说，容器以非 0 状态退出或者被系统终止。
				- Unknown：因为某些原因无法取得 Pod 的状态。这种情况通常是因为与 Pod 所在主机通信失败。
			- 容器状态：
				- `Waiting`
				- `Running`
				-  `Terminated`
			- 容器重启策略（restartPolicy）
				- Always（default）
				- OnFailure
				- Never
			- Pod 状况
				- PodScheduled
				- PodHasNetwork
				- ContainersReady
				- Initialized
				- Ready
			- 探测类型
				- `livenessProbe`
				- `readinessProbe`
				- `startupProbe`
			- Init 容器
			- 干扰（Disruptions）
			- 临时容器
			- Pod QoS 类
			- 用户命名空间
			- Downward API
		- Controllers
			- Deployments
			- ReplicaSet
			- StatefulSet(20230915更新)
				- 价值：
					- 稳定的、唯一的网络标识符。
					- 稳定的、持久的存储。
					- 有序的、优雅的部署和扩缩。
					- 有序的、自动的滚动更新。
				- 限制：
					-  PersistentVolume Provisioner 
					- 删除或者扩缩 StatefulSet 不会删除它关联的存储卷
					- StatefulSet 当前需要无头服务来负责 Pod 的网络标识。
					- 当删除一个 StatefulSet 时，该 StatefulSet 不提供任何终止 Pod 的保证。 
					- 在默认 Pod 管理策略(OrderedReady) 时使用滚动更新， 可能进入需要人工干预才能修复的损坏状态。
				- 组件：
					- 最短就绪秒数（可选，`.spec.minReadySeconds`）：指定新创建的 Pod 应该在没有任何容器崩溃的情况下运行并准备就绪，才能被认为是可用的。
					- Pod 管理策略（可选，`.spec.podManagementPolicy`）：指定控制器如何管理 Pod。
						- OrderedReady，表示控制器应该按照它们在 StatefulSet 中的顺序创建和删除 Pod。
						- Parallel，表示控制器可以并行创建和删除 Pod。
					- 更新策略（可选，`.spec.updateStrategy`）：指定控制器如何更新 Pod。
						- OnDelete，表示手动更新 Pod。
						- RollingUpdate，表示控制器应该自动更新 Pod。
					- 服务名称（可选，`.spec.serviceName`）：指定用于访问 Pod 的服务的名称。
					- 卷声明（可选，`.spec.volumeClaimTemplates`）：指定 StatefulSet 管理的卷声明。
					- Pod 模板（`.spec.template`）：指定 StatefulSet 管理的 Pod 的模板。
					- Pod 模板标签（`.spec.template.metadata.labels`）：指定 StatefulSet 管理的 Pod 的标签。
					- 起始序号（`.spec.podManagementPolicy`）：指定 StatefulSet 管理的 Pod 的起始序号。
					- 最大不可用 Pod 数（`.spec.updateStrategy.rollingUpdate.maxUnavailable`）：指定在滚动更新期间可以不可用的 Pod 的最大数量
			- DaemonSet
			- Job
			- CronJob
			- Replication Controller(old)
	- Services, Load Balancing, and Networking
		- Service
		- Ingress
		- Ingress 控制器
		- EndpointSlice
		- 网络策略
		- Service 与 Pod 的DNS
		- IPv4/IPv6双协议栈
		- 拓扑感知路由
		-  Service ClusterIP 分配
		- 服务内部流量策略
	- Storage
		- 卷
		- 持久卷
		- 投射卷
		- 临时卷
		- 存储类
		- 动态卷制备
		- 卷快照
		- 卷快照类
		- CSI 卷克隆
		- 存储容量
		- 特定于节点的卷数限制
		- 卷健康监测
	- Configuration
	- Security
	- Policies
	- Scheduling，Preemption and Eviction
