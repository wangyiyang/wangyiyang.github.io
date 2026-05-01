# Indie Workbench Theme Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the confirmed indie developer workbench theme for `wangyiyang.github.io` while keeping the Jekyll site buildable after every stage.

**Architecture:** Add a data-backed theme layer on top of the existing Jekyll content model, then migrate the homepage, post layout, secondary pages, and legacy GitHub-dependent widgets into the new system. The new theme uses static `_data` files for workbench modules, topics, and projects, with CSS split into tokens, base, layout, components, and page files loaded after the legacy CSS during migration.

**Tech Stack:** Jekyll 3.9.5, Liquid, Kramdown, Rouge, jekyll-paginate, Bash, CSS, existing jQuery scripts.

---

## Scope Check

This plan implements the approved theme design as one sequential theme migration because the homepage, post layout, topic/project pages, and shared CSS all depend on the same data and component contracts.

The work is split into small commits so a later PR can be reviewed in stages:

1. Data contracts and verification script.
2. Theme CSS foundation and layout loading.
3. Homepage components and homepage replacement.
4. Post layout components and article reading experience.
5. Topic, project, open source, and about pages.
6. Engineering cleanup and final verification.

## File Structure

### Files To Create

- `_data/workbench.yml`: homepage manifesto, CTA links, capability modules, and production-system flow.
- `_data/topics.yml`: curated topic paths shown on homepage and topics page.
- `_data/projects.yml`: static project/workbench data replacing build-time GitHub repository rendering.
- `_includes/theme/hero-manifesto.html`: homepage first-screen manifesto.
- `_includes/theme/workbench-modules.html`: homepage capability module grid.
- `_includes/theme/featured-projects.html`: grouped project/tool list.
- `_includes/theme/production-system.html`: personal production-system flow.
- `_includes/theme/topic-paths.html`: topic path list.
- `_includes/theme/article-list.html`: reusable article list.
- `_includes/theme/pagination.html`: homepage pagination.
- `_includes/theme/post-header.html`: post metadata and intro.
- `_includes/theme/post-toc.html`: desktop and mobile table of contents shell.
- `_includes/theme/post-navigation.html`: previous and next post navigation.
- `_includes/theme/related-posts.html`: related posts based on first shared category.
- `assets/css/theme/tokens.css`: color, typography, spacing, border, shadow tokens.
- `assets/css/theme/base.css`: global text, link, code, table, media defaults.
- `assets/css/theme/layout.css`: containers, grids, responsive layout.
- `assets/css/theme/components.css`: shared component styles.
- `assets/css/theme/pages-home.css`: homepage-specific styles.
- `assets/css/theme/pages-post.css`: post-specific styles.
- `assets/css/theme/pages-page.css`: secondary page styles.
- `assets/css/theme/main.css`: theme CSS import entry.
- `pages/topics.md`: curated topic paths page.
- `pages/projects.md`: project/workbench page.
- `scripts/check-theme-contracts.sh`: static checks for data, CSS, Liquid includes, and GitHub API removal.

### Files To Modify

- `_config.yml`: update navigation to 首页 / 文章 / 专题 / 项目 / 开源 / 关于.
- `_includes/header.html`: load theme CSS, fix Liquid `elsif`, respect Adsense toggle.
- `_includes/footer.html`: align footer with new navigation and quieter theme.
- `_includes/sidebar-popular-repo.html`: render static project data instead of `site.github.public_repositories`.
- `_includes/sidebar-search.html`: remove per-build timestamp cache busting.
- `_layouts/default.html`: use relative asset paths in local builds and keep CDN override.
- `_layouts/page.html`: migrate generic page layout to wider article-style page.
- `_layouts/categories.html`: migrate category page to the theme page shell.
- `_layouts/post.html`: migrate to the new post header, content grid, TOC, related posts, and navigation.
- `index.html`: replace legacy blog-list homepage with workbench homepage.
- `pages/about.md`: rewrite around the personal production system.
- `pages/open-source.md`: render curated static project data.

## Implementation Tasks

### Task 1: Add Data Contracts And Theme Verification Script

**Files:**
- Create: `_data/workbench.yml`
- Create: `_data/topics.yml`
- Create: `_data/projects.yml`
- Create: `scripts/check-theme-contracts.sh`

- [ ] **Step 1: Create the verification script first**

Create `scripts/check-theme-contracts.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

phase="${THEME_CONTRACT_PHASE:-full}"

require_file() {
  local path="$1"
  if [[ ! -f "$path" ]]; then
    echo "Missing required file: $path" >&2
    exit 1
  fi
}

require_text() {
  local path="$1"
  local pattern="$2"
  if ! rg -q "$pattern" "$path"; then
    echo "Missing pattern '$pattern' in $path" >&2
    exit 1
  fi
}

reject_text() {
  local path="$1"
  local pattern="$2"
  if [[ -f "$path" ]] && rg -q "$pattern" "$path"; then
    echo "Rejected pattern '$pattern' found in $path" >&2
    exit 1
  fi
}

require_file "_data/workbench.yml"
require_file "_data/topics.yml"
require_file "_data/projects.yml"
require_text "_data/workbench.yml" "一人公司时代"
require_text "_data/workbench.yml" "AI Engineering"
require_text "_data/topics.yml" "One-Person-Company"
require_text "_data/projects.yml" "wangyiyang/OLL"

if [[ "$phase" == "data" ]]; then
  echo "Theme data contracts passed."
  exit 0
fi

require_file "assets/css/theme/main.css"
require_file "_includes/theme/hero-manifesto.html"
require_file "_includes/theme/post-header.html"
require_file "pages/topics.md"
require_file "pages/projects.md"

require_text "index.html" "theme/hero-manifesto.html"
require_text "_layouts/post.html" "theme/post-header.html"
require_text "_includes/header.html" "assets/css/theme/main.css"
require_text "_includes/header.html" "site.google.adsense.enabled"
require_text "_config.yml" "label: 专题"
require_text "_config.yml" "label: 项目"

reject_text "index.html" "jaavascript:"
reject_text "pages/open-source.md" "site.github.public_repositories"
reject_text "_includes/sidebar-popular-repo.html" "site.github.public_repositories"
reject_text "_includes/sidebar-search.html" "new Date"

echo "Theme contracts passed."
```

- [ ] **Step 2: Run the script and verify the current failure**

Run:

```bash
bash scripts/check-theme-contracts.sh
```

Expected:

```text
Missing required file: _data/workbench.yml
```

- [ ] **Step 3: Add homepage workbench data**

