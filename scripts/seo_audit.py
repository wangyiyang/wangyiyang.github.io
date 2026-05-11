#!/usr/bin/env python3
"""
SEO 元数据审计脚本
检查所有文章是否包含 description 和 keywords，输出缺失清单
"""
import os, re, sys
from datetime import datetime

POSTS_DIR = "_posts"

def audit_posts():
    missing = []
    total = 0

    for fname in sorted(os.listdir(POSTS_DIR)):
        if not fname.endswith(".md"):
            continue

        path = os.path.join(POSTS_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # 提取 front matter
        fm_match = re.match(r"---\n(.*?)\n---", content, re.DOTALL)
        if not fm_match:
            continue

        total += 1
        fm = fm_match.group(1)

        has_desc = "description:" in fm
        has_kw = "keywords:" in fm

        if not has_desc or not has_kw:
            # 提取标题
            title_match = re.search(r'title:\s*["\']?(.*?)["\']?\n', fm)
            title = title_match.group(1) if title_match else fname

            # 提取日期
            date_match = re.search(r'date:\s*(\d{4}-\d{2}-\d{2})', fm)
            date_str = date_match.group(1) if date_match else ""

            missing.append({
                "file": fname,
                "title": title,
                "date": date_str,
                "missing_desc": not has_desc,
                "missing_kw": not has_kw
            })

    # 按日期倒序
    missing.sort(key=lambda x: x["date"] or "", reverse=True)

    print(f"\n📊 SEO 审计结果")
    print(f"总文章数: {total}")
    print(f"缺失 SEO 的文章: {len(missing)}")
    print(f"覆盖率: {((total - len(missing)) / total * 100):.1f}%\n")

    if missing:
        print("❌ 缺失 SEO 元数据的文章（按日期倒序）：\n")
        for item in missing[:50]:  # 只显示最近50篇
            status = []
            if item["missing_desc"]:
                status.append("❌ description")
            if item["missing_kw"]:
                status.append("❌ keywords")
            print(f"  {item['date']} | {item['title']}")
            print(f"    {' | '.join(status)}")

        # 按月份统计
        from collections import Counter
        months = Counter()
        for item in missing:
            if item["date"]:
                ym = item["date"][:7]
                months[ym] += 1

        print(f"\n📅 按月统计缺失数：")
        for ym, count in sorted(months.items(), reverse=True):
            print(f"  {ym}: {count} 篇")

    return len(missing)

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    count = audit_posts()
    sys.exit(1 if count > 0 else 0)
