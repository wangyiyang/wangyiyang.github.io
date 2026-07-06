---
name: notion-to-blog
description: >-
  将 Notion 页面转化为 Jekyll 博客文章。从 Notion API 读取页面 Markdown 内容，
  下载所有配图到 images/posts/ 目录，生成符合项目规范的 _posts/ 文章文件。
  当用户给出 Notion 页面/数据库 URL，要求「转换为博客文章」「导出为博客」「发到博客」
  时使用。URL 格式如 https://www.notion.so/xxx/...page-id?view=...
---

# Notion → Jekyll 博客文章转换

## 前提条件

- `ntn` CLI 已安装（`which ntn`）
- `NOTION_API_TOKEN` 已配置（`~/.config/notion/api_key` 或环境变量）

### 验证认证

```bash
# 检查 token 是否可用
export NOTION_API_TOKEN=$(cat ~/.config/notion/api_key 2>/dev/null)
if [ -z "$NOTION_API_TOKEN" ]; then
  echo "❌ NOTION_API_TOKEN 未设置"
  exit 1
fi
echo "✅ Notion API token 已就绪"
```

## 工作流

### 步骤 1：获取 Notion 页面内容

从用户提供的 Notion URL 中提取页面 ID：

```
https://www.notion.so/wangyiyangcc/...f13de73301f7403994c44210f6604a28...
```

页面 ID 是 URL 中 `...` 和 `?` 之间的 32 位 hex 字符串（或下划线连接的两个 32 位 hex），
实际 API 调用时需加连字符：`f13de733-01f7-4039-94c4-4210f6604a28`

**获取页面属性（含标题、分类、摘要等 Front Matter 信息）：**

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  -H "Notion-Version: 2022-06-28" \
  "https://api.notion.com/v1/pages/{page-id}" | python3 -c "
import json, sys
data = json.load(sys.stdin)
props = data.get('properties', {})
for name, val in props.items():
    print(json.dumps({name: val}, ensure_ascii=False))
"
```

关键属性映射（供 Front Matter 使用）：

| Notion 属性 | Front Matter 字段 | 处理方式 |
|---|---|---|
| 标题 (title) | `title` | 取第一个 title plain_text |
| 系列 / 标签 (multi_select) | `categories` | 取所有 name 值 |
| 摘要 / 核心观点 (rich_text) | `description` | 取全部 plain_text 拼接 |
| 总结 (rich_text) | `keywords` | 取内容并拼接 tags |
| 计划发布日 (date) | 文件名日期 | 取 date.start 作为文件前缀 |

> **注意：** 需要先验证页面 ID 对应的是 page 还是 database。用 `GET /v1/pages/{page-id}` 时，
> 如果返回 `"object": "error"` 且提示 `a page, not a database`，说明 ID 正确。
> 如果提示 `a database, not a page`，则这是数据库视图，需要先查询数据库来获取其中的子页面列表。

**处理数据库视图（多篇文章）：**

当用户给出的 URL 指向一个数据库视图（URL 中包含 `?v=...`），先查询数据库获取所有文章：

```bash
# 1. 先获取数据库详情
curl -s -H "Authorization: Bearer $TOKEN" \
  -H "Notion-Version: 2022-06-28" \
  "https://api.notion.com/v1/databases/{database-id}"

# 2. 查询数据库中所有页面
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Notion-Version: 2022-06-28" \
  "https://api.notion.com/v1/databases/{database-id}/query" \
  -d '{}'
```

**获取页面 Markdown 内容：**

```bash
# 获取单页内容
curl -s -H "Authorization: Bearer $TOKEN" \
  -H "Notion-Version: 2022-06-28" \
  "https://api.notion.com/v1/pages/{page-id}/markdown" | \
  python3 -c "import json, sys; print(json.load(sys.stdin)['markdown'])"
```

### 步骤 2：提取并下载图片

从 Markdown 中提取所有 `![](url)` 图片引用，下载到本地：

```bash
# 提取图片 URL 列表
extract_images() {
  local markdown="$1"
  echo "$markdown" | grep -oP '!\[.*?\]\(\K[^)]+' 
}

# 下载图片到指定目录
download_images() {
  local img_dir="$1"
  mkdir -p "$img_dir"
  local i=1
  while read -r url; do
    case "$url" in
      *.png?*)  ext="png" ;;
      *.jpeg?*|*.jpg?*) ext="jpeg" ;;
      *.gif?*)  ext="gif" ;;
      *.webp?*) ext="webp" ;;
      *)        ext="png" ;;
    esac
    local filename="$(printf '%02d' $i).${ext}"
    echo "⬇️  下载 $filename ..."
    curl -sL -o "${img_dir}/${filename}" "$url"
    i=$((i+1))
  done
}
```

### 步骤 3：生成文章文件名

文章文件命名规则：`_posts/{日期}-{kebab-title}.md`

```
日期 = plan_publish_date 或当前日期
kebab-title = 标题转英文小写连字符（从标题拼音或英文提取）
```

Fallback：如果标题是全中文，用标题的拼音首字母或直接使用关键英文词。

### 步骤 4：生成 Front Matter

```yaml
---
layout: post
title: {Notion 标题}
categories: [{系列/标签列表}]
description: {摘要/核心观点（最多 200 字）}
keywords: {标签 + 关键词}
mermaid: false
sequence: false
flow: false
mathjax: false
mindmap: false
mindmap2: false
---
```

> **注意：** Front Matter 中的 `layout: post` 和末尾的 feature switch 是固定的模板字段，
> 即使 Notion 中没有对应的属性，也应保留默认值 `false`。其他字段优先从 Notion 属性中提取。

### 步骤 5：替换 Markdown 中的图片路径

将 Markdown 中所有 `![](https://prod-files-secure.s3.aws...)` 替换为：
```
![](/images/posts/{文章目录名}/{filename})
```

第一张图片放在文章开头 Front Matter 之后作为题图/封面。

### 步骤 6：构建验证

```bash
cd <project-root>
bundle exec jekyll build 2>&1 | grep -E '(error|Warning|done)'
```

确认没有构建错误。

### 完整脚本示例

完整的转换脚本参考项目 `.agents/skills/notion-to-blog/convert.sh`。

## 常见问题

### Q: Notion API 返回 400 "Invalid request URL"

页面 ID 需要用标准 UUID 格式（带连字符）：
- 从 URL 提取：`f13de73301f7403994c44210f6604a28` → `f13de733-01f7-4039-94c4-4210f6604a28`

### Q: 页面显示为数据库

URL 中的 ID 可能是数据库 ID 而非页面 ID。先用 `GET /v1/databases/{id}` 确认类型，
然后通过 `POST /v1/databases/{id}/query` 获取子页面列表，再逐个处理每个子页面。

### Q: 图片下载失败

Notion 的 S3 图片 URL 有时效性（通常 1 小时）。如果在同一个会话中反复获取图片
失败，重新拉取一次 Markdown 内容获取新的签名的 URL。

### Q: `ntn api` 不支持 database query 端点

`ntn api` 的已知端点列表中没有 `POST /v1/databases/{id}/query`。这种情况下
应直接使用 `curl` 调用 Notion REST API，不要强行用 `ntn api`。