Create `_data/workbench.yml`:

```yaml
manifesto:
  eyebrow: 独立开发者工作台
  title: 一人公司时代，开发者需要自己的 AI 工程系统。
  description: 我在这里记录如何用代码、AI、自动化和写作，构建个人生产基础设施。
  actions:
    - label: 开源项目
      url: /projects/
      primary: true
    - label: 生产系统
      url: /about/
      primary: false
    - label: 专题文章
      url: /topics/
      primary: false
  status:
    - AI Engineering
    - Automation
    - Writing
    - Open Source
    - Product Experiments

modules:
  - key: ai-engineering
    title: AI 工程
    description: 围绕 Agent、RAG、MCP 与模型工程，把 AI 能力变成可交付系统。
    links:
      - label: Agent 专题
        url: /topics/#agent
      - label: MCP 实践
        url: /categories/#MCP
  - key: automation
    title: 自动化工具
    description: 用脚本、工作流和代理系统减少重复劳动，让个人项目具备组织级执行力。
    links:
      - label: 自动化文章
        url: /topics/#one-person-company
      - label: 工具项目
        url: /projects/#automation-tools
  - key: content-system
    title: 内容系统
    description: 把写作、复盘和知识管理沉淀成可检索、可复用、可迭代的内容资产。
    links:
      - label: 专题路径
        url: /topics/
      - label: 最新文章
        url: /archives/
  - key: product-experiments
    title: 产品实验
    description: 以一人公司的方式快速验证产品、工具和工作流，保留能产生复利的部分。
    links:
      - label: 一人公司
        url: /categories/#One-Person-Company
      - label: 项目页
        url: /projects/
  - key: open-source
    title: 开源组件
    description: 将可复用的工程实践沉淀为开源仓库、模板和技能包。
    links:
      - label: 开源项目
        url: /open-source/
      - label: GitHub
        url: https://github.com/wangyiyang

system_flow:
  - label: 输入信息
    description: 从文章、产品想法、用户反馈和工程问题中收集上下文。
  - label: AI 辅助处理
    description: 让 Agent、MCP 和提示工程参与分析、规划、编码与复盘。
  - label: 自动化执行
    description: 用脚本、CI、模板和工作流减少重复操作。
  - label: 产品/文章输出
    description: 把实验结果交付为产品、工具、文章或开源项目。
  - label: 复盘沉淀
    description: 将验证过的方法沉淀为下一轮系统能力。
```

- [ ] **Step 4: Add topic path data**

Create `_data/topics.yml`:

```yaml
- key: ai
  title: AI
  category: AI
  description: 关注 AI 编程、模型应用和工程化落地。
  url: /categories/#AI
- key: agent
  title: Agent
  category: Agent
  description: 从 Agent 架构、工具调用、追踪到生产治理。
  url: /categories/#Agent
- key: rag
  title: RAG
  category: RAG
  description: 面向真实业务知识库的检索增强生成实践。
  url: /categories/#RAG
- key: langchain
  title: LangChain
  category: LangChain
  description: LangChain 与 LangGraph 在 Agent 应用中的工程路径。
  url: /categories/#LangChain
- key: mlops
  title: MLOps
  category: MLOps
  description: 模型、数据、评估、部署和观测的生产流程。
  url: /categories/#MLOps
- key: architecture
  title: 架构
  category: 架构
  description: 用系统设计和工程约束提高长期可维护性。
  url: /categories/#架构
- key: one-person-company
  title: 一人公司
  category: One-Person-Company
  description: 用 AI、自动化和内容系统放大个人产出。
  url: /categories/#One-Person-Company
```

- [ ] **Step 5: Add static project data**

Create `_data/projects.yml`:

```yaml
- key: ai-engineering
  title: AI 工程
  description: Agent、RAG、MCP 和 AI 编程相关工程项目。
  projects:
    - name: OLL
      repo: wangyiyang/OLL
      url: https://github.com/wangyiyang/OLL
      description: 面向业务内容与门户体验的工程系统实验。
      language: Java
      stars: 1
      updated: 2026-04-26
      tags: [Java, CMS, Portal]
    - name: oss-mcp
      repo: wangyiyang/oss-mcp
      url: https://github.com/wangyiyang/oss-mcp
      description: 对象存储 MCP 服务，用于把存储能力接入 AI 工具链。
      language: Python
      stars: 0
      updated: 2025-12-25
      tags: [Python, MCP, OSS]
- key: automation-tools
  title: 自动化工具
  description: 面向个人工作流、代码代理和系统配置的自动化资产。
  projects:
    - name: agent-skills
      repo: wangyiyang/agent-skills
      url: https://github.com/wangyiyang/agent-skills
      description: 面向 Agent 工作流的可复用技能集合。
      language: Python
      stars: 3
      updated: 2026-03-30
      tags: [Agent, Skills, Python]
    - name: dotfiles
      repo: wangyiyang/dotfiles
      url: https://github.com/wangyiyang/dotfiles
      description: 本机开发环境和 shell 工作流配置。
      language: Shell
      stars: 0
      updated: 2026-03-30
      tags: [Shell, macOS, Workflow]
- key: content-system
  title: 内容系统
  description: 支撑写作、发布和内容沉淀的工具与站点。
  projects:
    - name: wangyiyang.github.io
      repo: wangyiyang/wangyiyang.github.io
      url: https://github.com/wangyiyang/wangyiyang.github.io
      description: 当前技术博客和个人生产系统入口。
      language: HTML
      stars: 3
      updated: 2026-04-23
      tags: [Jekyll, Blog, Writing]
    - name: Article
      repo: wangyiyang/Article
      url: https://github.com/wangyiyang/Article
      description: 文章、草稿和内容资产管理仓库。
      language: Python
      stars: 1
      updated: 2026-04-12
      tags: [Writing, Python, Archive]
- key: product-experiments
  title: 产品实验
  description: 一人公司方向的产品、工具和业务系统实验。
  projects:
    - name: Lichun
      repo: wangyiyang/Lichun
      url: https://github.com/wangyiyang/Lichun
      description: TypeScript 产品实验仓库。
      language: TypeScript
      stars: 0
      updated: 2026-04-26
      tags: [TypeScript, Product, Experiment]
    - name: Juanbing
      repo: wangyiyang/Juanbing
      url: https://github.com/wangyiyang/Juanbing
      description: TypeScript 工具或产品实验仓库。
      language: TypeScript
      stars: 0
      updated: 2026-04-26
      tags: [TypeScript, Product, Experiment]
- key: open-source-components
  title: 开源组件
  description: 可复用组件、模板和社区项目。
  projects:
    - name: md
      repo: wangyiyang/md
      url: https://github.com/wangyiyang/md
      description: 微信 Markdown 编辑器，支持主题样式、内容管理、多图床和 AI 助手。
      language: Vue
      stars: 0
      updated: 2026-04-04
      tags: [Vue, Markdown, Editor]
    - name: fastapi-project-template
      repo: wangyiyang/fastapi-project-template
      url: https://github.com/wangyiyang/fastapi-project-template
      description: FastAPI 项目模板。
      language: Python
      stars: 0
      updated: 2025-12-05
      tags: [FastAPI, Python, Template]
```

