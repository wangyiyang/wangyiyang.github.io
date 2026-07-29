---
layout: page
title: 归档
description: 按年份归档
keywords: 归档
comments: false
menu: 文章
permalink: /archives/
---

<div class="archive-list">
{% assign count = 1 %}
{% for post in site.posts reversed %}
    {% assign year = post.date | date: '%Y' %}
    {% assign nyear = post.next.date | date: '%Y' %}
    {% if year != nyear %}
        {% assign count = count | append: ', ' %}
        {% assign counts = counts | append: count %}
        {% assign count = 1 %}
    {% else %}
        {% assign count = count | plus: 1 %}
    {% endif %}
{% endfor %}

{% assign counts = counts | split: ', ' | reverse %}
{% assign i = 0 %}

{% assign thisyear = 1 %}

{% for post in site.posts %}
    {% assign year = post.date | date: '%Y' %}
    {% assign nyear = post.next.date | date: '%Y' %}
    {% if year != nyear %}
        {% if thisyear != 1 %}
            </ol>
        {% endif %}
<h3 class="archive-year">{{ post.date | date: '%Y' }} <span class="archive-year-count">{{ counts[i] }} 篇</span></h3>
        {% if thisyear != 0 %}
            {% assign thisyear = 0 %}
        {% endif %}
        <ol class="console-list archive-posts">
        {% assign i = i | plus: 1 %}
    {% endif %}
<li class="console-list-item archive-list-item">
    <article class="console-list-body">
        <h3 class="archive-row"><span class="archive-date">{{ post.date | date: "%m-%d" }}</span><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h3>
    </article>
</li>
{% endfor %}

</ol>
</div>
