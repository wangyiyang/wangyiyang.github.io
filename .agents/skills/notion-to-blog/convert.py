#!/usr/bin/env python3
"""
notion-to-blog — 将 Notion 页面转换为 Jekyll 博客文章

用法:
    ./convert.py <page-uuid-or-url>
    ./convert.py f13de733-01f7-4039-94c4-4210f6604a28
    ./convert.py "https://www.notion.so/...f13de73301f7403994c44210f6604a28..."

环境变量:
    NOTION_API_TOKEN 或 ~/.config/notion/api_key
"""

import os
import re
import sys
import json
import hashlib
import subprocess
import shutil
from pathlib import Path
from urllib.parse import urlparse

# ─── 配置 ──────────────────────────────────────────────────────────
TOKEN = os.environ.get("NOTION_API_TOKEN")
if not TOKEN:
    token_file = Path.home() / ".config" / "notion" / "api_key"
    if token_file.exists():
        TOKEN = token_file.read_text().strip()

assert TOKEN, "❌ NOTION_API_TOKEN 未设置"

BLOG_ROOT = Path(__file__).resolve().parent.parent.parent.parent
NOTION_VERSION = "2022-06-28"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Notion-Version": NOTION_VERSION,
}


# ─── 工具函数 ──────────────────────────────────────────────────────
def info(msg):    print(f"ℹ️  {msg}")
def ok(msg):      print(f"✅ {msg}")
def die(msg):     print(f"❌ {msg}", file=sys.stderr); sys.exit(1)