- [ ] **Step 6: Verify data contract**

Run:

```bash
THEME_CONTRACT_PHASE=data bash scripts/check-theme-contracts.sh
```

Expected:

```text
Theme data contracts passed.
```

- [ ] **Step 7: Commit data contracts**

Run:

```bash
git add _data/workbench.yml _data/topics.yml _data/projects.yml scripts/check-theme-contracts.sh
git commit -m "feat: add workbench theme data contracts"
```

Expected:

```text
[codex/indie-workbench-theme ...] feat: add workbench theme data contracts
```

### Task 2: Add Theme CSS Foundation And Header Loading

**Files:**
- Create: `assets/css/theme/tokens.css`
- Create: `assets/css/theme/base.css`
- Create: `assets/css/theme/layout.css`
- Create: `assets/css/theme/components.css`
- Create: `assets/css/theme/pages-home.css`
- Create: `assets/css/theme/pages-post.css`
- Create: `assets/css/theme/pages-page.css`
- Create: `assets/css/theme/main.css`
- Modify: `_includes/header.html`
- Modify: `_layouts/default.html`

- [ ] **Step 1: Add token file**

Create `assets/css/theme/tokens.css`:

```css
:root {
  --theme-bg: #fbfbfa;
  --theme-surface: #ffffff;
  --theme-text: #18191b;
  --theme-muted: #626973;
  --theme-subtle: #8a929c;
  --theme-border: #e5e7eb;
  --theme-border-strong: #cfd5dd;
  --theme-accent: #2563eb;
  --theme-accent-dark: #1d4ed8;
  --theme-code-bg: #f5f7fa;
  --theme-radius-sm: 4px;
  --theme-radius-md: 8px;
  --theme-container: 1120px;
  --theme-reading: 760px;
  --theme-space-1: 0.25rem;
  --theme-space-2: 0.5rem;
  --theme-space-3: 0.75rem;
  --theme-space-4: 1rem;
  --theme-space-6: 1.5rem;
  --theme-space-8: 2rem;
  --theme-space-12: 3rem;
  --theme-space-16: 4rem;
  --theme-font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  --theme-font-mono: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
}
```

- [ ] **Step 2: Add base styles**

Create `assets/css/theme/base.css`:

```css
html {
  background: var(--theme-bg);
}

body {
  background: var(--theme-bg);
  color: var(--theme-text);
  font-family: var(--theme-font-sans);
  letter-spacing: 0;
}

a {
  color: var(--theme-accent);
  text-decoration-thickness: 1px;
  text-underline-offset: 0.18em;
}

a:hover,
a:focus {
  color: var(--theme-accent-dark);
}

.markdown-body {
  color: var(--theme-text);
  font-size: 17px;
  line-height: 1.85;
}

.markdown-body h2,
.markdown-body h3,
.markdown-body h4 {
  color: var(--theme-text);
  letter-spacing: 0;
  margin-top: 2.2em;
}

.markdown-body p,
.markdown-body ul,
.markdown-body ol,
.markdown-body blockquote,
.markdown-body table,
.markdown-body pre {
  margin-bottom: 1.15em;
}

.markdown-body blockquote {
  border-left: 3px solid var(--theme-accent);
  color: var(--theme-muted);
  background: transparent;
}

.markdown-body code,
.markdown-body tt {
  background: var(--theme-code-bg);
  border-radius: var(--theme-radius-sm);
  font-family: var(--theme-font-mono);
}

.markdown-body pre {
  background: var(--theme-code-bg);
  border: 1px solid var(--theme-border);
  border-radius: var(--theme-radius-md);
}

.markdown-body img,
.markdown-body video {
  border-radius: var(--theme-radius-md);
  height: auto;
  max-width: 100%;
}
```

- [ ] **Step 3: Add layout styles**

Create `assets/css/theme/layout.css`:

```css
.theme-container {
  max-width: var(--theme-container);
  margin: 0 auto;
  padding: 0 var(--theme-space-6);
}

.theme-section {
  border-top: 1px solid var(--theme-border);
  padding: var(--theme-space-12) 0;
}

.theme-section-header {
  display: grid;
  gap: var(--theme-space-2);
  margin-bottom: var(--theme-space-8);
}

.theme-section-kicker {
  color: var(--theme-accent);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.theme-section-title {
  color: var(--theme-text);
  font-size: clamp(1.35rem, 2vw, 2rem);
  line-height: 1.25;
  margin: 0;
}

.theme-section-description {
  color: var(--theme-muted);
  max-width: 680px;
}

.theme-grid {
  display: grid;
  gap: var(--theme-space-6);
}

.theme-grid-2 {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.theme-grid-3 {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.theme-post-shell {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 260px;
  gap: var(--theme-space-12);
  max-width: var(--theme-container);
  margin: 0 auto;
  padding: var(--theme-space-12) var(--theme-space-6);
}

.theme-reading {
  max-width: var(--theme-reading);
}

@media (max-width: 900px) {
  .theme-grid-2,
  .theme-grid-3,
  .theme-post-shell {
    grid-template-columns: 1fr;
  }

  .theme-container,
  .theme-post-shell {
    padding-left: var(--theme-space-4);
    padding-right: var(--theme-space-4);
  }
}
```

- [ ] **Step 4: Add component styles**

Create `assets/css/theme/components.css`:

