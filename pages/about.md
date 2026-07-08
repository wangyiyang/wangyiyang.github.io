---
layout: page
title: 关于
description: 我关注如何用 AI、代码、自动化和写作构建一套可持续演进的个人生产系统。
keywords: 王翊仰,一人公司,AI工程,自动化,技术写作
comments: true
menu: 关于
permalink: /about/
full_width: true
---

我是王翊仰。这个博客记录我作为独立开发者和一人公司实践者，如何把 AI、代码、自动化、写作和开源项目组织成一套长期运转的个人生产基础设施。

## 长期方向

- 用 AI 工程系统放大个人交付能力。
- 用自动化工具减少重复劳动。
- 用写作和复盘沉淀可复用的方法。
- 用开源项目验证工具、流程和产品想法。

## 生产系统

{% include theme/production-system.html %}

## 技术关键词

{% for skill in site.data.skills %}
### {{ skill.name }}
<div class="theme-tags">
{% for keyword in skill.keywords %}
<span class="theme-tag">{{ keyword }}</span>
{% endfor %}
</div>
{% endfor %}

## 联系

{% for website in site.data.social %}
- {{ website.sitename }}：[@{{ website.name }}]({{ website.url }})
{% endfor %}
- 微信公众号：**{{ site.components.qrcode.image_alt }}**

<div class="wechat-qr-wrap">
  <img src="{{ site.url }}/images/qrcode.jpg" alt="{{ site.components.qrcode.image_alt }}" class="wechat-qr-img" />
</div>
