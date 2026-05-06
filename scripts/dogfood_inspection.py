#!/usr/bin/env python3
"""
博客 Dogfood 巡检脚本
每天早上 8 点执行，模拟真实用户访问博客关键页面
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

def check_url(url, timeout=TIMEOUT):
    """检查单个 URL，返回状态"""
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
            "error": None
        }
    except urllib.error.HTTPError as e:
        elapsed = (datetime.now() - start).total_seconds() * 1000
        return {
            "status": "error",
            "code": e.code,
            "size": 0,
            "elapsed_ms": round(elapsed, 1),
            "error": f"HTTP {e.code}: {e.reason}"
        }
    except Exception as e:
        elapsed = (datetime.now() - start).total_seconds() * 1000
        return {
            "status": "error",
            "code": 0,
            "size": 0,
            "elapsed_ms": round(elapsed, 1),
            "error": str(e)
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
    
    # 如果有失败，输出详细错误
    if results["summary"]["error"] > 0:
        print("\n🔴 失败详情:")
        for name, result in {**results["pages"], **results["images"]}.items():
            if result["status"] == "error":
                print(f"   - {name}: {result['error']}")
    
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