```css
.theme-button {
  align-items: center;
  border: 1px solid var(--theme-border-strong);
  border-radius: var(--theme-radius-sm);
  color: var(--theme-text);
  display: inline-flex;
  font-weight: 600;
  gap: var(--theme-space-2);
  min-height: 38px;
  padding: 0 var(--theme-space-4);
  text-decoration: none;
}

.theme-button-primary {
  background: var(--theme-accent);
  border-color: var(--theme-accent);
  color: #fff;
}

.theme-button:hover,
.theme-button:focus {
  border-color: var(--theme-accent);
  text-decoration: none;
}

.theme-list {
  border-top: 1px solid var(--theme-border);
  list-style: none;
  margin: 0;
  padding: 0;
}

.theme-list-item {
  border-bottom: 1px solid var(--theme-border);
  padding: var(--theme-space-5, 1.25rem) 0;
}

.theme-meta {
  color: var(--theme-subtle);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.86rem;
  gap: var(--theme-space-3);
}

.theme-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--theme-space-2);
  margin-top: var(--theme-space-3);
}

.theme-tag {
  border: 1px solid var(--theme-border);
  border-radius: 999px;
  color: var(--theme-muted);
  font-size: 0.78rem;
  padding: 0.12rem 0.55rem;
}

.site-header {
  background: rgba(251, 251, 250, 0.94);
  border-bottom: 1px solid var(--theme-border);
}

.site-header .container {
  max-width: var(--theme-container);
}

.site-header h1 a,
.site-header-nav-item {
  color: var(--theme-text);
}

.site-header-nav-item.selected,
.site-header-nav-item:hover {
  color: var(--theme-accent);
}
```

- [ ] **Step 5: Add page style files**

Create `assets/css/theme/pages-home.css`:

```css
.workbench-hero {
  padding: var(--theme-space-16) 0 var(--theme-space-12);
}

.workbench-hero-grid {
  display: grid;
  gap: var(--theme-space-12);
  grid-template-columns: minmax(0, 1.3fr) minmax(280px, 0.7fr);
  align-items: end;
}

.workbench-eyebrow {
  color: var(--theme-accent);
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.workbench-title {
  color: var(--theme-text);
  font-size: clamp(2.4rem, 6vw, 5rem);
  line-height: 1.05;
  margin: var(--theme-space-4) 0;
}

.workbench-description {
  color: var(--theme-muted);
  font-size: 1.12rem;
  line-height: 1.8;
  max-width: 720px;
}

.workbench-actions,
.workbench-status {
  display: flex;
  flex-wrap: wrap;
  gap: var(--theme-space-3);
  margin-top: var(--theme-space-6);
}

.workbench-status {
  border-left: 2px solid var(--theme-accent);
  color: var(--theme-muted);
  flex-direction: column;
  font-family: var(--theme-font-mono);
  font-size: 0.9rem;
  padding-left: var(--theme-space-4);
}

@media (max-width: 900px) {
  .workbench-hero-grid {
    grid-template-columns: 1fr;
  }
}
```

Create `assets/css/theme/pages-post.css`:

```css
.post-hero {
  border-bottom: 1px solid var(--theme-border);
  padding: var(--theme-space-12) 0 var(--theme-space-8);
}

.post-hero-inner {
  max-width: var(--theme-reading);
}

.post-title {
  color: var(--theme-text);
  font-size: clamp(2rem, 5vw, 3.8rem);
  line-height: 1.12;
  margin: var(--theme-space-4) 0;
}

.post-description {
  color: var(--theme-muted);
  font-size: 1.08rem;
  line-height: 1.75;
}

.post-toc {
  position: sticky;
  top: 92px;
}

.post-toc-title {
  color: var(--theme-text);
  font-size: 0.82rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.post-toc a {
  color: var(--theme-muted);
}

.post-toc a:hover {
  color: var(--theme-accent);
}

.post-footer-nav {
  border-top: 1px solid var(--theme-border);
  display: grid;
  gap: var(--theme-space-4);
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin-top: var(--theme-space-12);
  padding-top: var(--theme-space-6);
}

@media (max-width: 900px) {
  .post-toc {
    position: static;
  }

  .post-footer-nav {
    grid-template-columns: 1fr;
  }
}
```

Create `assets/css/theme/pages-page.css`:

```css
.theme-page-hero {
  border-bottom: 1px solid var(--theme-border);
  padding: var(--theme-space-12) 0 var(--theme-space-8);
}

.theme-page-title {
  color: var(--theme-text);
  font-size: clamp(2rem, 4vw, 3.2rem);
  line-height: 1.15;
  margin: 0;
}

.theme-page-description {
  color: var(--theme-muted);
  font-size: 1.06rem;
  line-height: 1.75;
  margin-top: var(--theme-space-4);
  max-width: 720px;
}

.theme-page-content {
  padding: var(--theme-space-10, 2.5rem) 0 var(--theme-space-16);
}
```

- [ ] **Step 6: Add CSS entry file**

Create `assets/css/theme/main.css`:

```css
@import url("./tokens.css");
@import url("./base.css");
@import url("./layout.css");
@import url("./components.css");
@import url("./pages-home.css");
@import url("./pages-post.css");
@import url("./pages-page.css");
```

- [ ] **Step 7: Load theme CSS and fix header toggles**

In `_includes/header.html`, make three edits:

1. After the `{% for css in page.css %}` loop, add:

```liquid
    <link rel="stylesheet" href="{{ assets_base_url }}/assets/css/theme/main.css">
```

2. Wrap Adsense script loading:

```liquid
    {% if site.google.adsense.enabled %}
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8213039222083919"
     crossorigin="anonymous"></script>
    {% endif %}
```

3. Replace both Liquid branches written as `{% else if ... %}` with `elsif`:

```liquid
      {% elsif page.description %}
```

and:

```liquid
      {% elsif content %}
```

- [ ] **Step 8: Make local asset base relative when CDN is off**

In `_layouts/default.html`, replace the first assign block with:

```liquid
{% assign assets_base_url = site.baseurl | default: '' | replace: '//', '/' | replace: '/$', '' %}
{% if site.cdn.jsdelivr.enabled %}
{% assign assets_base_url = "https://fastly.jsdelivr.net/gh/" | append: site.repository | append: '@master' %}
{% endif %}
```

Keep the existing image replacement logic unchanged in this task.

- [ ] **Step 9: Build and verify theme CSS loads**

Run:

```bash
bundle exec jekyll build
```

Expected:

```text
done in
```

Then run:

```bash
rg -n "assets/css/theme/main.css|site.google.adsense.enabled|elsif page.description" _includes/header.html _site/index.html
```

Expected: output includes `_includes/header.html` and `_site/index.html` matches.

- [ ] **Step 10: Commit CSS foundation**

Run:

```bash
git add assets/css/theme _includes/header.html _layouts/default.html
git commit -m "feat: add indie workbench theme foundation"
```

Expected:

```text
[codex/indie-workbench-theme ...] feat: add indie workbench theme foundation
```

### Task 3: Build Homepage Theme Components

