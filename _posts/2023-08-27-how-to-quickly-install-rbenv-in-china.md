---
layout: post
title: 如何在国内快速安装rbenv,及使用
categories: [Ruby, rbenv]
description: 如何在国内快速安装rbenv
keywords: Ruby, rbenv
mermaid: false
sequence: false
flow: false
mathjax: false
mindmap: false
mindmap2: false
---


## 简介

rbenv是一个Ruby版本管理工具，可以用来管理多个Ruby版本，同时也可以用来管理Ruby的gem包。

### 和RVM的对比

RVM是一个Ruby版本管理工具，和rbenv类似，但是RVM的功能更多，比如可以管理不同版本的gem包，同时RVM也是一个shell脚本，而rbenv是一个独立的程序，所以rbenv的性能更好。

### rbenv 源码地址

[https://github.com/rbenv/rbenv](https://github.com/rbenv/rbenv)

## 安装

### OSX

使用homebrew安装

```bash
brew install rbenv
```

如果安装过慢，可以使用 Homebrew 国内镜像，详见：[Homebrew / Linuxbrew 镜像使用帮助](https://mirrors.tuna.tsinghua.edu.cn/help/homebrew/)

### 源码安装（适用于Linux）

```bash
git clone https://gitee.com/wxqj/rbenv.git ~/.rbenv
git clone https://gitee.com/wxqj/ruby-build.git ~/.rbenv/plugins/ruby-build
git clone https://gitee.com/normalcoder/rbenv-update.git ~/.rbenv/plugins/rbenv-update
git clone https://gitee.com/normalcoder/rbenv-china-mirror.git ~/.rbenv/plugins/rbenv-china-mirror
```

*如果动手能力强，也可以自己在gitee上进行镜像代码仓库的创建*

### 一键安装包(未验证)

[https://gitee.com/RubyKids/rbenv-cn](https://gitee.com/RubyKids/rbenv-cn)

### 配置环境变量

```bash
export PATH="$HOME/.rbenv/bin:$PATH"
eval "$(rbenv init -)"
export RUBY_BUILD_MIRROR_URL=https://cache.ruby-china.com
```

*如果是bash用户，可以将上面的代码添加到 ~/.bashrc 文件中，如果是zsh用户，可以将上面的代码添加到 ~/.zshrc 文件中*

## 使用

### 可安装版本列表

```bash
rbenv install -l
```

### 列出版本

```bash
rbenv versions # 列出所有已安装的版本
rbenv version # 列出当前版本
```

### 安装Ruby

```bash
rbenv install 2.7.1
rbenv global 2.7.1 # 设置全局版本
rbenv local 2.7.1 # 设置当前目录版本
rbenv shell 2.7.1 # 设置当前shell版本
rbenv rehash # 重新hash
```

### rbenv 以及所有插件

```bash
rbenv update
```


## 参考

- [https://ruby-china.org/wiki/rbenv-guide](https://ruby-china.org/wiki/rbenv-guide)
- [https://zhuanlan.zhihu.com/p/616430346](https://zhuanlan.zhihu.com/p/616430346)
- [https://github.com/rbenv/rbenv](https://github.com/rbenv/rbenv)





---
layout: wiki
title: Kubernetes Core (未完)
cate1:
cate2:
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

- Kubernetes Core
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
		- 容器环境
		- 容器运行时类（Runtime Class）
		- 容器生命周期回调
	- Workloads
		- Pod
		- Controllers
			- Deployments
			- ReplicaSet
			- StatefulSet
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

