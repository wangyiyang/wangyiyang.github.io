#!/usr/bin/env python3
"""
博客 Dogfood 巡检脚本（带自动修复授权）
每天早上 8 点执行，模拟真实用户访问博客关键页面
发现问题时直接处理，无需额外确认

【授权范围】
- 404 链接 → 自动检查 _posts/ 目录，找到正确文件名并更新脚本
- 图片加载失败 → 检查 assets/images/ 目录，确认文件存在
- 首页异常 → 检查最近提交，必要时回滚或修复
- 所有修复自动 git commit + push
"""

import urllib.request
import urllib.error
import ssl
import json
import sys
from datetime import datetime

# 配置
BASE_URL = "https://www.wangyiyang.cc"
TIMEOUT = 30

# 要巡检的关键页面
PAGES = [
    {"path": "/", "name": "首页"},
    {"path": "/2026/04/09/mcp-intro-01/", "name": "MCP入门01（最新文章）"},
    {"path": "/2026/04/09/mcp-intro-05/", "name": "MCP入门05（含图片）"},
    {"path": "/2026/04/09/mcp-enterprise-practice/", "name": "MCP实战（含图片）"},
    {"path": "/2026/04/13/lobster-autobiography-day05/", "name": "龙虾自传 Day5"},
    {"path": "/2026/04/09/openclaw-series/", "name": "OpenClaw系列"},
    {"path": "/2025/08/03/rag-deep-dive-01/", "name": "深度RAG笔记01"},
    {"path": "/2025/08/08/langchain-guide-06/", "name": "LangChain Guide 06"},
    {"path": "/sitemap.xml", "name": "Sitemap"},
    {"path": "/robots.txt", "name": "Robots"},
]

# 要检查的图片资源
IMAGES = [
    "/assets/images/mcp-agent-ecosystem-cover.jpg",
    "/assets/images/mcp-agent-ecosystem-cover.webp",
]

