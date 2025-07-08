# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个基于 Jekyll 的个人技术博客网站，使用 GitHub Pages 进行部署。博客主要发布关于编程、技术架构、AI/ML 相关的文章。

## 核心架构

### 目录结构
- `_posts/` - 已发布的博客文章（Markdown 格式）
- `_drafts/` - 草稿文章
- `_wiki/` - Wiki 页面
- `_fragments/` - 短文片段
- `_layouts/` - 页面布局模板
- `_includes/` - 可重用的页面组件
- `_data/` - 数据文件（技能、社交媒体等）
- `assets/` - 静态资源（CSS、JS、图片）
- `images/` - 文章图片资源
- `pages/` - 独立页面
- `_site/` - Jekyll 生成的静态网站文件（不要修改）

### 配置文件
- `_config.yml` - Jekyll 主配置文件，包含站点信息、插件配置、评论系统等
- `Gemfile` - Ruby 依赖管理
- `Makefile` - 构建和部署脚本
- `package.json` - Node.js 依赖（主要用于百度推送）

## 开发命令

### 本地开发
```bash
# 启动本地服务器
make serve
# 或者
bundle exec jekyll serve

# 构建网站
make build
# 或者
bundle exec jekyll build

# 清理生成的文件
make clean
# 或者
bundle exec jekyll clean
```

### 部署相关
```bash
# 百度推送（SEO）
npm run baiduPush

# 同步文件到 CDN（七牛云）
make syncfile
```

## 内容创建规范

### 博客文章模板
文章文件名格式：`YYYY-MM-DD-title.md`
Front Matter 必须包含：
```yaml
---
layout: post
title: 文章标题
categories: [分类1, 分类2]
description: 简短描述
keywords: 关键词1, 关键词2
mermaid: false
sequence: false
flow: false
mathjax: false
mindmap: false
mindmap2: false
---
```

### Wiki 页面模板
```yaml
---
layout: wiki
title: 页面标题
cate1: 
cate2: 
description: 页面描述
keywords: 关键词
type: 
link: 
mermaid: false
sequence: false
flow: false
mathjax: true
mindmap: true
mindmap2: true
---
```

## 技术栈

- **静态网站生成器**: Jekyll (~3.9.5)
- **部署平台**: GitHub Pages
- **主题**: 基于 DONGChuan 主题的自定义修改
- **评论系统**: Giscus（GitHub Discussions）
- **搜索**: Simple Jekyll Search
- **分析**: Google Analytics
- **CDN**: 七牛云（可选）

## 重要配置

### 站点信息
- URL: https://www.wangyiyang.cc
- 标题: 翊行代码
- 副标题: 翊码行远，仰观星辰 ——用代码丈量世界，以仰望探索未知

### 功能开关
- 分享功能: 禁用
- 不蒜子统计: 禁用
- 侧边栏项目展示: 启用
- 文章字数统计: 启用
- 二维码展示: 启用
- 灯箱效果: 禁用

## 常见任务

### 添加新文章
1. 在 `_posts/` 目录创建新的 Markdown 文件
2. 使用正确的文件名格式和 Front Matter
3. 图片放在 `images/posts/文章标题/` 目录下

### 修改网站配置
主要配置都在 `_config.yml` 文件中，包括：
- 个人信息
- 导航菜单
- 评论系统
- 插件配置

### 自定义样式
- 主样式文件: `assets/css/style.css`
- 日系极客主题: `assets/css/japanese-geek-theme.css`
- 组件样式: `assets/css/components/`

## 依赖管理

### Ruby 依赖
```bash
bundle install  # 安装依赖
bundle update   # 更新依赖
```

### Node.js 依赖
```bash
npm install     # 安装依赖（主要用于百度推送功能）
```

## 注意事项

- 所有文章图片应放在 `images/posts/` 对应目录下
- 修改配置后需要重新构建网站
- 本地开发时使用 `make serve` 启动服务器
- 不要直接修改 `_site/` 目录下的文件
- 提交前确保本地构建成功