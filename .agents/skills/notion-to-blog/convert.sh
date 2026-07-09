#!/usr/bin/env bash
# ntn-to-blog — 将 Notion 页面转换为 Jekyll 博客文章
# 用法: ./convert.sh <notion-page-url>
# 示例: ./convert.sh "https://www.notion.so/wangyiyangcc/...page-id..."
set -euo pipefail

# === 配置 ===
TOKEN_FILE="$HOME/.config/notion/api_key"
BLOG_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"  # 项目根目录

# === 辅助函数 ===
die() { echo "❌ $*" >&2; exit 1; }
info() { echo "ℹ️  $*"; }
ok()   { echo "✅ $*"; }
build() { echo ""; echo "🔨 构建验证..."; cd "$BLOG_ROOT" && bundle exec jekyll build 2>&1 | tail -3; echo ""; }

# === 1. 认证 ===
[ -f "$TOKEN_FILE" ] || die "Notion token 文件不存在: $TOKEN_FILE"
TOKEN=$(cat "$TOKEN_FILE")
[ -n "$TOKEN" ] || die "Notion token 为空"
ok "Notion API token 已就绪"

# === 1b. 判断是 URL 还是 UUID ===
INPUT="$1"
if echo "$INPUT" | grep -qP '^[a-f0-9\-]{36}$'; then
  # 输入已是 UUID
  PAGE_ID="$INPUT"
elif echo "$INPUT" | grep -qP '[a-f0-9]{32}'; then
  # 从完整 URL 提取
  PAGE_ID_RAW=$(echo "$INPUT" | grep -oP '[a-f0-9]{32}' | head -1)
  PAGE_ID="${PAGE_ID_RAW:0:8}-${PAGE_ID_RAW:8:4}-${PAGE_ID_RAW:12:4}-${PAGE_ID_RAW:16:4}-${PAGE_ID_RAW:20:12}"
else
  die "无法从输入提取页面 ID: $INPUT"
fi
info "页面 ID: $PAGE_ID"

