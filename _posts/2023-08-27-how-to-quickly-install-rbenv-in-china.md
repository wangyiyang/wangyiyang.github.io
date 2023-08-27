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





