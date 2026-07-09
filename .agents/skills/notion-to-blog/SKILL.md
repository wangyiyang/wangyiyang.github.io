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

- `NOTION_API_TOKEN` 已配置（`~/.config/notion/api_key` 或环境变量）

### 验证认证

```bash
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
https://www.notion.so/wangyiyangcc/...f13de73301f7403994c44210f6604a28?view=...
```

页面 ID 是 URL 路径中 32 位 hex 字符串，API 调用时需加连字符：
`f13de733-01f7-4039-94c4-4210f6604a28`

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
# 1. 获取数据库详情
curl -s -H "Authorization: Bearer $TOKEN" \
  -H "Notion-Version: 2022-06-28" \
  "https://api.notion.com/v1/databases/{database-id}"

# 2. 查询数据库所有页面
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Notion-Version: 2022-06-28" \
  "https://api.notion.com/v1/databases/{database-id}/query" -d '{}'
```

**获取页面 Markdown 内容：**

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  -H "Notion-Version: 2022-06-28" \
  "https://api.notion.com/v1/pages/{page-id}/markdown" | \
  python3 -c "import json, sys; print(json.load(sys.stdin)['markdown'])"
```

### 步骤 2：提取并下载图片

**⚠️ 注意图片 URL 提取的陷阱：**

Notion 的 markdown 导出中，图片 alt text 可能包含嵌套的 markdown 链接（如 `[dev.to](http://dev.to)`），
使用简单 regex `!\[.*?\]\(([^)]+)\)` 会因为嵌套 `)` 而截断 URL。
正确做法：使用 Python 按行查找，定位到行末的 `)()` 对。

```python
with open('/tmp/markdown.md') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if '![' in line:
        # 取最后一个 ( 到最后一个 ) 之间的内容（忽略 alt 中的嵌套 link）
        start = line.rfind('(')
        end = line.rfind(')')
        url = line[start+1:end]
        # 识别图片类型
        if 'prod-files-secure.s3' in url:
            img_type = 'cover / 内部图片'
        elif 'dev.to' in url:
            img_type = 'Dev.to 外部图'
        # ...
```

**下载图片到指定目录：**

```bash
IMG_DIR="images/posts/{文章slug}"
mkdir -p "$IMG_DIR"
i=1
while read -r url; do
  case "$url" in
    *.png?*|*.png)  ext="png" ;;
    *.jpeg?*|*.jpg?*) ext="jpg" ;;
    *.gif?*|*.gif)  ext="gif" ;;
    *.webp?*|*.webp) ext="webp" ;;
    *)              ext="png" ;;
  esac
  filename="$(printf '%02d' $i).${ext}"
  curl -sL -o "${IMG_DIR}/${filename}" "$url"
  i=$((i+1))
done < /tmp/img_urls.txt
```

> **注意：** Notion S3 图片 URL 有时效性（约 1 小时）。每次重新拉取 markdown 后，S3 签名 URL 会变化，
> 必须重新下载 S3 托管的图片。Dev.to 等外部 CDN 图片 URL 通常稳定，无需重复下载。

### 步骤 3：处理 Notion 特有标记

Notion 的 markdown 导出包含非标准标记，必须处理：

#### 3.1 `<callout>` 标签 → markdown 引用块

Notion 的 callout 块导出为 `<callout icon="..." color="...">` 自定义 HTML 标签，**浏览器不识别**。
必须将其转换为标准 markdown blockquote：

```python
# 输入：
# <callout icon="💡" color="gray_bg">
# 	> **关键边界**：内容...
# </callout>

# 处理：移除 <callout> 和 </callout> 行，保留 > 内容
cleaned = []
for line in lines:
    stripped = line.strip()
    if stripped.startswith('<callout') or stripped == '</callout>':
        continue  # 移除 callout 标签
    if stripped.startswith('>'):
        line = line.lstrip('\t').lstrip()  # 清理 > 前的制表符
    cleaned.append(line)
```

#### 3.2 `<empty-block/>` → 空行