# === 1c. 验证是 page 还是 database ===
TYPE_CHECK=$(curl -sf -H "Authorization: Bearer $TOKEN" \
  -H "Notion-Version: 2022-06-28" \
  "https://api.notion.com/v1/pages/$PAGE_ID" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if data.get('object') == 'error':
        print(data.get('message',''))
    else:
        print('page')
except:
    print('unknown')")

if [ "$TYPE_CHECK" != "page" ]; then
  if echo "$TYPE_CHECK" | grep -qi "database"; then
    die "这是一个 database！请先 POST /v1/databases/\${PAGE_ID}/query 获取子页面列表"
  else
    die "API 返回错误: $TYPE_CHECK"
  fi
fi

# === 3. 获取页面属性 ===
info "获取页面属性..."
PAGE_JSON=$(curl -sf -H "Authorization: Bearer $TOKEN" \
  -H "Notion-Version: 2022-06-28" \
  "https://api.notion.com/v1/pages/$PAGE_ID") || die "获取页面失败"

TITLE=$(echo "$PAGE_JSON" | python3 -c "
import json, sys
data = json.load(sys.stdin)
props = data.get('properties', {})
title_field = props.get('title', {}).get('title', [])
print(title_field[0]['plain_text'] if title_field else 'Untitled')
")
CATEGORIES=$(echo "$PAGE_JSON" | python3 -c "
import json, sys
data = json.load(sys.stdin)
props = data.get('properties', {})
for name, val in props.items():
    t = val.get('type', '')
    if t == 'multi_select' and ('系列' in name or '标签' in name):
        tags = [item['name'] for item in val.get('multi_select', [])]
        print(','.join(tags))
        break
")
DESC=$(echo "$PAGE_JSON" | python3 -c "
import json, sys
data = json.load(sys.stdin)
props = data.get('properties', {})
for name, val in props.items():
    t = val.get('type', '')
    if t == 'rich_text' and ('摘要' in name or '观点' in name):
        texts = [t['plain_text'] for t in val.get('rich_text', [])]
        print(''.join(texts)[:200])
        break
")
PUB_DATE=$(echo "$PAGE_JSON" | python3 -c "
import json, sys
data = json.load(sys.stdin)
props = data.get('properties', {})
for name, val in props.items():
    t = val.get('type', '')
    if t == 'date' and ('发布' in name):
        d = val.get('date', {})
        print(d.get('start', '') if d else '')
        break
" || echo "")

[ -z "$PUB_DATE" ] && PUB_DATE=$(date +%Y-%m-%d)

ok "标题: $TITLE"
ok "分类: $CATEGORIES"
ok "发布日期: $PUB_DATE"

# === 4. 生成文件名和目录 ===
SLUG=$(echo "$TITLE" | python3 -c "
import sys, re
t = sys.stdin.read().strip()
eng = re.findall(r'[a-zA-Z]+', t)
if eng:
    print('-'.join(eng).lower()[:60])
else:
    print(t[:12])
" | sed 's/[^a-zA-Z0-9-]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//')
[ -z "$SLUG" ] && SLUG="post-$(date +%Y%m%d)"

POST_FILE="_posts/${PUB_DATE}-${SLUG}.md"
IMG_DIR="images/posts/${PUB_DATE}-${SLUG}"

info "文章文件: $POST_FILE"
info "图片目录: $IMG_DIR"

# === 5. 获取 Markdown 内容 ===
info "获取 Markdown 内容..."
MARKDOWN=$(curl -sf -H "Authorization: Bearer $TOKEN" \
  -H "Notion-Version: 2022-06-28" \
  "https://api.notion.com/v1/pages/$PAGE_ID/markdown" | \
  python3 -c "import json, sys; print(json.load(sys.stdin)['markdown'])") || die "获取 Markdown 失败"
ok "Markdown 内容已获取（${#MARKDOWN} 字符）"

# === 6. 提取图片 URL（Python 方式，正确处理 alt text 中的嵌套链接）===
info "提取图片 URL..."
IMG_URLS=$(echo "$MARKDOWN" | python3 -c "
import sys, re
lines = sys.stdin.read().split('\n')
urls = []
for line in lines:
    if '![' in line:
        start = line.rfind('(')
        end = line.rfind(')')
        if start != -1 and end != -1 and end > start:
            url = line[start+1:end]
            urls.append(url)
for u in urls:
    print(u)
")

echo "$IMG_URLS" > /tmp/notion_blog_img_urls.txt
IMG_COUNT=$(echo "$IMG_URLS" | grep -c '.' || true)
info "发现 $IMG_COUNT 张图片"

# === 7. 下载图片 ===
info "下载配图..."
IMG_DIR_FULL="${BLOG_ROOT}/${IMG_DIR}"

# ⚠️  每次重新拉取后先清空目录，防止旧文件残留导致顺序错乱
rm -rf "$IMG_DIR_FULL"
mkdir -p "$IMG_DIR_FULL"

i=1
while IFS= read -r url; do
  [ -z "$url" ] && continue
  case "$url" in
    *.png?*|*.png)    ext="png" ;;
    *.jpeg?*|*.jpg?*|*.jpeg|*.jpg) ext="jpg" ;;
    *.gif?*|*.gif)    ext="gif" ;;
    *.webp?*|*.webp)  ext="webp" ;;
    *)                ext="png" ;;
  esac
  filename="$(printf '%02d' $i).${ext}"
  if curl -sfL -o "${IMG_DIR_FULL}/${filename}" "$url"; then
    size=$(wc -c < "${IMG_DIR_FULL}/${filename}")
    info "  [$i/$IMG_COUNT] $filename (${size} bytes)"
  else
    info "  ⚠️  [$i/$IMG_COUNT] $filename 下载失败"
  fi
  i=$((i+1))
done < /tmp/notion_blog_img_urls.txt

ok "配图下载完成 (共 $((i-1)) 张)"

# === 7b. md5 去重验证（覆盖所有图片格式）===
info "验证图片唯一性..."
DUPS=$(find "$IMG_DIR_FULL" -type f \( -name '*.png' -o -name '*.jpg' -o -name '*.jpeg' -o -name '*.gif' -o -name '*.webp' \) -exec md5sum {} \; | sort | uniq -d -w32)
if [ -n "$DUPS" ]; then
  echo "$DUPS"
  die "存在 md5 重复的图片！下载顺序可能出错"
fi
ok "所有图片内容唯一"

# 显示文件列表供核对
ls -la "$IMG_DIR_FULL/"

# === 8. 处理 Notion 特有标记并替换图片路径 ===
TEMP_MD=$(mktemp)
echo "$MARKDOWN" > "$TEMP_MD"

# 8a. 用 Python 处理 Notion 标记和图片替换
python3 << PYEOF
import re, sys, os

slug = "${PUB_DATE}-${SLUG}"
with open("$TEMP_MD", 'r') as f:
    md = f.read()

lines = md.split('\n')

# 收集图片 URL（用 rfind 确保正确提取，无视 alt 中的嵌套链接）
img_urls = []
for line in lines:
    if '![' in line:
        start = line.rfind('(')
        end = line.rfind(')')
        if start != -1 and end != -1 and end > start:
            img_urls.append(line[start+1:end])

assert len(img_urls) > 0, '未找到任何图片 URL'

# 处理每一行
cleaned = []
for line in lines:
    stripped = line.strip()
    
    # 8a-1: 移除 <callout> 标签
    if stripped.startswith('<callout') or stripped == '</callout>':
        continue
    # 8a-2: 清理 callout 内容前的制表符（保留 >）
    if stripped.startswith('>'):
        line = line.lstrip('\t').lstrip()
    # 8a-3: <empty-block/> 替换为空行（保留段落分隔，防 blockquote 扩张）
    if stripped == '<empty-block/>':
        cleaned.append('')
        continue
    # 8a-4: 替换图片 URL 为本地路径（以完整 URL 子串匹配，避免误匹配）
    if '![' in line:
        for idx, url in enumerate(img_urls):
            if url in line:
                ext = 'png'
                if '.jpg' in url.lower() or '.jpeg' in url.lower():
                    ext = 'jpg'
                elif '.gif' in url.lower():
                    ext = 'gif'
                elif '.webp' in url.lower():
                    ext = 'webp'
                filename = f'{idx+1:02d}.{ext}'
                line = re.sub(r'\]\(https?://[^)]+\)',
                             f'](/images/posts/{slug}/{filename})',
                             line)
                break
    cleaned.append(line)

new_md = '\n'.join(cleaned)
with open("$TEMP_MD", 'w') as f:
    f.write(new_md)

img_replaced = new_md.count('/images/posts/')
print(f"已替换 {img_replaced} 张图片路径")
PYEOF

# === 9. 组装文章 ===
KEYWORDS="${CATEGORIES//,/，}"
[ -n "$DESC" ] && KEYWORDS="${KEYWORDS}，${DESC:0:50}"

POST_BODY=$(cat "$TEMP_MD")
rm -f "$TEMP_MD"

cat > "${BLOG_ROOT}/${POST_FILE}" <<POSTEOF
---
layout: post
title: ${TITLE}
categories: [${CATEGORIES}]
description: ${DESC}
keywords: ${KEYWORDS}
mermaid: false
sequence: false
flow: false
mathjax: false
mindmap: false
mindmap2: false
---

${POST_BODY}
POSTEOF

ok "文章已生成: ${BLOG_ROOT}/${POST_FILE}"
ok "配图位置: ${BLOG_ROOT}/${IMG_DIR}/"

# === 10. 自动构建验证 ===
build

echo ""
echo "📋 下一步："
echo "  确认无误后提交推送:"
echo "    git add -A _posts/ images/posts/${PUB_DATE}-${SLUG}/"
echo "    git commit -m \"feat: 新增博客文章「${TITLE}」\""
echo "    git push origin master"
