---
layout: categories
title: Categories
description: 哈哈，你找到了我的文章基因库
keywords: 分类
comments: false
menu: 分类
permalink: /categories/
---

<div class="archive-list">
{% assign sorted_categories = site.categories | sort %}
{% for category in sorted_categories %}
<h3 class="archive-year" id="{{ category[0] }}">{{ category | first }} <span class="archive-year-count">{{ category.last.size }} 篇</span></h3>
<ol class="console-list archive-posts">
{% for post in category.last %}
<li class="console-list-item archive-list-item">
    <article class="console-list-body">
        <h3 class="archive-row"><span class="archive-date">{{ post.date | date: "%y-%m-%d" }}</span><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h3>
    </article>
</li>
{% endfor %}
</ol>
{% endfor %}
</div>
