---
name: notion-to-blog
description: >-
  将 Notion 页面自动转化为 Jekyll 博客文章并推送。
  工作流：提取页面 ID → 运行 convert.sh（全自动：拉取内容、下载图片、生成文章）→ 构建验证 → 推送 master。
  当用户给出 Notion 页面/数据库 URL 要求「转换为博客文章」时使用。
---

# Notion → Jekyll 博客文章转换

## 工作流

### 步骤 1：提取页面 ID

从用户提供的 Notion URL 中提取 32 位 hex 页面 ID。

```
URL:  https://www.notion.so/...f13de73301f7403994c44210f6604a28?view=...
ID:   f13de73301f7403994c44210f6604a28
UUID: f13de733-01f7-4039-94c4-4210f6604a28
```

**判断类型：** 用 `GET /v1/pages/{uuid}` 判断是 page 还是 database。
- 返回 `"title"` 属性 → 单页，走步骤 2
- 返回 `"a database, not a page"` → 数据库视图，先 `POST /v1/databases/{uuid}/query` 获取子页面列表

### 步骤 2：运行自动化脚本

```bash
.agents/skills/notion-to-blog/convert.sh <page-uuid>
```

脚本自动完成以下所有操作：

1. **获取页面属性**（标题、分类、摘要、发布日期）
2. **生成 slug 和文件路径** — `_posts/{date}-{slug}.md` + `images/posts/{date}-{slug}/`
3. **获取 Markdown 内容** — 从 `/v1/pages/{uuid}/markdown`
4. **提取及下载图片** — 按行解析 `rfind('(')/rfind(')')` 提取 URL，逐一下载为 `01.png`、`02.png`...
5. **处理 Notion 特有标记** — `<callout>`→blockquote、`<empty-block/>`→空行
6. **替换图片路径** — 远程 URL → 本地 `/images/posts/{slug}/`
7. **组装 Front Matter** — 标题、分类、摘要、关键词
8. **md5 去重验证** — 确保无重复图片
9. **Jekyll 构建验证**

### 步骤 3：人工检查和推送

```bash
# 1. 检查文章
less _posts/{date}-{slug}.md

# 2. 确认图片目录
ls images/posts/{slug}/

# 3. 最终构建确认
bundle exec jekyll build 2>&1 | tail -3

# 4. 提交推送
git add -A _posts/ images/posts/{slug}/
git commit -m "feat: 新增博客文章「{标题}」"
git push origin master
```

## 前置条件

```bash
export NOTION_API_TOKEN=$(cat ~/.config/notion/api_key 2>/dev/null)
[ -z "$NOTION_API_TOKEN" ] && echo "❌ NOTION_API_TOKEN 未设置" && exit 1
```

## 关键约定

| 项目 | 规则 |
|---|---|
| 文件名 | `_posts/{计划发布日或今天}-{slug}.md` |
| 日期 | Jekyll 默认跳过未来文章，如需当天可见用今天日期 |
| 图片 | `images/posts/{slug}/01..N.{png\|jpg\|gif\|webp}` |
| Front Matter | `categories` 从 Notion `系列 / 标签` 提取 |
| Callout | `<callout>` → `>` blockquote |
| 空段落 | `<empty-block/>` → 空行（保留段落分隔） |

## 已知陷阱（convert.sh 已自动处理）

- **图片 URL 提取** — alt text 中可能含 `[dev.to](http://dev.to)` 嵌套链接，
  脚本用 `line.rfind('(')/rfind(')')` 定位真正的图片 URL 而非简单 regex
- **Callout 标签** — 自动移除 `<callout>`/`</callout>`，保留内部 `>`
- **空段落** — 替换为空行而非删除，防 blockquote 扩张
- **S3 URL 过期** — 每次重新拉取 markdown 后 S3 签名变化，脚本自动刷新
- **图片顺序错乱** — 下载前清空目录，下载后 md5 去重校验

## FAQ

### Q: 页面是数据库视图（URL 带 `?v=...`）

先 `GET /v1/databases/{id}` 确认，再 `POST /v1/databases/{id}/query` 获取子页面列表，
对每个子页面分别运行 convert.sh。

### Q: 需要重新拉取

```bash
# 清空旧文件再运行，防止残留
rm -rf images/posts/{slug}/
.agents/skills/notion-to-blog/convert.sh <uuid>
```

### Q: 需要更新已有文章

重新运行 convert.sh，它会覆盖同名的 `_posts/{date}-{slug}.md` 和 `images/posts/{slug}/`。
