---
layout: post
title: 使用 MPI Opnerator 和 DeepSpeed 进行分布式训练
categories: [MLOps, LLM]
description: 使用 MPI Opnerator 和 DeepSpeed 进行分布式训练
keywords: MLOps, LLM
mermaid: false
sequence: false
flow: false
mathjax: false
mindmap: false
mindmap2: false
---

## 介绍

本文介绍如何使用 MPI Operator 和 DeepSpeed 进行分布式训练。

## 环境

- MPI Operator v0.4.0
- DeepSpeed v0.10.0
- Kubernetes v1.21.2
- Docker v20.10.7
- Tesla V100 * 3

以cifar10为例

## 镜像

```Dockerfile
FROM registry.cn-beijing.aliyuncs.com/acs/deepspeed:v072_base
# FROM deepspeed/deepspeed:v072_torch112_cu117

 Install OpenSSH
RUN apt-get install -y --no-install-recommends openssh-client openssh-server && \
    mkdir -p /var/run/sshd

# Allow OpenSSH to talk to containers without asking for confirmation
# by disabling StrictHostKeyChecking.
RUN sed -i 's/[ #]\(.*StrictHostKeyChecking \).*/ \1no/g' /etc/ssh/ssh_config && \
    echo "    UserKnownHostsFile /dev/null" >> /etc/ssh/ssh_config && \
    sed -i 's/#\(StrictModes \).*/\1no/g' /etc/ssh/sshd_config

RUN apt update
RUN apt install -y ninja-build

RUN mkdir /deepspeed
WORKDIR "/deepspeed"
RUN git clone https://github.com/microsoft/DeepSpeedExamples/
WORKDIR "/deepspeed/DeepSpeedExamples/training/"
RUN pip install -r cifar/requirements.txt
CMD ["/bin/bash"]
```



## Kubernetes 配置

### 创建 MPI Operator

```bash

```yaml
apiVersion: kubeflow.org/v2beta1
kind: MPIJob
metadata:
  name: deepspeed-mpijob
spec:
  slotsPerWorker: 1
  runPolicy:
    cleanPodPolicy: Running
  mpiReplicaSpecs:
    Launcher:
      replicas: 1
      template:
        spec:
          containers:
          # Container with the DeepSpeed training image built from the provided Dockerfile and the DeepSpeed support
          # Sample container for DeepSpeed applied model, you can check this image to your application or training process
          - image: cifards:v0.0.1
            name: deepspeed-mpijob-container
            command:
            - mpirun
            - --allow-run-as-root
            - -np
            - "2"
            - -bind-to
            - none
            - -map-by
            - slot
            - -x
            - NCCL_DEBUG=INFO
            - -x
            - LD_LIBRARY_PATH
            - -x
            - PATH
            - -mca
            - pml
            - ob1
            - -mca
            - btl
            - ^openib
            - python
            - cifar/cifar10_deepspeed.py
            - --deepspeed_mpi
            - --deepspeed
            - --deepspeed_config
            - ds_config.json
            resources:
              limits:
                # Optional: varies to nodepool group 
                cpu: 16
                memory: 32Gi
                nvidia.com/gpu: 2
              requests:
                # Optional: varies to nodepool group
                cpu: 8
                memory: 16Gi
                nvidia.com/gpu: 1
    Worker:
      replicas: 2
      template:
        spec:
          # OPTIONAL: Taint toleration for the specific nodepool
          #
          # Taints and tolerations are used to ensure that the DeepSpeed worker pods
          # are scheduled on the desired nodes. By applying taints to nodes, you can
          # repel pods that do not have the corresponding tolerations. This is useful
          # in situations where you want to reserve nodes with specific resources
          # (e.g. GPU nodes) for particular workloads, like the DeepSpeed training
          # job.
          #
          # In this example, the tolerations are set to allow the DeepSpeed worker
          # pods to be scheduled on nodes with the specified taints (i.e., the node
          # pool with GPU resources). This ensures that the training job can
          # utilize the available GPU resources on those nodes, improving the
          # efficiency and performance of the training process.
          #
          # You can remove the taint tolerations if you do not have any taints on your cluster.
          tolerations:
          # Change the nodepool name in here
          - effect: NoSchedule
            key: nodepool
            operator: Equal
            value: nodepool-256ram32cpu2gpu-0
          # Taint toleration effect for GPU nodes
          - effect: NoSchedule
            key: nvidia.com/gpu
            operator: Equal
            value: present
          containers:
          # Container with the DeepSpeed training image built from the provided Dockerfile and the DeepSpeed support
          # Change your image name and version in here
          - image: <YOUR-DEEPSPEED-CONTAINER-NAME>:<VERSION>
            name: deepspeed-mpijob-container
            resources:
              limits:
                # Optional: varies to nodepool group 
                cpu: 16
                memory: 32Gi
                nvidia.com/gpu: 2
              requests:
                # Optional: varies to nodepool group
                cpu: 8
                memory: 16Gi
                nvidia.com/gpu: 1
```
这里和MPI Operator PR #567里不太一样的点：

- 因为 DeepSpeed 不仅需要MPI协议进行消息通信，还需要NCCL协议进行GPU通信，所以launch container和worker container都需要GPU资源；
- Command里的`-np`参数需要设置为`2`，因为DeepSpeed的`deepspeed_mpi`模式下，launch container和worker container都需要进行MPI通信，所以需要两个进程；
- Command里原有的`$@`会报错，所以也删除了；


## 参考

- [MPI Operator](https://www.github.com/kubeflow/mpi-operator)
- [DeepSpeed](https://www.deepspeed.ai/)
- [DeepSpeed + Kubernetes 如何轻松落地大规模分布式训练](https://developer.aliyun.com/article/1260610)
- [(integration) deepspeed_mpi specific container, deepspeed_config for MPI with nodetaints #567](https://github.com/kubeflow/mpi-operator/pull/567)