def notion_get(path: str) -> dict:
    """调用 Notion REST API GET"""
    url = f"https://api.notion.com/v1/{path.lstrip('/')}"
    r = subprocess.run(
        ["curl", "-sf", "-H", f"Authorization: Bearer {TOKEN}",
         "-H", f"Notion-Version: {NOTION_VERSION}", url],
        capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        die(f"API 请求失败: {url}\n{r.stderr}")
    return json.loads(r.stdout)

def notion_get_text(path: str) -> str:
    """调用 Notion API 并返回 markdown 文本"""
    url = f"https://api.notion.com/v1/{path.lstrip('/')}/markdown"
    r = subprocess.run(
        ["curl", "-sf", "-H", f"Authorization: Bearer {TOKEN}",
         "-H", f"Notion-Version: {NOTION_VERSION}", url],
        capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        die(f"Markdown API 请求失败: {url}\n{r.stderr}")
    return json.loads(r.stdout)["markdown"]

def extract_page_id(input_str: str) -> str:
    """从 URL 或 UUID 中提取标准 UUID 格式的页面 ID"""
    # 已经是 UUID 格式
    if re.match(r'^[a-f0-9\-]{36}$', input_str.lower()):
        return input_str.lower()
    # 32 位 hex
    m = re.search(r'[a-f0-9]{32}', input_str.lower())
    if m:
        raw = m.group()
        return f"{raw[:8]}-{raw[8:12]}-{raw[12:16]}-{raw[16:20]}-{raw[20:]}"
    die(f"无法从输入提取页面 ID: {input_str}")

def download_file(url: str, dest: Path):
    """下载文件，返回 (success, size)"""
    r = subprocess.run(
        ["curl", "-sfL", "-o", str(dest), "-w", "%{size_download}", url],
        capture_output=True, text=True, timeout=60)
    if r.returncode == 0:
        return True, int(r.stdout) if r.stdout else 0
    return False, 0

def gen_slug(title: str) -> str:
    """从标题生成 slug"""
    eng = re.findall(r'[a-zA-Z]+', title)
    if eng:
        slug = '-'.join(eng).lower()[:60]
    else:
        slug = title[:12]
    slug = re.sub(r'[^a-zA-Z0-9\-]', '-', slug)
    slug = re.sub(r'-+', '-', slug).strip('-')
    return slug or f"post-{PUB_DATE}"


# ═══════════════════════════════════════════════════════════════════
#  主流程
# ═══════════════════════════════════════════════════════════════════

# ─── 步骤 1: 解析输入 ─────────────────────────────────────────
page_id = extract_page_id(sys.argv[1] if len(sys.argv) > 1 else "")
info(f"页面 ID: {page_id}")

# ─── 步骤 2: 获取页面属性 ─────────────────────────────────────
info("获取页面属性...")
props = notion_get(f"pages/{page_id}")["properties"]

# 判断是 page 还是 database（查找 type==title 的属性，兼容中文键名）
def _find_title_prop(props) -> tuple:
    """返回 (key, value) 或 None"""
    for k, v in props.items():
        if v.get("type") == "title":
            txt = ''.join(t.get("plain_text", "") for t in v.get("title", []))
            return k, txt
    return None, None

title_key, title = _find_title_prop(props)
if title_key is None:
    # 尝试检查是否 database
    db_check = notion_get(f"databases/{page_id}")
    die(f"这是 database 而非 page。请先查询其子页面:\n"
        f"  POST https://api.notion.com/v1/databases/{page_id}/query")

categories = []
description = ""
pub_date = ""

for name, val in props.items():
    t = val.get("type", "")
    if t == "multi_select" and ("系列" in name or "标签" in name):
        categories = [s["name"] for s in val.get("multi_select", [])]
    elif t == "rich_text" and ("摘要" in name or "观点" in name):
        description = ''.join(t.get("plain_text", "") for t in val.get("rich_text", []))
    elif t == "date" and "发布" in name:
        d = val.get("date")
        if d and d.get("start"):
            pub_date = d["start"]

if not pub_date:
    from datetime import date
    pub_date = date.today().isoformat()

ok(f"标题: {title}")
ok(f"分类: {categories}")
ok(f"发布日期: {pub_date}")

# ─── 步骤 3: 生成文件名和目录 ─────────────────────────────────
slug = gen_slug(title)
post_file = BLOG_ROOT / "_posts" / f"{pub_date}-{slug}.md"
img_dir = BLOG_ROOT / "images" / "posts" / f"{pub_date}-{slug}"

info(f"文章文件: {post_file}")
info(f"图片目录: {img_dir}")

# ─── 步骤 4: 获取 Markdown 内容 ───────────────────────────────
info("获取 Markdown 内容...")
markdown = notion_get_text(f"pages/{page_id}")
ok(f"Markdown 已获取 ({len(markdown)} 字符)")

# ─── 步骤 5: 提取图片 URL ────────────────────────────────────
info("提取图片 URL...")

lines = markdown.split('\n')
img_urls = []
for line in lines:
    if '![' in line:
        start = line.rfind('(')
        end = line.rfind(')')
        if start != -1 and end != -1 and end > start:
            img_urls.append(line[start+1:end])

assert img_urls, "未找到任何图片 URL"
info(f"发现 {len(img_urls)} 张图片")

# ─── 步骤 6: 下载图片 ─────────────────────────────────────────
info("下载配图...")
shutil.rmtree(img_dir, ignore_errors=True)
img_dir.mkdir(parents=True)

for i, url in enumerate(img_urls):
    ext = "png"
    if ".jpg" in url.lower() or ".jpeg" in url.lower():
        ext = "jpg"
    elif ".gif" in url.lower():
        ext = "gif"
    elif ".webp" in url.lower():
        ext = "webp"

    filename = f"{i+1:02d}.{ext}"
    dest = img_dir / filename
    success, size = download_file(url, dest)
    if success:
        info(f"  [{i+1}/{len(img_urls)}] {filename} ({size} bytes)")
    else:
        info(f"  ⚠️  [{i+1}/{len(img_urls)}] {filename} 下载失败")

ok(f"配图下载完成 ({len(img_urls)} 张)")

# ─── 步骤 6b: md5 去重验证 ────────────────────────────────────
info("验证图片唯一性...")
hashes = {}
for f in sorted(img_dir.iterdir()):
    if f.is_file():
        h = hashlib.md5(f.read_bytes()).hexdigest()
        hashes[f.name] = h

# 检查重复
for f1 in hashes:
    for f2 in hashes:
        if f1 < f2 and hashes[f1] == hashes[f2]:
            die(f"md5 重复: {f1} == {f2}！下载顺序可能出错")

ok("所有图片内容唯一")

# ─── 步骤 7: 处理 Notion 特有标记并替换图片路径 ─────────────
info("处理 Notion 标记并替换图片路径...")

cleaned = []
for line in lines:
    stripped = line.strip()

    # 移除 <callout> 标签
    if stripped.startswith("<callout") or stripped == "</callout>":
        continue
    # 清理 callout 内容前的制表符
    if stripped.startswith(">"):
        line = line.lstrip("\t").lstrip()
    # <empty-block/> → 空行
    if stripped == "<empty-block/>":
        cleaned.append("")
        continue
    # 替换图片 URL
    if "![" in line:
        for idx, url in enumerate(img_urls):
            if url in line:
                ext = "png"
                if ".jpg" in url.lower() or ".jpeg" in url.lower():
                    ext = "jpg"
                elif ".gif" in url.lower():
                    ext = "gif"
                elif ".webp" in url.lower():
                    ext = "webp"
                filename = f"{idx+1:02d}.{ext}"
                line = re.sub(r'\]\(https?://[^)]+\)',
                             f'](/images/posts/{pub_date}-{slug}/{filename})',
                             line)
                break
    cleaned.append(line)

body = '\n'.join(cleaned)
img_replaced = body.count("/images/posts/")
info(f"已替换 {img_replaced} 张图片路径")

# ─── 步骤 8: 组装 Front Matter 并写入 ────────────────────────
keywords = ", ".join(categories)
if description:
    short_desc = description[:200]
else:
    short_desc = title

front_matter = f"""---
layout: post
title: "{title}"
categories: [{', '.join(categories)}]
description: "{short_desc}"
keywords: {keywords}
mermaid: false
sequence: false
flow: false
mathjax: false
mindmap: false
mindmap2: false
---

"""

post_file.write_text(front_matter + body)
ok(f"文章已生成: {post_file}")
ok(f"配图位置: {img_dir}/")

# ─── 步骤 9: 构建验证 ─────────────────────────────────────────
print("\n🔨 构建验证...")
r = subprocess.run(
    ["bundle", "exec", "jekyll", "build"],
    cwd=BLOG_ROOT,
    capture_output=True, text=True, timeout=120)
# 只输出最后几行
last_lines = [l for l in r.stdout.split('\n') if l.strip()][-5:]
print('\n'.join(last_lines))
if r.returncode == 0:
    ok("构建成功")
else:
    die(f"构建失败:\n{r.stderr}")

# ─── 完成 ─────────────────────────────────────────────────────
print(f"""
📋 已自动完成所有步骤。确认无误后推送:
   git add -A _posts/ images/posts/{pub_date}-{slug}/
   git commit -m "feat: 新增博客文章「{title}」"
   git push origin master
""")