def auto_fix_404(page_name, page_path):
    """
    自动修复 404 问题：
    1. 检查 _posts/ 目录，查找标题匹配的文件
    2. 如果有正确文件但 URL 错误，更新巡检脚本中的路径
    """
    import subprocess
    import re
    
    # 获取文章标题关键词（简化版）
    keyword = page_name.lower().replace("langchain", "").replace("guide", "").replace("系列", "").strip()
    if not keyword:
        keyword = page_name.replace("系列", "").strip()
    
    # 搜索 _posts/ 目录
    posts_dir = Path(__file__).parent.parent / "_posts"
    candidates = []
    
    for post in posts_dir.glob("*.md"):
        with open(post, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        # 提取标题
        match = re.search(r'^---\n.*?^title:\s*"([^"]+)".*?^---', content, re.MULTILINE | re.DOTALL)
        if match:
            title = match.group(1).lower()
            if keyword in title or title in keyword:
                candidates.append(post)
    
    if candidates:
        # 取最新的一个
        latest = sorted(candidates, key=lambda x: x.name, reverse=True)[0]
        # 生成正确的 URL 路径（从文件名提取日期和 slug）
        match = re.match(r'(\d{4}-\d{2}-\d{2})-(.+)\.md$', latest.name)
        if match:
            date = match.group(1).replace('-', '/')
            slug = match.group(2)
            correct_path = f"/{date}/{slug}/"
            
            # 更新脚本中的路径
            script_file = Path(__file__)
            script_content = script_file.read_text()
            if page_path in script_content:
                new_content = script_content.replace(
                    f'"path": "{page_path}"',
                    f'"path": "{correct_path}"'
                )
                script_file.write_text(new_content)
                
                # git commit + push
                blog_dir = Path(__file__).parent.parent
                try:
                    subprocess.run(['git', 'add', str(script_file)], cwd=blog_dir, check=True, capture_output=True)
                    subprocess.run(['git', 'commit', '-m', f'fix: auto-fix 404 for {page_name}\n\n- Update URL from {page_path} to {correct_path}\n- Found correct post: {latest.name}'], cwd=blog_dir, check=True, capture_output=True)
                    subprocess.run(['git', 'push'], cwd=blog_dir, check=True, capture_output=True)
                    return f"已自动修复：更新 URL 为 {correct_path} 并推送"
                except Exception as e:
                    return f"找到正确文件 {latest.name} 但推送失败: {e}"
    
    return "无法自动修复：未找到匹配的文章"


def auto_fix_image(image_path):
    """
    自动修复图片 404：
    检查 assets/images/ 目录，确认文件是否存在
    """
    img_file = Path(__file__).parent.parent / "assets" / "images" / Path(image_path).name
    
    if img_file.exists():
        return f"图片文件存在 ({img_file.stat().st_size/1024:.0f}KB)，可能是 GitHub Pages 缓存问题"
    else:
        # 检查是否有相似文件
        images_dir = Path(__file__).parent.parent / "assets" / "images"
        name_without_ext = Path(image_path).stem
        similar = list(images_dir.glob(f"*{name_without_ext}*"))
        
        if similar:
            return f"原文件不存在，但找到相似文件: {[f.name for f in similar]}"
        else:
            return f"图片文件不存在: {img_file}"


def check_url(url, timeout=TIMEOUT):
    """检查单个 URL，返回状态（增强版，带自动修复）"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    start = datetime.now()
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        response = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        elapsed = (datetime.now() - start).total_seconds() * 1000
        
        return {
            "status": "ok",
            "code": response.status,
            "size": len(response.read()),
            "elapsed_ms": round(elapsed, 1),
            "error": None,
            "auto_fix": None
        }
    except urllib.error.HTTPError as e:
        elapsed = (datetime.now() - start).total_seconds() * 1000
        error_msg = f"HTTP {e.code}: {e.reason}"
        auto_fix_result = None
        
        # 尝试自动修复 404
        if e.code == 404:
            # 从 URL 中提取路径
            parsed = urllib.parse.urlparse(url)
            path = parsed.path
            
            # 找到对应的页面配置
            for page in PAGES:
                if page["path"] == path:
                    auto_fix_result = auto_fix_404(page["name"], page["path"])
                    break
            
            # 检查是否是图片
            if not auto_fix_result and path.startswith("/assets/images/"):
                auto_fix_result = auto_fix_image(path)
        
        return {
            "status": "error",
            "code": e.code,
            "size": 0,
            "elapsed_ms": round(elapsed, 1),
            "error": error_msg,
            "auto_fix": auto_fix_result
        }
    except Exception as e:
        elapsed = (datetime.now() - start).total_seconds() * 1000
        return {
            "status": "error",
            "code": 0,
            "size": 0,
            "elapsed_ms": round(elapsed, 1),
            "error": str(e),
            "auto_fix": None
        }

def check_blog():
    """执行完整巡检"""
    results = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "base_url": BASE_URL,
        "pages": {},
        "images": {},
        "summary": {
            "total": 0,
            "ok": 0,
            "error": 0,
            "slow": 0  # > 3s
        }
    }
    
    print(f"🐕 Dogfood 巡检开始: {results['timestamp']}")
    print(f"目标: {BASE_URL}")
    print("=" * 60)
    
    # 检查页面
    print("\n📄 页面检查")
    for page in PAGES:
        url = f"{BASE_URL}{page['path']}"
        result = check_url(url)
        results["pages"][page["name"]] = result
        results["summary"]["total"] += 1
        
        if result["status"] == "ok":
            results["summary"]["ok"] += 1
            icon = "✅"
            if result["elapsed_ms"] > 3000:
                icon = "⚠️"
                results["summary"]["slow"] += 1
            print(f"  {icon} {page['name']}: HTTP {result['code']} ({result['elapsed_ms']}ms)")
        else:
            results["summary"]["error"] += 1
            print(f"  ❌ {page['name']}: {result['error']}")
    
    # 检查图片
    print("\n🖼️  图片检查")
    for img_path in IMAGES:
        url = f"{BASE_URL}{img_path}"
        result = check_url(url)
        results["images"][img_path] = result
        results["summary"]["total"] += 1
        
        if result["status"] == "ok":
            results["summary"]["ok"] += 1
            print(f"  ✅ {img_path}: {result['size']/1024:.0f}KB ({result['elapsed_ms']}ms)")
        else:
            results["summary"]["error"] += 1
            print(f"  ❌ {img_path}: {result['error']}")
    
    # 总结
    print("\n" + "=" * 60)
    print(f"📊 巡检结果: {results['summary']['ok']}/{results['summary']['total']} 通过")
    if results["summary"]["error"] > 0:
        print(f"   ❌ {results['summary']['error']} 个失败")
    if results["summary"]["slow"] > 0:
        print(f"   ⚠️ {results['summary']['slow']} 个加载过慢 (>3s)")
    
    # 如果有失败，输出详细错误 + 自动修复结果
    if results["summary"]["error"] > 0:
        print("\n🔴 失败详情:")
        for name, result in {**results["pages"], **results["images"]}.items():
            if result["status"] == "error":
                print(f"   - {name}: {result['error']}")
                if result.get("auto_fix"):
                    print(f"     🤖 自动修复: {result['auto_fix']}")
    
    return results

def main():
    results = check_blog()
    
    # 如果有任何失败，返回非零退出码
    if results["summary"]["error"] > 0:
        print("\n🚨 巡检发现异常，需要人工介入检查")
        return 1
    
    print("\n✅ 巡检全部通过，博客运行正常")
    return 0

if __name__ == "__main__":
    sys.exit(main())
