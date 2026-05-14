#!/usr/bin/env python3
"""
全站图片优化脚本：压缩 JPG + 生成 WebP + Markdown 图片语法替换

用法：
  python3 optimize_images.py [--dry-run] [--posts-only] [--images-only]

功能：
  1. 遍历 assets/images/，压缩现有 JPG/PNG，生成 WebP 版本
  2. 遍历 _posts/*.md，把 ![alt](url) 替换为 <picture> 渐进增强标签
  3. 支持增量处理（已处理过的图片和文章跳过）
  4. 保留原文件作为 fallback
"""

import os
import re
import sys
import argparse
from pathlib import Path
from PIL import Image

# 配置
SCRIPT_DIR = Path(__file__).parent
BLOG_DIR = SCRIPT_DIR.parent  # scripts/ 的父目录是博客根目录
IMAGES_DIR = BLOG_DIR / "assets" / "images"
POSTS_DIR = BLOG_DIR / "_posts"

# 图片压缩质量
JPEG_QUALITY = 80
WEBP_QUALITY = 80

# 支持的图片格式
SOURCE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def optimize_image(source_path: Path, dry_run: bool = False) -> dict:
    """
    压缩图片并生成 WebP 版本
    返回: {"jpg": 新大小, "webp": webp大小, "saved": 节省字节}
    """
    ext = source_path.suffix.lower()
    if ext not in SOURCE_EXTENSIONS:
        return None

    # 检查是否已优化过（通过 .optimized 标记文件或文件名判断）
    webp_path = source_path.with_suffix(".webp")
    if webp_path.exists():
        return None  # 已处理过，跳过

    # 读取图片
    try:
        img = Image.open(source_path)
    except Exception as e:
        print(f"  ❌ 无法打开图片: {source_path} - {e}")
        return None

    # 如果是 PNG，先转成 RGB（去掉 alpha）再存为高质量 JPG
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    original_size = source_path.stat().st_size

    if dry_run:
        # 预估大小（按质量 80 约是原图的 30-40%）
        estimated_jpg = int(original_size * 0.35)
        estimated_webp = int(original_size * 0.20)
        print(f"  📝 [dry-run] {source_path.name}: {original_size/1024:.0f}KB → JPG ~{estimated_jpg/1024:.0f}KB + WebP ~{estimated_webp/1024:.0f}KB")
        return {"jpg": estimated_jpg, "webp": estimated_webp, "saved": original_size - estimated_jpg}

    # 1. 压缩原图为 JPG（覆盖原文件）
    try:
        img.save(source_path, "JPEG", quality=JPEG_QUALITY, optimize=True, dpi=(72, 72))
        new_jpg_size = source_path.stat().st_size
    except Exception as e:
        print(f"  ❌ 压缩 JPG 失败: {source_path} - {e}")
        return None

    # 2. 生成 WebP
    try:
        img.save(webp_path, "WEBP", quality=WEBP_QUALITY, method=6)
        webp_size = webp_path.stat().st_size
    except Exception as e:
        print(f"  ❌ 生成 WebP 失败: {source_path} - {e}")
        return None

    saved = original_size - new_jpg_size
    print(f"  ✅ {source_path.name}: {original_size/1024:.0f}KB → JPG {new_jpg_size/1024:.0f}KB + WebP {webp_size/1024:.0f}KB (省 {saved/1024:.0f}KB)")

    return {"jpg": new_jpg_size, "webp": webp_size, "saved": saved}


def optimize_all_images(dry_run: bool = False):
    """批量处理 assets/images/ 目录"""
    if not IMAGES_DIR.exists():
        print(f"⚠️ 图片目录不存在: {IMAGES_DIR}")
        return 0, 0

    print(f"\n🖼️  扫描图片目录: {IMAGES_DIR}")

    total_saved = 0
    processed = 0

    for img_path in sorted(IMAGES_DIR.iterdir()):
        if img_path.is_file() and img_path.suffix.lower() in SOURCE_EXTENSIONS:
            result = optimize_image(img_path, dry_run)
            if result:
                processed += 1
                total_saved += result.get("saved", 0)

    print(f"\n📊 图片处理完成: {processed} 张，共节省 {total_saved/1024:.0f}KB")
    return processed, total_saved