**Files:**
- Create: `_includes/theme/hero-manifesto.html`
- Create: `_includes/theme/workbench-modules.html`
- Create: `_includes/theme/featured-projects.html`
- Create: `_includes/theme/production-system.html`
- Create: `_includes/theme/topic-paths.html`
- Create: `_includes/theme/article-list.html`
- Create: `_includes/theme/pagination.html`

- [ ] **Step 1: Add manifesto component**

Create `_includes/theme/hero-manifesto.html`:

```liquid
{% assign manifesto = site.data.workbench.manifesto %}
<section class="workbench-hero">
  <div class="theme-container workbench-hero-grid">
    <div>
      <div class="workbench-eyebrow">{{ manifesto.eyebrow }}</div>
      <h1 class="workbench-title">{{ manifesto.title }}</h1>
      <p class="workbench-description">{{ manifesto.description }}</p>
      <div class="workbench-actions">
        {% for action in manifesto.actions %}
        <a class="theme-button {% if action.primary %}theme-button-primary{% endif %}" href="{{ action.url | relative_url }}">{{ action.label }}</a>
        {% endfor %}
      </div>
    </div>
    <div class="workbench-status" aria-label="Workbench status">
      {% for item in manifesto.status %}
      <span>{{ item }}</span>
      {% endfor %}
    </div>
  </div>
</section>
```

- [ ] **Step 2: Add workbench modules component**

Create `_includes/theme/workbench-modules.html`:

```liquid
<section class="theme-section">
  <div class="theme-container">
    <header class="theme-section-header">
      <div class="theme-section-kicker">Workbench</div>
      <h2 class="theme-section-title">个人生产系统的能力模块</h2>
      <p class="theme-section-description">这些模块把 AI、自动化、写作、产品实验和开源组件组织成可持续迭代的工作台。</p>
    </header>
    <div class="theme-grid theme-grid-3">
      {% for module in site.data.workbench.modules %}
      <article class="workbench-module" id="{{ module.key }}">
        <h3>{{ module.title }}</h3>
        <p>{{ module.description }}</p>
        <div class="theme-tags">
          {% for link in module.links %}
          <a class="theme-tag" href="{{ link.url | relative_url }}">{{ link.label }}</a>
          {% endfor %}
        </div>
      </article>
      {% endfor %}
    </div>
  </div>
</section>
```

- [ ] **Step 3: Add featured projects component**

Create `_includes/theme/featured-projects.html`:

```liquid
<section class="theme-section">
  <div class="theme-container">
    <header class="theme-section-header">
      <div class="theme-section-kicker">Projects</div>
      <h2 class="theme-section-title">正在构建的项目与工具</h2>
      <p class="theme-section-description">项目按能力模块组织，GitHub 数据只作为辅助信息，核心结构由静态数据维护。</p>
    </header>
    {% for group in site.data.projects %}
    <section class="project-group" id="{{ group.key }}">
      <h3>{{ group.title }}</h3>
      <p>{{ group.description }}</p>
      <ol class="theme-list">
        {% for project in group.projects %}
        <li class="theme-list-item project-list-item">
          <div>
            <h4><a href="{{ project.url }}" target="_blank" rel="noopener">{{ project.name }}</a></h4>
            <p>{{ project.description }}</p>
            <div class="theme-meta">
              <span>{{ project.language }}</span>
              <span>{{ project.stars }} stars</span>
              <span>Updated {{ project.updated }}</span>
            </div>
            <div class="theme-tags">
              {% for tag in project.tags %}
              <span class="theme-tag">{{ tag }}</span>
              {% endfor %}
            </div>
          </div>
        </li>
        {% endfor %}
      </ol>
    </section>
    {% endfor %}
  </div>
</section>
```

- [ ] **Step 4: Add production system component**

Create `_includes/theme/production-system.html`:

```liquid
<section class="theme-section">
  <div class="theme-container">
    <header class="theme-section-header">
      <div class="theme-section-kicker">System</div>
      <h2 class="theme-section-title">从输入到复盘的个人生产闭环</h2>
      <p class="theme-section-description">主题不只展示文章，也展示这些文章、项目和自动化能力如何形成一套长期运转的系统。</p>
    </header>
    <ol class="theme-list production-flow">
      {% for step in site.data.workbench.system_flow %}
      <li class="theme-list-item production-flow-item">
        <span class="production-flow-index">{{ forloop.index }}</span>
        <div>
          <h3>{{ step.label }}</h3>
          <p>{{ step.description }}</p>
        </div>
      </li>
      {% endfor %}
    </ol>
  </div>
</section>
```

- [ ] **Step 5: Add topic paths component**

Create `_includes/theme/topic-paths.html`:

```liquid
<section class="theme-section">
  <div class="theme-container">
    <header class="theme-section-header">
      <div class="theme-section-kicker">Topics</div>
      <h2 class="theme-section-title">专题路径</h2>
      <p class="theme-section-description">专题是阅读路径，不只是分类聚合。</p>
    </header>
    <div class="theme-grid theme-grid-3">
      {% for topic in site.data.topics %}
      {% assign topic_posts = site.categories[topic.category] | default: empty %}
      <article class="topic-path" id="{{ topic.key }}">
        <h3><a href="{{ topic.url | relative_url }}">{{ topic.title }}</a></h3>
        <p>{{ topic.description }}</p>
        <div class="theme-meta">
          <span>{{ topic_posts.size }} 篇文章</span>
          <span>{{ topic.category }}</span>
        </div>
      </article>
      {% endfor %}
    </div>
  </div>
</section>
```

- [ ] **Step 6: Add article list component**

Create `_includes/theme/article-list.html`:

```liquid
{% assign article_items = include.posts | default: site.posts %}
<ol class="theme-list article-list">
  {% for post in article_items limit: include.limit %}
  <li class="theme-list-item article-list-item">
    <h3><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h3>
    <p>{{ post.description | default: post.excerpt | strip_html | strip }}</p>
    <div class="theme-meta">
      <time datetime="{{ post.date | date_to_xmlschema }}">{{ post.date | date: "%Y-%m-%d" }}</time>
      {% for cat in post.categories %}
      <a href="{{ '/categories/#' | append: cat | relative_url }}">{{ cat }}</a>
      {% endfor %}
    </div>
  </li>
  {% endfor %}
</ol>
```

- [ ] **Step 7: Add pagination component**

Create `_includes/theme/pagination.html`:

