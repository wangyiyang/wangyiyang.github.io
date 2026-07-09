---
name: notion-to-blog
description: >-
  将 Notion 页面自动转化为 Jekyll 博客文章并推送。
  工作流：运行 convert.py（全自动）→ 构建验证 → 推送 master。
  当用户给出 Notion 页面/数据库 URL 要求「转换为博客文章」时使用。
---

# Notion → Jekyll 博客文章转换

## 工作流

### 步骤 1：提取页面 ID

从 Notion URL 中提取 32 位 hex ID，转为 UUID 格式。

```
URL:  https://www.notion.so/...f13de73301f7403994c44210f6604a28?view=...
ID:   f13de733-01f7-4039-94c4-4210f6604a28
```

**判断类型：** 用 `GET /v1/pages/{uuid}` 判断是 page 还是 database。
- 返回 `title` 属性 → 单页，走步骤 2
- 返回 `"a database, not a page"` → 数据库视图

### 步骤 2：运行自动化脚本

```bash
.agents/skills/notion-to-blog/convert.py <page-uuid-or-url>
```

脚本自动完成全部操作：

1. 获取页面属性（标题、分类、摘要、发布日期）
2. 生成 slug 和文件路径
3. 获取 Markdown 内容
4. 提取并下载图片（自动处理 alt text 嵌套链接）
5. 处理 Notion 特有标记（`<callout>`→blockquote、`<empty-block/>`→空行）
6. 替换图片路径为本地路径
7. 组装 Front Matter
8. md5 去重验证图片
9. 自动 Jekyll 构建验证
10. 输出 git 推送命令

### 步骤 3：推送

```bash
git add -A _posts/ images/posts/{date}-{slug}/
git commit -m "feat: 新增博客文章「{title}」"
git push origin master
```

## 前置条件

```bash
export NOTION_API_TOKEN=$(cat ~/.config/notion/api_key 2>/dev/null)
```

## 关键约定

| 项目 | 规则 |
|---|---|
| 文件名 | `_posts/{发布日期}-{slug}.md` |
| 日期 | 从 Notion `计划发布日` 取，无则用今天 |
| 图片 | `images/posts/{slug}/01..N.{ext}` |
| Front Matter | `categories` 从 Notion `系列 / 标签` 提取 |
| Feature switch | 默认全部 `false`（固定模板） |

## 已知陷阱（convert.py 已自动处理）

- **图片 URL 提取** — 使用 `rfind('(')/rfind(')')` 而非简单 regex，兼容 alt text 嵌套链接
- **Callout 标签** — 自动移除 `<callout>`/`</callout>`，保留 `>` 引用
- **空段落** — `<empty-block/>` 替换为空行而非删除，防 blockquote 扩张
- **S3 URL 过期** — 每次重新拉取自动获得新签名 URL
- **图片顺序错乱** — 下载前清空目录，下载后 md5 去重校验
- **Jekyll 未来日期** — 如需当天可见用今天日期

## FAQ

### Q: 页面是数据库视图（URL 带 `?v=...`）

convert.py 会检测并提示。需要先查询子页面列表：

```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Notion-Version: 2022-06-28" \
  "https://api.notion.com/v1/databases/{uuid}/query"
```

对每个子页面分别运行 convert.py。

### Q: 需要重新拉取/更新

```bash
.agents/skills/notion-to-blog/convert.py <uuid>
```

脚本自动清空旧图片目录后重新下载。