Notion 的空段落导出为 `<empty-block/>`，**必须替换为空行而非直接删除**，
否则 blockquote 和紧接的标题之间没有空行分隔，会导致引用范围扩张。

```python
# ✅ 正确：替换为空行
if stripped == '<empty-block/>':
    cleaned.append('')  # 保留段落分隔
    continue

# ❌ 错误：直接删除（导致 blockquote 吞噬后续标题）
# continue  # 不要这样做！
```

#### 3.3 图片 alt text 为空

Notion 可能导出 `![](...)`（空 alt），这是正常现象，保留原样即可。

### 步骤 4：生成文章文件名

```
_posts/{日期}-{kebab-title}.md
```

日期 = `计划发布日` 或当前日期。注意 Jekyll 默认不构建未来日期的文章（需要 `--future` 标志或在 `_config.yml` 中设置 `future: true`）。

### 步骤 5：生成 Front Matter

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

> **注意：** `layout: post` 和 feature switch 是固定模板字段，即使 Notion 中没有对应属性，也保留默认值 `false`。

### 步骤 6：替换 Markdown 中的图片路径

将远程图片 URL 按顺序替换为本地路径。由于 markdown 中 alt text 可能含嵌套链接，
**不要使用简单的 sed 字符串替换**，应逐行按 URL 特征匹配：

```python
import re

url_mappings = [
    (r'https://prod-files-secure\.s3\.us-west-2\.amazonaws\.com[^)]+', '01.png'),
    (r'https://media2\.dev\.to/dynamic/image/[^)]*gw11kx[^)]+\.png', '02.png'),
    (r'https://media2\.dev\.to/dynamic/image/[^)]*knk0m1[^)]+\.png', '03.png'),
    # ...
]

new_lines = []
for line in lines:
    for pattern, filename in url_mappings:
        if re.search(pattern, line):
            line = re.sub(r'\]\(https://[^)]+\)',
                         f'](/images/posts/{slug}/{filename})', line)
    new_lines.append(line)
```

### 步骤 7：构建验证

```bash
cd <project-root>
bundle exec jekyll build 2>&1 | grep -E '(error|Warning|done)'
```

确认没有构建错误后，建议用浏览器工具打开页面检查渲染效果，重点关注：
- 图片是否显示（alt text 正常）
- blockquote 是否范围正确（没有吞噬标题）
- 页面布局是否正常

## 完整脚本

参考项目 `.agents/skills/notion-to-blog/convert.sh`。

## 常见问题

### Q: Notion API 返回 400 "Invalid request URL"

页面 ID 需要用标准 UUID 格式（带连字符）：
`f13de73301f7403994c44210f6604a28` → `f13de733-01f7-4039-94c4-4210f6604a28`

### Q: 页面显示为数据库

URL 中的 ID 可能是数据库 ID 而非页面 ID。用 `GET /v1/databases/{id}` 确认类型，
然后 `POST /v1/databases/{id}/query` 获取子页面列表。

### Q: 图片下载失败

Notion S3 图片 URL 有时效性（约 1 小时），重新拉取 markdown 获得新签名 URL。
Dev.to 等外部 CDN 图片通常稳定。

### Q: `ntn api` 不支持某些端点

`ntn` CLI 对未注册的端点不支持。直接使用 `curl` 调用 Notion REST API。

### Q: 图片 URL 提取被 alt text 中的 markdown 链接打断

当 alt text 包含 `[dev.to](http://dev.to)` 时，简单 regex `!\[.*?\]\(([^)]+)\)` 
会错误匹配到嵌套的 `)`。解法：对每行取 `rfind('(')` 和 `rfind(')')` 定位真正的图片 URL。

### Q: 渲染后 blockquote 范围异常扩张

原因：`<empty-block/>` 被直接删除而非替换为空行，导致 blockquote 和后续标题间没有空行。
解法：`<empty-block/>` → `''`（空行），确保 blockquote 被正确终止。

### Q: 渲染后出现原始 HTML `<callout>` 标签

原因：Notion 导出的 `<callout>` 自定义标签未被处理。
解法：移除 `<callout>` 和 `</callout>` 行，保留内部 `>` 引用内容。