```liquid
{% if paginator.total_pages > 1 %}
<nav class="theme-pagination" aria-label="文章分页">
  {% if paginator.previous_page %}
    {% if paginator.previous_page == 1 %}
    <a class="theme-button" href="{{ '/' | relative_url }}">上一页</a>
    {% else %}
    <a class="theme-button" href="{{ '/page' | append: paginator.previous_page | relative_url }}">上一页</a>
    {% endif %}
  {% endif %}
  <span class="theme-meta">第 {{ paginator.page }} / {{ paginator.total_pages }} 页</span>
  {% if paginator.next_page %}
  <a class="theme-button" href="{{ '/page' | append: paginator.next_page | relative_url }}">下一页</a>
  {% endif %}
</nav>
{% endif %}
```

- [ ] **Step 8: Build and verify components parse**

Run:

```bash
bundle exec jekyll build
```

Expected:

```text
done in
```

- [ ] **Step 9: Commit homepage components**

Run:

```bash
git add _includes/theme
git commit -m "feat: add workbench homepage components"
```

Expected:

```text
[codex/indie-workbench-theme ...] feat: add workbench homepage components
```

### Task 4: Replace Homepage With Workbench Structure

**Files:**
- Modify: `index.html`

- [ ] **Step 1: Replace the homepage with the workbench layout**

Replace `index.html` with:

```liquid
---
layout: default
class: home workbench-home
comments: false
---

{% include theme/hero-manifesto.html %}
{% include theme/workbench-modules.html %}
{% include theme/featured-projects.html %}
{% include theme/production-system.html %}
{% include theme/topic-paths.html %}

<section class="theme-section">
  <div class="theme-container">
    <header class="theme-section-header">
      <div class="theme-section-kicker">Writing</div>
      <h2 class="theme-section-title">最新文章</h2>
      <p class="theme-section-description">文章是工作台的持续沉淀区，记录 AI 工程、一人公司和产品实验中的判断、方法与复盘。</p>
    </header>
    {% include theme/article-list.html posts=paginator.posts limit=10 %}
    {% include theme/pagination.html %}
  </div>
</section>
```

- [ ] **Step 2: Verify the old typo is gone**

Run:

```bash
rg -n "jaavascript:" index.html
```

Expected: command exits with status `1` and prints no matches.

- [ ] **Step 3: Build and inspect generated homepage**

Run:

```bash
bundle exec jekyll build
```

Expected:

```text
done in
```

Then run:

```bash
rg -n "一人公司时代|个人生产系统的能力模块|正在构建的项目与工具|最新文章" _site/index.html
```

Expected: all four phrases are present in `_site/index.html`.

- [ ] **Step 4: Commit homepage replacement**

Run:

```bash
git add index.html
git commit -m "feat: replace homepage with workbench experience"
```

Expected:

```text
[codex/indie-workbench-theme ...] feat: replace homepage with workbench experience
```

### Task 5: Rebuild Post Layout And Reading Experience

**Files:**
- Create: `_includes/theme/post-header.html`
- Create: `_includes/theme/post-toc.html`
- Create: `_includes/theme/post-navigation.html`
- Create: `_includes/theme/related-posts.html`
- Modify: `_layouts/post.html`

- [ ] **Step 1: Add post header component**

Create `_includes/theme/post-header.html`:

```liquid
<header class="post-hero">
  <div class="theme-container">
    <div class="post-hero-inner">
      <div class="theme-meta">
        {% if page.date %}
        <time datetime="{{ page.date | date_to_xmlschema }}">{{ page.date | date: "%Y-%m-%d" }}</time>
        {% endif %}
        {% for cat in page.categories %}
        <a href="{{ '/categories/#' | append: cat | relative_url }}">{{ cat }}</a>
        {% endfor %}
        {% if site.components.word_count.enabled %}
        <span>约 {{ page.content | strip_html | strip_newlines | remove: " " | size | divided_by: 350 | plus: 1 }} 分钟</span>
        {% endif %}
      </div>
      <h1 class="post-title">{{ page.title }}</h1>
      {% if page.description %}
      <p class="post-description">{{ page.description }}</p>
      {% endif %}
      {% if page.keywords %}
      <div class="theme-tags">
        {% assign keyword_items = page.keywords | split: ',' %}
        {% for keyword in keyword_items %}
        <span class="theme-tag">{{ keyword | strip }}</span>
        {% endfor %}
      </div>
      {% endif %}
    </div>
  </div>
</header>
```

- [ ] **Step 2: Add TOC component**

Create `_includes/theme/post-toc.html`:

```liquid
<aside class="post-toc" aria-label="文章目录">
  <h2 class="post-toc-title">Contents</h2>
  {% include sidebar-post-nav.html %}
</aside>
```

- [ ] **Step 3: Add previous and next navigation**

Create `_includes/theme/post-navigation.html`:

```liquid
{% if page.previous or page.next %}
<nav class="post-footer-nav" aria-label="文章导航">
  {% if page.previous %}
  <a class="theme-button" href="{{ page.previous.url | relative_url }}">上一篇：{{ page.previous.title }}</a>
  {% else %}
  <span></span>
  {% endif %}
  {% if page.next %}
  <a class="theme-button" href="{{ page.next.url | relative_url }}">下一篇：{{ page.next.title }}</a>
  {% endif %}
</nav>
{% endif %}
```

- [ ] **Step 4: Add related posts component**

Create `_includes/theme/related-posts.html`:

```liquid
{% assign primary_category = page.categories | first %}
{% assign related_posts = site.categories[primary_category] | where_exp: "post", "post.url != page.url" %}
{% if related_posts.size > 0 %}
<section class="theme-section related-posts">
  <header class="theme-section-header">
    <div class="theme-section-kicker">Related</div>
    <h2 class="theme-section-title">继续阅读 {{ primary_category }}</h2>
  </header>
  {% include theme/article-list.html posts=related_posts limit=3 %}
</section>
{% endif %}
```

- [ ] **Step 5: Replace post layout**

Replace `_layouts/post.html` with:

```liquid
---
layout: default
---

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "{{ page.title | escape }}",
  "author": {
    "@type": "Person",
    "name": "{{ site.author }}",
    "url": "{{ site.url }}"
  },
  {% if page.date %}
  "datePublished": "{{ page.date | date_to_xmlschema }}",
  {% endif %}
  {% if page.categories %}
  "articleSection": "{{ page.categories | first }}",
  {% endif %}
  "url": "{{ site.url }}{{ page.url | remove_first:'index.html' }}"
}
</script>

{% include theme/post-header.html %}

<main class="theme-post-shell">
  <article class="article-content markdown-body theme-reading">
    {% include content-header-ad.html %}
    {{ content }}
    {% include copyright.html %}
    {% include theme/post-navigation.html %}
    {% include theme/related-posts.html %}
    {% include content-footer-ad.html %}
    <div class="comment">
      {% include comments.html %}
    </div>
  </article>
  {% include theme/post-toc.html %}
</main>
```

