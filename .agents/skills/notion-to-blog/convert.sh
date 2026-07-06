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

# === 1. 认证 ===
[ -f "$TOKEN_FILE" ] || die "Notion token 文件不存在: $TOKEN_FILE"
TOKEN=$(cat "$TOKEN_FILE")
[ -n "$TOKEN" ] || die "Notion token 为空"
ok "Notion API token 已就绪"

# === 2. 从 URL 提取页面 ID ===
URL="$1"
PAGE_ID_RAW=$(echo "$URL" | grep -oP '[a-f0-9]{32}' | head -1)
[ -n "$PAGE_ID_RAW" ] || die "无法从 URL 提取页面 ID: $URL"
# 转为 UUID 格式
PAGE_ID="${PAGE_ID_RAW:0:8}-${PAGE_ID_RAW:8:4}-${PAGE_ID_RAW:12:4}-${PAGE_ID_RAW:16:4}-${PAGE_ID_RAW:20:12}"
info "页面 ID: $PAGE_ID"

# === 3. 获取页面属性 ===
info "获取页面属性..."
PAGE_JSON=$(curl -sf -H "Authorization: Bearer $TOKEN" \
  -H "Notion-Version: 2022-06-28" \
  "https://api.notion.com/v1/pages/$PAGE_ID") || die "获取页面失败"

# 提取关键属性
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
    if val.get('type') == 'multi_select' and '系列' in name or '标签' in name:
        tags = [item['name'] for item in val.get('multi_select', [])]
        print(','.join(tags))
        break
")
DESC=$(echo "$PAGE_JSON" | python3 -c "
import json, sys
data = json.load(sys.stdin)
props = data.get('properties', {})
for name, val in props.items():
    if val.get('type') == 'rich_text' and ('摘要' in name or '观点' in name):
        texts = [t['plain_text'] for t in val.get('rich_text', [])]
        print(''.join(texts)[:200])
        break
")
PUB_DATE=$(echo "$PAGE_JSON" | python3 -c "
import json, sys
data = json.load(sys.stdin)
props = data.get('properties', {})
for name, val in props.items():
    if val.get('type') == 'date' and ('发布' in name):
        d = val.get('date', {})
        print(d.get('start', '') if d else '')
        break
" || echo "")

if [ -z "$PUB_DATE" ]; then
  PUB_DATE=$(date +%Y-%m-%d)
fi

ok "标题: $TITLE"
ok "分类: $CATEGORIES"
ok "发布日期: $PUB_DATE"

# === 4. 生成文件名和目录 ===
# 从标题生成 slug（取前 4 个英文/拼音字符或直接用标题）
SLUG=$(echo "$TITLE" | python3 -c "
import sys, re
t = sys.stdin.read().strip()
# 先试标题中的英文部分
eng = re.findall(r'[a-zA-Z]+', t)
if eng:
    print('-'.join(eng).lower()[:60])
else:
    # 全中文：简短截取
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

# === 6. 下载图片 ===
info "下载配图..."
IMG_DIR_FULL="${BLOG_ROOT}/${IMG_DIR}"
mkdir -p "$IMG_DIR_FULL"

i=1
while read -r url; do
  [ -z "$url" ] && continue
  case "$url" in
    *.png?*)    ext="png" ;;
    *.jpeg?*|*.jpg?*) ext="jpeg" ;;
    *.gif?*)    ext="gif" ;;
    *.webp?*)   ext="webp" ;;
    *)          ext="png" ;;
  esac
  filename="$(printf '%02d' $i).${ext}"
  if curl -sfL -o "${IMG_DIR_FULL}/${filename}" "$url"; then
    size=$(wc -c < "${IMG_DIR_FULL}/${filename}")
    info "  [$i/] $filename (${size} bytes)"
  else
    info "  ⚠️  图片 $i 下载失败"
  fi
  i=$((i+1))
done < <(echo "$MARKDOWN" | grep -oP '!\[.*?\]\(\K[^)]+' || true)

ok "配图下载完成 (共 $((i-1)) 张)"

# === 7. 替换 Markdown 中的图片路径 ===
while read -r url; do
  [ -z "$url" ] && continue
  local_path="/${IMG_DIR}/$(basename "$url" | sed 's/\?.*//')"
  # 实际替换使用序号文件名，重新扫描
  :
done < <(echo "$MARKDOWN" | grep -oP '!\[.*?\]\(\K[^)]+' || true)

# 用序号替换（简化版：将所有远程 URL 按顺序替换为本地路径）
TEMP_MD=$(mktemp)
echo "$MARKDOWN" > "$TEMP_MD"

i=1
while read -r url; do
  [ -z "$url" ] && continue
  case "$url" in
    *.png?*)    ext="png" ;;
    *.jpeg?*|*.jpg?*) ext="jpeg" ;;
    *.gif?*)    ext="gif" ;;
    *.webp?*)   ext="webp" ;;
    *)          ext="png" ;;
  esac
  filename="$(printf '%02d' $i).${ext}"
  # 先获取 alt 文本（保留原有 alt）
  alt=$(echo "$MARKDOWN" | grep -oP "!\[.*?\]\(\Q${url}\E\)" | grep -oP '!\[\K[^\]]+' | head -1)
  sed -i "s|${url}|/images/posts/${PUB_DATE}-${SLUG}/${filename}|g" "$TEMP_MD"
  i=$((i+1))
done < <(echo "$MARKDOWN" | grep -oP '!\[.*?\]\(\K[^)]+' || true)

# 移除 <empty-block/>
sed -i 's/<empty-block\/>//g' "$TEMP_MD"

# === 8. 组装文章 ===
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
echo ""
echo "📋 下一步："
echo "  1. 检查文章内容: less ${POST_FILE}"
echo "  2. 验证构建: bundle exec jekyll build"
echo "  3. 如果没有构建错误，提交即可"