def replace_markdown_image(match, dry_run: bool = False) -> str:
    """
    把 Markdown 图片语法替换为 <picture> 标签
    
    输入: ![alt text](/path/to/image.jpg)
    输出: <picture>\n  <source srcset="/path/to/image.webp" type="image/webp">\n  <img src="/path/to/image.jpg" alt="alt text" loading="lazy">\n</picture>
    """
    alt_text = match.group(1) or ""
    img_url = match.group(2)

    # 只处理站内图片（以 / 开头或相对路径）
    if not (img_url.startswith("/") or img_url.startswith("./") or img_url.startswith("../")):
        return match.group(0)  # 外部链接，不处理

    # 生成 webp 路径
    base_url = img_url
    if "." in img_url:
        base_url = img_url.rsplit(".", 1)[0]
    webp_url = f"{base_url}.webp"

    picture_html = (
        f'<picture>\n'
        f'  <source srcset="{webp_url}" type="image/webp">\n'
        f'  <img src="{img_url}" alt="{alt_text}" loading="lazy">\n'
        f'</picture>'
    )

    return picture_html


def process_post(post_path: Path, dry_run: bool = False) -> bool:
    """
    处理单篇文章，替换图片语法
    返回: 是否修改了内容
    """
    # 读取文件（处理编码问题）
    try:
        with open(post_path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(post_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception as e:
            print(f"  ⚠️ 跳过（编码问题）: {post_path.name} - {e}")
            return False

    # 检查是否已包含 <picture> 标签（已处理过）
    if "<picture>" in content:
        return False

    # 正则匹配 Markdown 图片: ![alt](url)
    pattern = r'!\[(.*?)\]\((.*?)\)'
    new_content = re.sub(pattern, lambda m: replace_markdown_image(m, dry_run), content)

    if new_content == content:
        return False  # 没有需要替换的图片

    if dry_run:
        count = len(re.findall(pattern, content))
        print(f"  📝 [dry-run] {post_path.name}: 将替换 {count} 处图片语法")
        return True

    # 写回文件
    with open(post_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    count = len(re.findall(pattern, content))
    print(f"  ✅ {post_path.name}: 替换 {count} 处图片语法")
    return True


def process_all_posts(dry_run: bool = False):
    """批量处理 _posts/ 目录"""
    if not POSTS_DIR.exists():
        print(f"⚠️ 文章目录不存在: {POSTS_DIR}")
        return 0

    print(f"\n📝 扫描文章目录: {POSTS_DIR}")

    processed = 0
    for post_path in sorted(POSTS_DIR.glob("*.md")):
        if process_post(post_path, dry_run):
            processed += 1

    print(f"\n📊 文章处理完成: {processed} 篇")
    return processed


def main():
    parser = argparse.ArgumentParser(description="全站图片优化工具")
    parser.add_argument("--dry-run", action="store_true", help="预演模式，不实际修改文件")
    parser.add_argument("--posts-only", action="store_true", help="只处理文章，不处理图片")
    parser.add_argument("--images-only", action="store_true", help="只处理图片，不处理文章")
    args = parser.parse_args()

    mode = "【预演模式】" if args.dry_run else "【执行模式】"
    print(f"\n🚀 全站图片优化 {mode}")
    print("=" * 50)

    if not args.posts_only:
        img_count, saved_bytes = optimize_all_images(args.dry_run)
    else:
        img_count, saved_bytes = 0, 0

    if not args.images_only:
        post_count = process_all_posts(args.dry_run)
    else:
        post_count = 0

    print("\n" + "=" * 50)
    print("📋 总结")
    print(f"  图片处理: {img_count} 张, 节省 {saved_bytes/1024:.0f}KB")
    print(f"  文章处理: {post_count} 篇")

    if args.dry_run:
        print("\n💡 这是预演，没有实际修改文件。确认无误后去掉 --dry-run 执行。")

    return 0


if __name__ == "__main__":
    sys.exit(main())