- [ ] **Step 6: Build and verify generated post**

Run:

```bash
bundle exec jekyll build
```

Expected:

```text
done in
```

Then run:

```bash
first_post="$(find _site -path '*/index.html' -type f | rg '/20[0-9]{2}/' | head -1)"
rg -n "post-hero|theme-post-shell|post-toc|BlogPosting" "$first_post"
```

Expected: all four patterns are present in one generated post page.

- [ ] **Step 7: Commit post layout**

Run:

```bash
git add _includes/theme/post-header.html _includes/theme/post-toc.html _includes/theme/post-navigation.html _includes/theme/related-posts.html _layouts/post.html
git commit -m "feat: rebuild post reading layout"
```

Expected:

```text
[codex/indie-workbench-theme ...] feat: rebuild post reading layout
```

### Task 6: Add Topic, Project, Open Source, And About Pages

**Files:**
- Create: `pages/topics.md`
- Create: `pages/projects.md`
- Modify: `pages/open-source.md`
- Modify: `pages/about.md`
- Modify: `_config.yml`
- Modify: `_layouts/page.html`
- Modify: `_layouts/categories.html`

- [ ] **Step 1: Update navigation**

In `_config.yml`, replace the `navs:` list with:

```yaml
navs:
  -
    href: /
    label: 首页

  -
    href: /archives/
    label: 文章

  -
    href: /topics/
    label: 专题

  -
    href: /projects/
    label: 项目

  -
    href: /open-source/
    label: 开源
    mobile-hidden: true

  -
    href: /about/
    label: 关于
```

- [ ] **Step 2: Replace generic page layout**

Replace `_layouts/page.html` with:

```liquid
---
layout: default
---

<header class="theme-page-hero">
  <div class="theme-container">
    <h1 class="theme-page-title">{{ page.title }}</h1>
    {% if page.description %}
    <p class="theme-page-description">{{ page.description }}</p>
    {% endif %}
  </div>
</header>

<main class="theme-container theme-page-content">
  <article class="article-content markdown-body theme-reading">
    {{ content }}
  </article>
  {% if page.comments %}
  <div class="comment theme-reading">
    {% include comments.html %}
  </div>
  {% endif %}
</main>
```

- [ ] **Step 3: Replace category layout shell**

Replace `_layouts/categories.html` with:

```liquid
---
layout: default
---

<header class="theme-page-hero">
  <div class="theme-container">
    <h1 class="theme-page-title">{{ page.title }}</h1>
    {% if page.description %}
    <p class="theme-page-description">{{ page.description }}</p>
    {% endif %}
  </div>
</header>

<main class="theme-container theme-page-content">
  {{ content }}
</main>
```

- [ ] **Step 4: Add topics page**

Create `pages/topics.md`:

```liquid
---
layout: page
title: 专题
description: 以阅读路径组织 AI、Agent、RAG、LangChain、MLOps、架构和一人公司相关内容。
keywords: 专题,AI,Agent,RAG,LangChain,MLOps,一人公司
comments: false
menu: 专题
permalink: /topics/
---

{% include theme/topic-paths.html %}
```

- [ ] **Step 5: Add projects page**

Create `pages/projects.md`:

```liquid
---
layout: page
title: 项目
description: 按能力模块整理开源项目、自动化工具、内容系统和产品实验。
keywords: 项目,开源,工具,一人公司,AI工程
comments: false
menu: 项目
permalink: /projects/
---

{% include theme/featured-projects.html %}
```

- [ ] **Step 6: Replace open source page with static data**

Replace `pages/open-source.md` with:

```liquid
---
layout: page
title: 开源
keywords: 开源,open-source,GitHub,开源项目
description: 这里整理我公开维护或用于个人生产系统的开源项目。
comments: false
menu: 开源
permalink: /open-source/
---

{% include theme/featured-projects.html %}
```

- [ ] **Step 7: Rewrite about page around production system**

Replace `pages/about.md` with:

```liquid
---
layout: page
title: 关于
description: 我关注如何用 AI、代码、自动化和写作构建一套可持续演进的个人生产系统。
keywords: 王翊仰,一人公司,AI工程,自动化,技术写作
comments: true
menu: 关于
permalink: /about/
---

我是王翊仰。这个博客记录我作为独立开发者和一人公司实践者，如何把 AI、代码、自动化、写作和开源项目组织成一套长期运转的个人生产基础设施。

## 长期方向

- 用 AI 工程系统放大个人交付能力。
- 用自动化工具减少重复劳动。
- 用写作和复盘沉淀可复用的方法。
- 用开源项目验证工具、流程和产品想法。

## 生产系统

{% include theme/production-system.html %}

## 技术关键词

{% for skill in site.data.skills %}
### {{ skill.name }}
<div class="theme-tags">
{% for keyword in skill.keywords %}
<span class="theme-tag">{{ keyword }}</span>
{% endfor %}
</div>
{% endfor %}

## 联系

{% for website in site.data.social %}
- {{ website.sitename }}：[@{{ website.name }}]({{ website.url }})
{% endfor %}
```

- [ ] **Step 8: Build and verify pages**

Run:

```bash
bundle exec jekyll build
```

Expected:

```text
done in
```

Then run:

```bash
rg -n "专题路径" _site/topics/index.html
rg -n "正在构建的项目与工具" _site/projects/index.html _site/open-source/index.html
rg -n "个人生产基础设施" _site/about/index.html
```

Expected: each command prints at least one match.

- [ ] **Step 9: Commit secondary pages**

Run:

```bash
git add _config.yml _layouts/page.html _layouts/categories.html pages/topics.md pages/projects.md pages/open-source.md pages/about.md
git commit -m "feat: add workbench topic and project pages"
```

Expected:

```text
[codex/indie-workbench-theme ...] feat: add workbench topic and project pages
```

### Task 7: Remove GitHub API Sidebar Dependency And Search Cache Buster

**Files:**
- Modify: `_includes/sidebar-popular-repo.html`
- Modify: `_includes/sidebar-search.html`
- Modify: `_includes/footer.html`

- [ ] **Step 1: Replace popular repo sidebar**

Replace `_includes/sidebar-popular-repo.html` with:

