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
正确做法：使用 Python 按行查找，定位到行末的 `rfind('(')` 和 `rfind(')')`：

```python
# ✅ 正确：定位行末的 () 对，忽略 alt 中的嵌套链接
for line in lines:
    if '![' in line:
        start = line.rfind('(')
        end = line.rfind(')')
        url = line[start+1:end]
```

**下载图片（关键：务必保持 URL 顺序与文件名一一对应）：**

```python
# 用 Python 统一处理 URL 提取 → 下载 → 文件映射
# 不要用 bash while read 逐行下载，容易丢失顺序映射

import subprocess, hashlib, os

IMG_DIR = f'images/posts/{slug}'
os.makedirs(IMG_DIR, exist_ok=True)

# 1. 按 markdown 出现顺序提取所有图片 URL
urls = []
for line in lines:
    if '![' in line:
        start = line.rfind('(')
        end = line.rfind(')')
        if start != -1 and end != -1 and end > start:
            urls.append(line[start+1:end])

# 2. 逐一下载，文件名 = 序号（01, 02, ...）
for i, url in enumerate(urls):
    ext = 'png'
    if '.jpg' in url.lower() or '.jpeg' in url.lower():
        ext = 'jpg'
    elif '.gif' in url.lower():
        ext = 'gif'
    elif '.webp' in url.lower():
        ext = 'webp'
    filename = f'{i+1:02d}.{ext}'
    subprocess.run(['curl', '-sL', '-o', f'{IMG_DIR}/{filename}', url])

# 3. ⚠️ 关键验证：确保没有两张图内容相同（之前踩过的大坑）
hashes = {}
for filename in sorted(os.listdir(IMG_DIR)):
    path = os.path.join(IMG_DIR, filename)
    with open(path, 'rb') as f:
        h = hashlib.md5(f.read()).hexdigest()
    hashes[filename] = h

# 如果有重复，说明下载顺序错了，需要手动排查
for f1 in hashes:
    for f2 in hashes:
        if f1 < f2 and hashes[f1] == hashes[f2]:
            print(f'⚠️  {f1} 和 {f2} 内容相同！下载顺序可能错乱')
```

> **注意：** Notion S3 图片 URL 有时效性（约 1 小时）。每次重新拉取 markdown 后，S3 签名 URL 会变化，
> 必须重新下载 S3 托管的图片。Dev.to 等外部 CDN 图片 URL 通常稳定，无需重复下载。
> **重要：** 如果中途出错重试，务必先清空图片目录再重新下载，防止旧文件残留导致顺序错乱。

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

将远程图片 URL 按出现的顺序替换为本地路径。**必须使用同名顺序映射**，
确保第 N 个提取的 URL 被替换为 `{N:02d}.{ext}`。

```python
import re

# 用与下载时间样的顺序提取 URLs，保证映射一致
urls = []
for line in lines:
    if '![' in line:
        start = line.rfind('(')
        end = line.rfind(')')
        if start != -1 and end != -1 and end > start:
            urls.append(line[start+1:end])

# 按顺序替换（注意：必须先用 rfind 提取完整的 long URL 再匹配，避免部分匹配）
new_lines = []
for line in lines:
    if '![' in line:
        for idx, url in enumerate(urls):
            if url in line:  # 用完整 URL 做子串匹配，避免误匹配
                ext = 'png'
                if '.jpg' in url.lower() or '.jpeg' in url.lower():
                    ext = 'jpg'
                elif '.gif' in url.lower():
                    ext = 'gif'
                elif '.webp' in url.lower():
                    ext = 'webp'
                filename = f'{idx+1:02d}.{ext}'
                line = re.sub(r'\]\(https?://[^)]+\)',
                             f'](/images/posts/{slug}/{filename})', line)
                break
    new_lines.append(line)
```

> ⚠️ **注意：** S3 URL 的 query parameters 中可能包含 `+`、`/`、`=` 等字符，
> 这些字符在 shell 和 sed 中需要特殊处理。建议全程使用 Python 处理，避免 shell 转义问题。
> 如果中途重新拉取 markdown 后重新下载，务必先清空图片目录再执行，防止旧文件残留。

### 步骤 7：构建验证

```bash
cd <project-root>
bundle exec jekyll build 2>&1 | grep -E '(error|Warning|done)'
```

确认没有构建错误后，必须用浏览器工具打开页面检查渲染效果，重点关注：

1. **图片是否正确显示** — 检查每张图的内容是否匹配其上下文
2. **blockquote 范围是否正确** — 引用块没有吞噬后续标题
3. **md5 去重检查** — 确认生成的图片目录中没有重复文件：
   ```bash
   md5sum images/posts/{slug}/*.png | sort | uniq -d -w32
   ```
   如果有输出，说明有两张图相同，下载顺序出错。
4. **文件数量正确** — 图片数量应与 markdown 中的 `![](...)` 出现次数一致

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
Dev.to 等外部 CDN 图片通常稳定，无需每次重新下载。

### Q: 下载后两张图片内容相同 / md5 一致

原因：下载过程中 URL 提取或顺序映射出错，导致不同序号的文件下载了同一张图。
**解法：**
1. 清空图片目录后重新下载
2. 下载后执行 md5 去重检测
3. 确认每个文件的 URL 来源与行号对应正确

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

### Q: 重试后图片顺序错乱

原因：多次运行下载脚本时，旧图片文件未被清理，新文件写入后与旧文件混合。
**解法：** 每次重新拉取 markdown 后，先清空图片目录再重新下载：
```bash
rm -rf images/posts/{slug}/*
mkdir -p images/posts/{slug}
# 然后重新下载
```