```liquid
{% if site.components.side_bar_repo.enabled %}
<div class="boxed-group flush">
  <h3>Featured Projects</h3>
  <ul class="mini-repo-list">
    {% assign project_count = 0 %}
    {% for group in site.data.projects %}
      {% for project in group.projects %}
        {% if project_count < site.components.side_bar_repo.limit %}
        <li class="public source">
          <a href="{{ project.url }}" target="_blank" rel="noopener" class="mini-repo-list-item">
            <span class="repo-icon octicon octicon-repo"></span>
            <span class="repo-and-owner">
              <span class="repo">{{ project.name }}</span>
            </span>
            <span class="stars">
              <span class="octicon octicon-star"></span>
              {{ project.stars }}
            </span>
            <span class="repo-description">{{ project.description }}</span>
          </a>
        </li>
        {% assign project_count = project_count | plus: 1 %}
        {% endif %}
      {% endfor %}
    {% endfor %}
  </ul>
</div>
{% endif %}
```

- [ ] **Step 2: Remove search timestamp cache buster**

In `_includes/sidebar-search.html`, replace the search JSON URL construction with a stable relative URL:

```javascript
json: '{{ "/assets/search_data.json" | relative_url }}',
```

Run this command to confirm there is no timestamp expression left:

```bash
rg -n "Date\\(|now|search_data.json.*\\?" _includes/sidebar-search.html
```

Expected: command exits with status `1` and prints no matches.

- [ ] **Step 3: Quiet the footer**

In `_includes/footer.html`, keep the existing includes and script conditions, but replace the visible footer block with:

```liquid
        <div class="site-footer" role="contentinfo">
            <div class="copyright left mobile-block">
                    © {{ site.since }}
                    <span title="{{ site.author}}">{{ site.author }}</span>
                    <a href="javascript:window.scrollTo(0,0)" class="right mobile-visible">TOP</a>
            </div>

            <ul class="site-footer-links mobile-hidden">
                {% for nav in site.navs %}
                <li>
                    <a href="{{ site.url }}{{ nav.href }}" title="{{ nav.label }}" target="{{ nav.target | default: _self }}">{{ nav.label }}</a>
                </li>
                {% endfor %}
                <li><a href="{{ site.github.repository_url }}" target="_blank" rel="noopener">GitHub</a></li>
                <li><a href="{{ site.url }}{{ site.subscribe_rss }}">RSS</a></li>
            </ul>

          {% include visit-stat.html %}

        </div>
```

- [ ] **Step 4: Run full contract check**

Run:

```bash
bash scripts/check-theme-contracts.sh
```

Expected:

```text
Theme contracts passed.
```

- [ ] **Step 5: Build**

Run:

```bash
bundle exec jekyll build
```

Expected:

```text
done in
```

- [ ] **Step 6: Commit cleanup**

Run:

```bash
git add _includes/sidebar-popular-repo.html _includes/sidebar-search.html _includes/footer.html
git commit -m "fix: remove live github theme dependencies"
```

Expected:

```text
[codex/indie-workbench-theme ...] fix: remove live github theme dependencies
```

### Task 8: Final Build, Browser Verification, And PR Readiness

**Files:**
- Modify only files needed to fix issues found during verification.

- [ ] **Step 1: Run full static checks**

Run:

```bash
bash scripts/check-theme-contracts.sh
git diff --check
```

Expected:

```text
Theme contracts passed.
```

and `git diff --check` prints no output.

- [ ] **Step 2: Run production build**

Run:

```bash
bundle exec jekyll build
```

Expected:

```text
done in
```

If GitHub Metadata emits rate-limit warnings but the build succeeds, record that in the PR notes and confirm the new homepage/open-source path no longer depends on `site.github.public_repositories`.

- [ ] **Step 3: Run local server**

Run:

```bash
bundle exec jekyll serve --host 127.0.0.1 --port 4000
```

Expected:

```text
Server address: http://127.0.0.1:4000/
```

- [ ] **Step 4: Browser-check key pages**

Open these URLs in the in-app browser:

```text
http://127.0.0.1:4000/
http://127.0.0.1:4000/topics/
http://127.0.0.1:4000/projects/
http://127.0.0.1:4000/open-source/
http://127.0.0.1:4000/about/
```

Also open one generated post URL from the build output.

Verify:

- Header navigation shows 首页 / 文章 / 专题 / 项目 / 开源 / 关于.
- Homepage first screen shows the manifesto and status panel.
- Projects render from `_data/projects.yml`.
- Post page has title, metadata, reading column, TOC, and related-post section.
- Mobile viewport does not overlap text, navigation, or article content.

- [ ] **Step 5: Stop local server**

Stop the server process with `Ctrl-C`.

Expected: terminal returns to the shell prompt.

- [ ] **Step 6: Check final git state**

Run:

```bash
git status --short --branch
```

Expected: only intentional changes are present. `AGENTS.md` may remain untracked if it is still the user's local instruction file.

- [ ] **Step 7: Commit verification fixes if needed**

If Step 4 required visual or Liquid fixes, commit them:

```bash
git add _config.yml _data/workbench.yml _data/topics.yml _data/projects.yml _includes/theme _includes/header.html _includes/footer.html _includes/sidebar-popular-repo.html _includes/sidebar-search.html _layouts/default.html _layouts/page.html _layouts/categories.html _layouts/post.html assets/css/theme index.html pages scripts/check-theme-contracts.sh
git commit -m "fix: polish workbench theme verification issues"
```

Expected:

```text
[codex/indie-workbench-theme ...] fix: polish workbench theme verification issues
```

If Step 4 required no fixes, do not create an empty commit.

## Self-Review Checklist

Spec coverage:

- Theme direction is covered by Tasks 2, 3, and 4.
- Homepage workbench structure is covered by Tasks 1, 3, and 4.
- Article reading experience is covered by Task 5.
- Topic, project, open source, and about pages are covered by Task 6.
- GitHub API dependency cleanup is covered by Task 7.
- Build and browser verification are covered by Task 8.

Implementation boundaries:

- `_site/` is never edited.
- Core project data comes from `_data/projects.yml`.
- New CSS is isolated under `assets/css/theme/`.
- Existing Jekyll plugins and content collections remain unchanged.

Verification commands:

- `THEME_CONTRACT_PHASE=data bash scripts/check-theme-contracts.sh`
- `bash scripts/check-theme-contracts.sh`
- `git diff --check`
- `bundle exec jekyll build`
- `bundle exec jekyll serve --host 127.0.0.1 --port 4000`
