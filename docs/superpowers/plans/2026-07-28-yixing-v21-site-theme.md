# 翊行代码 v2.1 全站主题改造 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在保留 Jekyll 内容架构和既有功能的前提下，将全站视觉升级为碳黑、冷白、终端绿构成的 v2.1 工业极简主题。

**Architecture:** 继续使用 `assets/css/theme/main.css` 聚合现有主题模块，以 `tokens.css` 作为唯一视觉变量来源，通过小范围调整 Liquid includes 提供 Hero、品牌状态灯和编辑式列表所需的语义结构。新增一个静态主题契约脚本，分阶段验证颜色、字体、旧资产引用、关键结构和最终 Jekyll 构建。

**Tech Stack:** Jekyll 3.9、Liquid、HTML5、CSS Custom Properties、Bash、ripgrep、Bundler

---

## 文件结构与职责

### 新增文件

- `scripts/check-theme-v21.sh`：按 foundations、shell、home、reading、all 五种模式验证 v2.1 主题契约。

### 修改文件

- `Makefile`：增加 `check-theme` 统一验收入口。
- `assets/css/theme/tokens.css`：定义三色、字体、间距、圆角和明暗模式变量。
- `_includes/header.html`：加载思源黑字体并将旧 Logo 替换为文字品牌与状态灯。
- `_includes/footer.html`：将旧 Logo 替换为文字品牌与状态灯。
- `_includes/theme/post-header.html`：将文章头部旧 Logo 替换为品牌状态标记。
- `_includes/theme/hero-manifesto.html`：用语义化 HTML 构建黑白双空间 Hero。
- `_includes/theme/featured-posts.html`：将精选卡片改为编辑式编号列表。
- `_includes/theme/post-toc.html`：删除内联样式，为 TOC 与二维码提供稳定类名。
- `assets/css/theme/base.css`：统一正文、焦点、代码、引用、图片、表格和 reduced-motion。
- `assets/css/theme/layout.css`：调整主题容器与移动端断点。
- `assets/css/theme/components.css`：统一按钮、导航、品牌状态灯、文章列表和页脚。
- `assets/css/theme/featured-posts.css`：将卡片墙改为无阴影编辑式列表。
- `assets/css/theme/pages-home.css`：实现双空间 Hero、首页双栏和仪器面板侧栏。
- `assets/css/theme/pages-post.css`：实现文章 Header、TOC 和文章尾部的 v2.1 样式。
- `assets/css/theme/pages-page.css`：统一普通页面标题与留白。
- `assets/css/theme/post-hero-image.css`：移除封面大圆角、阴影和缩放动效。

### 保留不动

- `images/yixing-logo.svg`、现有 favicon：作为历史资产保留，等待独立 Logo 重绘任务。
- `images/yixing-hero-banner.jpg`：不再被页面引用，但本轮不删除。
- `_data/workbench.yml`：保留当前站点文案与内容数据。
- `_site/`：只由 Jekyll 生成，不直接编辑。

## Task 1：建立主题契约并替换基础 Token

**Files:**

- Create: `scripts/check-theme-v21.sh`
- Modify: `Makefile:1-72`
- Modify: `assets/css/theme/tokens.css:1-55`
- Modify: `_includes/header.html:10-12,45-51`

- [ ] **Step 1：写入分阶段主题契约脚本**

创建 `scripts/check-theme-v21.sh`：

```bash
#!/usr/bin/env bash
set -euo pipefail

failures=0
checks=0

pass() {
  checks=$((checks + 1))
  printf 'PASS: %s\n' "$1"
}

fail() {
  checks=$((checks + 1))
  failures=$((failures + 1))
  printf 'FAIL: %s\n' "$1" >&2
}

expect_contains() {
  local file=$1
  local text=$2
  local description=$3
  if rg -Fq -- "$text" "$file"; then
    pass "$description"
  else
    fail "$description"
  fi
}

expect_absent() {
  local file=$1
  local text=$2
  local description=$3
  if rg -Fq -- "$text" "$file"; then
    fail "$description"
  else
    pass "$description"
  fi
}

expect_tree_absent() {
  local pattern=$1
  local description=$2
  shift 2
  if rg -q -- "$pattern" "$@"; then
    fail "$description"
  else
    pass "$description"
  fi
}

check_foundations() {
  expect_contains assets/css/theme/tokens.css '--yx-carbon: #0A0A0A;' '定义碳黑'
  expect_contains assets/css/theme/tokens.css '--yx-off-white: #FAFAFA;' '定义冷白'
  expect_contains assets/css/theme/tokens.css '--yx-terminal: #00E676;' '定义终端绿'
  expect_contains assets/css/theme/tokens.css '"Noto Sans SC"' '主题字体包含思源黑'
  expect_absent assets/css/theme/tokens.css '--yx-vermilion' 'Token 移除朱红'
  expect_absent assets/css/theme/tokens.css '--yx-gold' 'Token 移除哑金'
  expect_contains _includes/header.html 'family=Noto+Sans+SC' '页面加载思源黑'
  expect_absent _includes/header.html 'family=Noto+Serif+SC' '页面不再加载思源宋'
}

check_shell() {
  expect_absent _includes/header.html 'class="site-logo"' '页头品牌区不展示旧 Logo'
  expect_absent _includes/footer.html 'yixing-logo.svg' '页脚不引用旧 Logo'
  expect_absent _includes/theme/post-header.html 'yixing-logo.svg' '文章头部不引用旧 Logo'
  expect_contains _includes/header.html 'brand-signal' '页头包含状态灯'
  expect_contains _includes/footer.html 'footer-brand' '页脚包含文字品牌'
  expect_contains _includes/theme/post-header.html 'post-hero-brand' '文章头部包含文字品牌'
}

check_home() {
  expect_absent _includes/theme/hero-manifesto.html 'yixing-hero-banner.jpg' '首页不引用水墨 Hero'
  expect_contains _includes/theme/hero-manifesto.html 'workbench-hero-panel' '首页包含系统面板'
  expect_contains _includes/theme/hero-manifesto.html 'workbench-signal-line' '首页包含信号线'
  expect_contains _includes/theme/featured-posts.html 'featured-post-list' '精选文章使用编辑式列表'
  expect_absent assets/css/theme/featured-posts.css 'box-shadow' '精选文章不使用阴影'
}

check_reading() {
  expect_contains assets/css/theme/base.css 'var(--theme-accent)' '正文使用主题强调色'
  expect_contains assets/css/theme/base.css 'prefers-reduced-motion' '支持减少动态效果'
  expect_absent _includes/theme/post-toc.html 'style=' '文章 TOC 无内联样式'
  expect_tree_absent '#C0392B|#D4A84B|#9E2B20|#E04A3A' \
    '主题 CSS 不含旧红金色' assets/css/theme
  expect_tree_absent 'theme-font-serif|Noto Serif SC' \
    '主题 CSS 不含旧宋体角色' assets/css/theme
}

run_mode=${1:-all}
case "$run_mode" in
  foundations) check_foundations ;;
  shell) check_shell ;;
  home) check_home ;;
  reading) check_reading ;;
  all)
    check_foundations
    check_shell
    check_home
    check_reading
    ;;
  *)
    printf 'Usage: %s [foundations|shell|home|reading|all]\n' "$0" >&2
    exit 2
    ;;
esac

if ((failures > 0)); then
  printf '%s/%s checks failed\n' "$failures" "$checks" >&2
  exit 1
fi

printf '%s checks passed\n' "$checks"
```

- [ ] **Step 2：运行基础契约并确认失败**

Run:

```bash
bash scripts/check-theme-v21.sh foundations
```

Expected: FAIL，至少报告缺少 `--yx-terminal`、仍存在 `--yx-vermilion`、仍加载 `Noto Serif SC`。

- [ ] **Step 3：用三色系统完整替换主题 Token**

将 `assets/css/theme/tokens.css` 替换为：

```css
:root {
  --yx-carbon: #0A0A0A;
  --yx-off-white: #FAFAFA;
  --yx-terminal: #00E676;

  --theme-bg: var(--yx-off-white);
  --theme-surface: rgba(10, 10, 10, 0.025);
  --theme-surface-strong: rgba(10, 10, 10, 0.055);
  --theme-text: var(--yx-carbon);
  --theme-muted: rgba(10, 10, 10, 0.58);
  --theme-subtle: rgba(10, 10, 10, 0.38);
  --theme-border: rgba(10, 10, 10, 0.1);
  --theme-border-strong: rgba(10, 10, 10, 0.2);
  --theme-accent: var(--yx-terminal);
  --theme-code-bg: var(--yx-carbon);
  --theme-code-text: var(--yx-off-white);
  --theme-code-muted: rgba(250, 250, 250, 0.55);
  --theme-focus-ring: 0 0 0 2px var(--theme-bg), 0 0 0 4px var(--theme-accent);
  --theme-radius-sm: 2px;
  --theme-radius-md: 4px;
  --theme-container: 1120px;
  --theme-reading: 680px;
  --theme-space-1: 0.25rem;
  --theme-space-2: 0.5rem;
  --theme-space-3: 0.75rem;
  --theme-space-4: 1rem;
  --theme-space-5: 1.25rem;
  --theme-space-6: 1.5rem;
  --theme-space-8: 2rem;
  --theme-space-10: 2.5rem;
  --theme-space-12: 3rem;
  --theme-space-16: 4rem;
  --theme-font-sans: "Inter", "Noto Sans SC", "Source Han Sans SC",
    -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --theme-font-mono: "JetBrains Mono", "SFMono-Regular", "Fira Code",
    Consolas, "Liberation Mono", Menlo, monospace;
}

[data-theme="dark"] {
  --theme-bg: var(--yx-carbon);
  --theme-surface: rgba(250, 250, 250, 0.04);
  --theme-surface-strong: rgba(250, 250, 250, 0.08);
  --theme-text: var(--yx-off-white);
  --theme-muted: rgba(250, 250, 250, 0.6);
  --theme-subtle: rgba(250, 250, 250, 0.4);
  --theme-border: rgba(250, 250, 250, 0.12);
  --theme-border-strong: rgba(250, 250, 250, 0.22);
  --theme-code-bg: var(--yx-carbon);
  --theme-code-text: var(--yx-off-white);
  --theme-focus-ring: 0 0 0 2px var(--theme-bg), 0 0 0 4px var(--theme-accent);
}
```

- [ ] **Step 4：替换字体请求和 Favicon 信号色**

在 `_includes/header.html` 中将 Google Fonts 请求替换为：

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Noto+Sans+SC:wght@400;500;700&display=swap" rel="stylesheet">
```

将现有 mask icon 的颜色改为终端绿：

```html
<link rel="mask-icon" href="{{ site.url }}/images/yixing-logo.svg?v=2" color="#00E676">
```

这里只改 mask color，不更换 favicon 资产。

- [ ] **Step 5：在 Makefile 中增加统一检查入口**

在 `Makefile` 的 `clean` 目标后增加：

```make
check-theme:
	bash scripts/check-theme-v21.sh all
	$(JEKYLL) build
```

将 `.PHONY` 行更新为：

```make
.PHONY: all build serve clean check-theme check-qshell check-qiniu-bucket check-qiniu-account qiniu-login cdn-upload cdn-sync syncfile
```

- [ ] **Step 6：验证基础契约通过**

Run:

```bash
bash scripts/check-theme-v21.sh foundations
```

Expected: `8 checks passed`。

- [ ] **Step 7：提交基础系统**

```bash
git add scripts/check-theme-v21.sh Makefile assets/css/theme/tokens.css _includes/header.html
git commit -m "feat: establish v2.1 theme foundations"
```

## Task 2：重塑页头、文章品牌标记与页脚

**Files:**

- Modify: `_includes/header.html:174-190`
- Modify: `_includes/footer.html:1-26`
- Modify: `_includes/theme/post-header.html:1-16`
- Modify: `assets/css/theme/components.css:1-204`
- Modify: `assets/css/theme/pages-post.css:25-49`

- [ ] **Step 1：运行站点外壳契约并确认失败**

Run:

```bash
bash scripts/check-theme-v21.sh shell
```

Expected: FAIL，报告页头、页脚和文章头部仍引用旧 Logo。

- [ ] **Step 2：替换页头品牌结构**

将 `_includes/header.html` 中 `.site-brand` 内容替换为：

```html
<div class="site-brand-wrapper">
  <a href="{{ site.url }}/" title="{{ site.title }}" class="site-brand">
    <span class="site-brand-name">翊行代码</span>
    <span class="brand-signal" aria-hidden="true"></span>
  </a>
</div>
```

保留现有移动菜单按钮、导航循环和主题切换按钮。

- [ ] **Step 3：替换文章头部品牌结构**

将 `_includes/theme/post-header.html` 中 `.post-hero-logo` 替换为：

```html
<div class="post-hero-brand">
  <span>翊行代码</span>
  <span class="post-hero-brand-state">EDITORIAL / ONLINE</span>
</div>
```

保留日期、分类、阅读时间、标题、描述、标签和可选封面逻辑。

- [ ] **Step 4：替换页脚品牌结构**

将 `_includes/footer.html` 中 copyright 区域替换为：

```html
<div class="copyright left mobile-block">
  <span class="footer-brand">
    <span class="brand-signal" aria-hidden="true"></span>
    <span>© {{ site.time | date: "%Y" }} 翊行代码</span>
  </span>
  <span class="footer-domain">wangyiyang.cc</span>
  <a href="javascript:window.scrollTo(0,0)" class="right mobile-visible">TOP</a>
</div>
```

页脚导航、统计与脚本保持不变。

- [ ] **Step 5：重写通用组件的品牌与交互样式**

在 `assets/css/theme/components.css` 中：

1. 保留 `.theme-list`、`.theme-meta`、`.theme-tags` 的现有职责。
2. 用以下规则替换按钮、页头、导航、旧 `.site-logo` / `.footer-seal` 和主题切换相关规则：

```css
.theme-button {
  align-items: center;
  background: transparent;
  border: 1px solid var(--theme-border-strong);
  border-radius: var(--theme-radius-sm);
  color: var(--theme-text);
  display: inline-flex;
  font-weight: 600;
  gap: var(--theme-space-2);
  min-height: 40px;
  padding: 0 var(--theme-space-4);
  text-decoration: none;
  transition: border-color 180ms ease, transform 180ms ease;
}

.theme-button-primary {
  background: var(--theme-text);
  border-color: var(--theme-text);
  color: var(--theme-bg);
}

.theme-button:hover,
.theme-button:focus-visible {
  border-color: var(--theme-accent);
  color: inherit;
  text-decoration: none;
  transform: translateY(-1px);
}

.brand-signal {
  background: var(--theme-accent);
  display: inline-block;
  flex: 0 0 auto;
  height: 7px;
  width: 7px;
}

.site-header {
  background: var(--theme-bg);
  border-bottom: 1px solid var(--theme-border);
}

.site-header .container {
  align-items: center;
  display: flex;
  justify-content: space-between;
  margin: 0 auto;
  max-width: var(--theme-container);
  padding: 16px var(--theme-space-4);
}

.site-header .container::before,
.site-header .container::after {
  display: none;
}

.site-brand {
  align-items: center;
  color: var(--theme-text);
  display: inline-flex;
  gap: 10px;
  text-decoration: none;
}

.site-brand-name {
  font-family: var(--theme-font-sans);
  font-size: 1.12rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  line-height: 1;
}

.site-brand:hover {
  color: var(--theme-text);
  text-decoration: none;
}

.site-header-nav {
  align-items: center;
  display: flex;
  float: none;
  gap: 4px;
  margin-bottom: 0;
}

.site-header-nav-item {
  border-bottom: 1px solid transparent;
  color: var(--theme-text);
  font-size: 0.95rem;
  font-weight: 500;
  padding: 6px 12px;
  text-decoration: none;
  transition: border-color 180ms ease;
}

.site-header-nav-item.selected,
.site-header-nav-item:hover,
.site-header-nav-item:focus-visible {
  border-bottom-color: var(--theme-accent);
  color: var(--theme-text);
  text-decoration: none;
}

.theme-toggle {
  align-items: center;
  background: transparent;
  border: 1px solid var(--theme-border);
  border-radius: var(--theme-radius-sm);
  color: var(--theme-muted);
  cursor: pointer;
  display: inline-flex;
  font-size: 0.85rem;
  height: 32px;
  justify-content: center;
  padding: 0 var(--theme-space-3);
  transition: border-color 180ms ease, color 180ms ease;
}

.theme-toggle:hover,
.theme-toggle:focus-visible {
  border-color: var(--theme-accent);
  color: var(--theme-text);
}

.theme-toggle .theme-toggle-dark,
[data-theme="dark"] .theme-toggle .theme-toggle-light {
  display: none;
}

.theme-toggle .theme-toggle-light,
[data-theme="dark"] .theme-toggle .theme-toggle-dark {
  display: inline;
}

.footer-brand {
  align-items: center;
  color: var(--theme-text);
  display: inline-flex;
  font-weight: 700;
  gap: var(--theme-space-2);
  letter-spacing: 0.06em;
}

.footer-domain {
  color: var(--theme-muted);
  font-family: var(--theme-font-mono);
  font-size: 0.78rem;
  margin-left: var(--theme-space-3);
}

.site-footer a {
  color: var(--theme-muted);
}

.site-footer a:hover,
.site-footer a:focus-visible {
  color: var(--theme-text);
  text-decoration-color: var(--theme-accent);
}
```

- [ ] **Step 6：调整文章品牌标记样式**

将 `assets/css/theme/pages-post.css` 中 `.post-hero-logo` 相关规则替换为：

```css
.post-hero-brand {
  align-items: center;
  color: var(--theme-muted);
  display: flex;
  font-family: var(--theme-font-mono);
  font-size: 0.76rem;
  gap: var(--theme-space-3);
  letter-spacing: 0.08em;
  margin-bottom: var(--theme-space-6);
  text-transform: uppercase;
}

.post-hero-brand-state {
  border-left: 1px solid var(--theme-border-strong);
  padding-left: var(--theme-space-3);
}

.post-title {
  color: var(--theme-text);
  font-family: var(--theme-font-sans);
  font-size: clamp(2rem, 4.5vw, 3.4rem);
  font-weight: 700;
  letter-spacing: -0.03em;
  line-height: 1.2;
  margin: var(--theme-space-3) 0;
}
```

- [ ] **Step 7：验证站点外壳契约与构建**

Run:

```bash
bash scripts/check-theme-v21.sh shell
bundle exec jekyll build
```

Expected: shell 契约 `6 checks passed`；Jekyll 以 `done` 结束。

- [ ] **Step 8：提交站点外壳**

```bash
git add _includes/header.html _includes/footer.html _includes/theme/post-header.html assets/css/theme/components.css assets/css/theme/pages-post.css
git commit -m "feat: restyle site shell for v2.1"
```

## Task 3：将首页 Hero 重建为黑白系统面板

**Files:**

- Modify: `_includes/theme/hero-manifesto.html:1-17`
- Modify: `assets/css/theme/pages-home.css:1-94,204-224`

- [ ] **Step 1：运行首页契约并确认失败**

Run:

```bash
bash scripts/check-theme-v21.sh home
```

Expected: FAIL，报告仍引用水墨 Hero，缺少系统面板和信号线。

- [ ] **Step 2：替换 Hero 语义结构**

将 `_includes/theme/hero-manifesto.html` 替换为：

```html
{% assign manifesto = site.data.workbench.manifesto %}
<section class="workbench-hero">
  <div class="theme-container workbench-hero-grid">
    <div class="workbench-hero-content">
      <p class="workbench-eyebrow">
        WANGYIYANG.CC / ONLINE
      </p>
      <h1 class="workbench-title">{{ manifesto.title }}</h1>
      <p class="workbench-tagline">Code, one stroke at a time.</p>
      <p class="workbench-description">{{ manifesto.description }}</p>
      <div class="workbench-actions">
        {% for action in manifesto.actions %}
        <a class="theme-button {% if action.primary %}theme-button-primary{% endif %}" href="{{ action.url | relative_url }}">{{ action.label }}</a>
        {% endfor %}
      </div>
    </div>
    <div class="workbench-signal-line" aria-hidden="true"></div>
    <div class="workbench-hero-panel" aria-hidden="true">
      <div class="workbench-panel-head">
        <span>YY / SYSTEM</span>
        <span>RUNNING</span>
      </div>
      <div class="workbench-panel-grid">
        <span>01 / CODE</span>
        <span>02 / AI</span>
        <span>03 / AGENTS</span>
        <span>04 / SYSTEMS</span>
      </div>
      <div class="workbench-panel-axis"></div>
      <div class="workbench-panel-status">
        SIGNAL STABLE
      </div>
    </div>
  </div>
</section>
```

- [ ] **Step 3：用双空间布局替换旧水墨 Hero 样式**

将 `assets/css/theme/pages-home.css` 的 Hero 规则替换为：

```css
.workbench-hero {
  border-bottom: 1px solid var(--theme-border);
  min-height: clamp(440px, 58vh, 580px);
  overflow: hidden;
  position: relative;
}

.workbench-hero-grid {
  display: grid;
  grid-template-columns: minmax(0, 7fr) 1px minmax(300px, 5fr);
  min-height: inherit;
  padding-bottom: 0;
  padding-top: 0;
}

.workbench-hero-content {
  align-self: center;
  max-width: 620px;
  padding: var(--theme-space-12) var(--theme-space-16) var(--theme-space-12) 0;
}

.workbench-eyebrow {
  align-items: center;
  color: var(--theme-muted);
  display: flex;
  font-family: var(--theme-font-mono);
  font-size: 0.72rem;
  gap: var(--theme-space-3);
  letter-spacing: 0.1em;
  margin: 0 0 var(--theme-space-8);
}

.workbench-title {
  color: var(--theme-text);
  font-family: var(--theme-font-sans);
  font-size: clamp(3rem, 7vw, 6.4rem);
  font-weight: 700;
  letter-spacing: -0.06em;
  line-height: 0.95;
  margin: 0;
}

.workbench-tagline {
  color: var(--theme-text);
  font-family: var(--theme-font-mono);
  font-size: clamp(0.82rem, 1.4vw, 1rem);
  letter-spacing: 0.04em;
  margin: var(--theme-space-6) 0 0;
}

.workbench-description {
  color: var(--theme-muted);
  font-size: 1rem;
  line-height: 1.8;
  margin: var(--theme-space-4) 0 0;
  max-width: 540px;
}

.workbench-actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--theme-space-3);
  margin-top: var(--theme-space-8);
}

.workbench-signal-line {
  align-self: stretch;
  background: var(--theme-accent);
}

.workbench-hero-panel {
  align-self: stretch;
  background: var(--yx-carbon);
  color: var(--yx-off-white);
  display: grid;
  grid-template-rows: auto auto 1fr auto;
  margin-right: calc((100vw - min(100vw, var(--theme-container))) / -2);
  min-width: 0;
  padding: var(--theme-space-8);
}

[data-theme="dark"] .workbench-hero-panel {
  background: var(--yx-off-white);
  color: var(--yx-carbon);
}

.workbench-panel-head,
.workbench-panel-status {
  display: flex;
  font-family: var(--theme-font-mono);
  font-size: 0.68rem;
  justify-content: space-between;
  letter-spacing: 0.1em;
}

.workbench-panel-grid {
  border-top: 1px solid currentColor;
  display: grid;
  font-family: var(--theme-font-mono);
  font-size: 0.72rem;
  gap: var(--theme-space-3);
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin-top: var(--theme-space-8);
  opacity: 0.62;
  padding-top: var(--theme-space-4);
}

.workbench-panel-axis {
  opacity: 0.18;
  position: relative;
}

.workbench-panel-axis::before,
.workbench-panel-axis::after {
  background: currentColor;
  content: "";
  left: 50%;
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
}

.workbench-panel-axis::before {
  height: 100%;
  width: 1px;
}

.workbench-panel-axis::after {
  height: 1px;
  width: 100%;
}

.workbench-panel-status {
  align-items: center;
  justify-content: flex-start;
}
```

- [ ] **Step 4：增加 Hero 移动端布局**

在 `assets/css/theme/pages-home.css` 的媒体查询中加入：

```css
@media (max-width: 900px) {
  .workbench-hero-grid {
    grid-template-columns: 1fr;
  }

  .workbench-hero-content {
    padding: var(--theme-space-12) 0;
  }

  .workbench-signal-line {
    height: 1px;
  }

  .workbench-hero-panel {
    margin: 0 calc(var(--theme-space-4) * -1);
    min-height: 260px;
    padding: var(--theme-space-6) var(--theme-space-4);
  }
}

@media (max-width: 480px) {
  .workbench-title {
    font-size: clamp(2.8rem, 18vw, 4.4rem);
  }

  .workbench-panel-grid {
    grid-template-columns: 1fr;
  }
}
```

- [ ] **Step 5：验证首页 Hero 结构**

Run:

```bash
rg -n "yixing-hero-banner|workbench-hero-panel|workbench-signal-line" _includes/theme/hero-manifesto.html assets/css/theme/pages-home.css
bundle exec jekyll build
rg -n "workbench-hero-panel|WANGYIYANG.CC / ONLINE" _site/index.html
```

Expected:

- 源码中没有 `yixing-hero-banner`。
- 源码和 `_site/index.html` 均包含 `workbench-hero-panel`。
- Jekyll 构建成功。

- [ ] **Step 6：提交首页 Hero**

```bash
git add _includes/theme/hero-manifesto.html assets/css/theme/pages-home.css
git commit -m "feat: rebuild homepage hero as system panel"
```

## Task 4：将首页内容改为编辑式列表与仪器侧栏

**Files:**

- Modify: `_includes/theme/featured-posts.html:1-19`
- Modify: `assets/css/theme/featured-posts.css:1-79`
- Modify: `assets/css/theme/components.css:26-59`
- Modify: `assets/css/theme/pages-home.css:96-224`
- Modify: `assets/css/theme/layout.css:7-35,64-76`

- [ ] **Step 1：确认精选内容契约仍失败**

Run:

```bash
bash scripts/check-theme-v21.sh home
```

Expected: FAIL，报告精选文章尚未使用 `featured-post-list`，旧 CSS 仍含 `box-shadow`。

- [ ] **Step 2：将精选文章改为编号列表**

将 `_includes/theme/featured-posts.html` 替换为：

```html
<section class="theme-section featured-posts">
  <div class="theme-container">
    <header class="theme-section-header">
      <div class="theme-section-kicker">Featured</div>
      <h2 class="theme-section-title">{{ site.data.workbench.featured_posts.title }}</h2>
      <p class="theme-section-subtitle">{{ site.data.workbench.featured_posts.subtitle }}</p>
    </header>
    <ol class="featured-post-list">
      {% for post in site.data.workbench.featured_posts.posts %}
      <li class="featured-post-item">
        <span class="featured-post-index" aria-hidden="true">0{{ forloop.index }}</span>
        <div class="featured-post-body">
          <p class="featured-post-tag">SELECTED / {{ forloop.index }}</p>
          <h3><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h3>
          <p>{{ post.description }}</p>
        </div>
        <a href="{{ post.url | relative_url }}" class="featured-post-link" aria-label="阅读：{{ post.title }}">OPEN ↗</a>
      </li>
      {% endfor %}
    </ol>
  </div>
</section>
```

- [ ] **Step 3：重写精选文章样式**

将 `assets/css/theme/featured-posts.css` 替换为：

```css
.featured-posts {
  background: var(--theme-surface);
}

.featured-post-list {
  border-top: 1px solid var(--theme-border-strong);
  list-style: none;
  margin: 0;
  padding: 0;
}

.featured-post-item {
  align-items: start;
  border-bottom: 1px solid var(--theme-border);
  display: grid;
  gap: var(--theme-space-6);
  grid-template-columns: 48px minmax(0, 1fr) auto;
  padding: var(--theme-space-6) 0;
  position: relative;
  transition: padding-left 180ms ease;
}

.featured-post-item::before {
  background: var(--theme-accent);
  content: "";
  height: 0;
  left: 0;
  position: absolute;
  top: 0;
  transition: height 180ms ease;
  width: 2px;
}

.featured-post-item:hover,
.featured-post-item:focus-within {
  padding-left: var(--theme-space-3);
}

.featured-post-item:hover::before,
.featured-post-item:focus-within::before {
  height: 100%;
}

.featured-post-index,
.featured-post-tag,
.featured-post-link {
  font-family: var(--theme-font-mono);
  font-size: 0.72rem;
  letter-spacing: 0.08em;
}

.featured-post-index {
  color: var(--theme-subtle);
}

.featured-post-tag {
  color: var(--theme-muted);
  margin: 0 0 var(--theme-space-2);
}

.featured-post-item h3 {
  font-size: clamp(1.05rem, 2vw, 1.3rem);
  line-height: 1.4;
  margin: 0;
}

.featured-post-item h3 a {
  color: var(--theme-text);
  text-decoration: none;
}

.featured-post-body > p:last-child {
  color: var(--theme-muted);
  line-height: 1.7;
  margin: var(--theme-space-2) 0 0;
}

.featured-post-link {
  color: var(--theme-text);
  text-decoration-color: var(--theme-accent);
}

.theme-section-subtitle {
  color: var(--theme-muted);
  margin: 0;
}

@media (max-width: 640px) {
  .featured-post-item {
    grid-template-columns: 32px minmax(0, 1fr);
  }

  .featured-post-link {
    grid-column: 2;
  }
}
```

- [ ] **Step 4：将普通文章列表改为编号编辑式列表**

在 `assets/css/theme/components.css` 中用以下规则扩展现有 `.theme-list`：

```css
.theme-list {
  border-top: 1px solid var(--theme-border-strong);
  counter-reset: article;
  list-style: none;
  margin: 0;
  padding: 0;
}

.theme-list-item {
  border-bottom: 1px solid var(--theme-border);
  counter-increment: article;
  display: grid;
  gap: var(--theme-space-2) var(--theme-space-5);
  grid-template-columns: 40px minmax(0, 1fr);
  padding: var(--theme-space-6) 0;
  position: relative;
  transition: padding-left 180ms ease;
}

.theme-list-item::before {
  color: var(--theme-subtle);
  content: counter(article, decimal-leading-zero);
  font-family: var(--theme-font-mono);
  font-size: 0.72rem;
  grid-row: 1 / span 3;
}

.theme-list-item::after {
  background: var(--theme-accent);
  content: "";
  height: 0;
  left: 0;
  position: absolute;
  top: 0;
  transition: height 180ms ease;
  width: 2px;
}

.theme-list-item:hover,
.theme-list-item:focus-within {
  padding-left: var(--theme-space-3);
}

.theme-list-item:hover::after,
.theme-list-item:focus-within::after {
  height: 100%;
}

.theme-list-item h3,
.theme-list-item p,
.theme-list-item .theme-meta {
  grid-column: 2;
}

.theme-list-item h3 {
  font-size: 1.08rem;
  line-height: 1.45;
  margin: 0;
}

.theme-list-item h3 a {
  color: var(--theme-text);
  text-decoration: none;
}

.theme-list-item p {
  color: var(--theme-muted);
  line-height: 1.7;
  margin: 0;
}

.theme-meta {
  color: var(--theme-subtle);
  display: flex;
  flex-wrap: wrap;
  font-family: var(--theme-font-mono);
  font-size: 0.76rem;
  gap: var(--theme-space-3);
}
```

- [ ] **Step 5：将首页侧栏改为仪器面板**

在 `assets/css/theme/pages-home.css` 中保留首页双栏结构，并将侧栏规则调整为：

```css
.home-two-column {
  align-items: start;
  display: grid;
  gap: var(--theme-space-10);
  grid-template-columns: minmax(0, 7fr) minmax(260px, 3fr);
}

.home-sidebar {
  align-self: start;
  position: sticky;
  top: 92px;
}

.sidebar-widget {
  background: var(--theme-surface);
  border: 1px solid var(--theme-border);
  border-radius: var(--theme-radius-sm);
  margin-bottom: var(--theme-space-5);
  padding: var(--theme-space-5);
}

.sidebar-widget-title {
  border-bottom: 1px solid var(--theme-border);
  color: var(--theme-text);
  font-family: var(--theme-font-mono);
  font-size: 0.72rem;
  font-weight: 500;
  letter-spacing: 0.1em;
  margin: 0 0 var(--theme-space-4);
  padding-bottom: var(--theme-space-3);
  text-transform: uppercase;
}

.sidebar-wechat {
  text-align: center;
}

.sidebar-wechat .wechat-qr-img {
  border: 1px solid var(--theme-border);
  border-radius: var(--theme-radius-sm);
  height: 180px;
  width: 180px;
}

.sidebar-wechat .wechat-qr-caption,
.sidebar-widget-desc,
.sidebar-about p {
  color: var(--theme-muted);
  font-size: 0.85rem;
  line-height: 1.7;
}

.sidebar-topic-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.sidebar-topic-list li {
  align-items: center;
  border-bottom: 1px solid var(--theme-border);
  display: flex;
  justify-content: space-between;
  padding: var(--theme-space-2) 0;
}

.sidebar-topic-list li:last-child {
  border-bottom: 0;
}

.sidebar-topic-list a {
  color: var(--theme-text);
  font-size: 0.88rem;
  text-decoration: none;
}

.sidebar-topic-list a:hover,
.sidebar-topic-list a:focus-visible {
  text-decoration-color: var(--theme-accent);
  text-decoration-line: underline;
}

.sidebar-topic-list span {
  color: var(--theme-muted);
  font-family: var(--theme-font-mono);
  font-size: 0.75rem;
}
```

在同一文件的 `max-width: 900px` 查询中保留：

```css
@media (max-width: 900px) {
  .home-two-column {
    grid-template-columns: 1fr;
  }

  .home-sidebar {
    position: static;
  }

  .sidebar-wechat {
    display: none;
  }
}
```

- [ ] **Step 6：统一分区标题和断点**

在 `assets/css/theme/layout.css` 中确认：

```css
.theme-section {
  border-top: 1px solid var(--theme-border);
  padding: var(--theme-space-16) 0;
}

.theme-section-header {
  display: grid;
  gap: var(--theme-space-2);
  margin-bottom: var(--theme-space-8);
}

.theme-section-kicker {
  color: var(--theme-text);
  font-family: var(--theme-font-mono);
  font-size: 0.72rem;
  font-weight: 500;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.theme-section-kicker::before {
  background: var(--theme-accent);
  content: "";
  display: inline-block;
  height: 6px;
  margin-right: var(--theme-space-2);
  width: 6px;
}

.theme-section-title {
  color: var(--theme-text);
  font-size: clamp(1.5rem, 2.5vw, 2.2rem);
  line-height: 1.2;
  margin: 0;
}
```

- [ ] **Step 7：验证首页内容契约**

Run:

```bash
bash scripts/check-theme-v21.sh home
bundle exec jekyll build
```

Expected: home 契约 `5 checks passed`；Jekyll 构建成功。

- [ ] **Step 8：提交首页内容系统**

```bash
git add _includes/theme/featured-posts.html assets/css/theme/featured-posts.css assets/css/theme/components.css assets/css/theme/pages-home.css assets/css/theme/layout.css
git commit -m "feat: convert homepage content to editorial lists"
```

## Task 5：统一文章阅读与普通页面体验

**Files:**

- Modify: `assets/css/theme/base.css:1-218`
- Modify: `assets/css/theme/pages-post.css:1-167`
- Modify: `_includes/theme/post-toc.html:1-12`
- Modify: `assets/css/theme/post-hero-image.css:1-31`
- Modify: `assets/css/theme/pages-page.css:1-23`

- [ ] **Step 1：运行阅读契约并确认失败**

Run:

```bash
bash scripts/check-theme-v21.sh reading
```

Expected: FAIL，报告旧红色、旧宋体角色、TOC 内联样式和 reduced-motion 缺失。

- [ ] **Step 2：统一正文标题、链接和 Focus**

在 `assets/css/theme/base.css` 中：

```css
html,
body {
  background: var(--theme-bg);
  color: var(--theme-text);
}

body {
  font-family: var(--theme-font-sans);
  letter-spacing: 0;
}

a {
  color: var(--theme-text);
  text-decoration-color: var(--theme-accent);
  text-decoration-thickness: 1px;
  text-underline-offset: 0.18em;
}

a:hover {
  color: var(--theme-text);
  text-decoration-line: underline;
}

:focus-visible {
  box-shadow: var(--theme-focus-ring);
  outline: 0;
}

.markdown-body {
  color: var(--theme-text);
  font-family: var(--theme-font-sans);
  font-size: 16px;
  line-height: 1.8;
  margin: 0 auto;
  max-width: var(--theme-reading);
}

.markdown-body h2,
.markdown-body h3,
.markdown-body h4 {
  color: var(--theme-text);
  font-family: var(--theme-font-sans);
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.3;
  margin-top: 2.2em;
}
```

保留现有字号阶梯、段落间距和表格结构。

- [ ] **Step 3：将引用、代码和图片收敛到三色系统**

在 `assets/css/theme/base.css` 中使用：

```css
.markdown-body blockquote {
  background: var(--theme-surface);
  border-left: 4px solid var(--theme-accent);
  border-radius: 0 var(--theme-radius-sm) var(--theme-radius-sm) 0;
  color: var(--theme-muted);
  font-style: italic;
  margin-left: 0;
  margin-right: 0;
  padding: 1em 1.2em;
}

.markdown-body code,
.markdown-body tt {
  background: var(--theme-surface-strong);
  border-radius: var(--theme-radius-sm);
  font-family: var(--theme-font-mono);
  font-size: 0.875em;
  padding: 0.15em 0.35em;
}

.markdown-body pre,
.markdown-body .highlight pre {
  background: var(--theme-code-bg);
  border: 1px solid var(--theme-border-strong);
  border-radius: var(--theme-radius-md);
  color: var(--theme-code-text);
  overflow-x: auto;
}

.markdown-body pre code {
  background: transparent;
  color: inherit;
  font-family: var(--theme-font-mono);
  font-size: 14px;
  line-height: 1.5;
  padding: 0;
}

.markdown-body pre .highlight,
.markdown-body pre .hll {
  background: transparent;
}

.markdown-body pre .c,
.markdown-body pre .cm,
.markdown-body pre .cp,
.markdown-body pre .c1,
.markdown-body pre .cs,
.markdown-body pre .go,
.markdown-body pre .sd,
.markdown-body pre .w {
  color: var(--theme-code-muted);
}

.markdown-body pre .k,
.markdown-body pre .kc,
.markdown-body pre .kd,
.markdown-body pre .kn,
.markdown-body pre .kp,
.markdown-body pre .kr,
.markdown-body pre .kt,
.markdown-body pre .ow,
.markdown-body pre .nt,
.markdown-body pre .na,
.markdown-body pre .gi {
  color: var(--theme-accent);
  font-weight: 600;
}

.markdown-body pre .o,
.markdown-body pre .gd,
.markdown-body pre .ge,
.markdown-body pre .gr,
.markdown-body pre .gh,
.markdown-body pre .gp,
.markdown-body pre .gs,
.markdown-body pre .gu,
.markdown-body pre .gt,
.markdown-body pre .m,
.markdown-body pre .s,
.markdown-body pre .nb,
.markdown-body pre .nc,
.markdown-body pre .no,
.markdown-body pre .nd,
.markdown-body pre .ni,
.markdown-body pre .ne,
.markdown-body pre .nf,
.markdown-body pre .nl,
.markdown-body pre .nn,
.markdown-body pre .nx,
.markdown-body pre .py,
.markdown-body pre .nv,
.markdown-body pre .mb,
.markdown-body pre .mf,
.markdown-body pre .mh,
.markdown-body pre .mi,
.markdown-body pre .mo,
.markdown-body pre .sa,
.markdown-body pre .sb,
.markdown-body pre .sc,
.markdown-body pre .dl,
.markdown-body pre .s2,
.markdown-body pre .se,
.markdown-body pre .sh,
.markdown-body pre .si,
.markdown-body pre .sx,
.markdown-body pre .sr,
.markdown-body pre .s1,
.markdown-body pre .ss,
.markdown-body pre .bp,
.markdown-body pre .fm,
.markdown-body pre .vc,
.markdown-body pre .vg,
.markdown-body pre .vi,
.markdown-body pre .vm,
.markdown-body pre .il {
  color: var(--theme-code-text);
}

.markdown-body pre .gd,
.markdown-body pre .gi {
  background: transparent;
}

.markdown-body pre .ge,
.markdown-body pre .sd {
  font-style: italic;
}

.markdown-body pre .gs {
  font-weight: 600;
}

.markdown-body img,
.markdown-body video {
  border: 1px solid var(--theme-border);
  border-radius: var(--theme-radius-sm);
  display: block;
  height: auto;
  max-width: 100%;
}
```

以上分组覆盖现有 `base.css` 中全部 Rouge 类；删除原有逐类颜色声明，不保留红、蓝、紫、黄色值。

- [ ] **Step 4：集中 TOC 二维码样式**

将 `_includes/theme/post-toc.html` 替换为：

```html
<aside class="post-toc" aria-label="文章目录">
  <h2 class="post-toc-title">Contents</h2>
  {% include sidebar-post-nav.html %}

  <div class="post-toc-wechat">
    <h2 class="post-toc-title">公众号</h2>
    <div class="wechat-qr-wrap">
      <img src="{{ site.url }}/images/qrcode.jpg" alt="{{ site.components.qrcode.image_alt }}" class="wechat-qr-img post-toc-wechat-image" />
      <p class="wechat-qr-caption post-toc-wechat-caption">{{ site.components.qrcode.image_alt }}</p>
    </div>
  </div>
</aside>
```

在 `assets/css/theme/pages-post.css` 中加入：

```css
.post-toc {
  align-self: start;
  border-left: 1px solid var(--theme-border);
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 112px);
  padding: var(--theme-space-2) 0 var(--theme-space-2) var(--theme-space-5);
  position: sticky;
  top: 92px;
}

.post-toc-title {
  color: var(--theme-text);
  font-family: var(--theme-font-mono);
  font-size: 0.72rem;
  font-weight: 500;
  letter-spacing: 0.1em;
  margin-bottom: var(--theme-space-3);
  text-transform: uppercase;
}

.post-toc a {
  color: var(--theme-muted);
  font-size: 0.82rem;
  line-height: 1.8;
  text-decoration: none;
}

.post-toc a:hover,
.post-toc .active > a {
  color: var(--theme-text);
  text-decoration-color: var(--theme-accent);
  text-decoration-line: underline;
}

.post-toc-wechat {
  border-top: 1px solid var(--theme-border);
  flex-shrink: 0;
  margin-top: var(--theme-space-8);
  padding-top: var(--theme-space-6);
}

.post-toc-wechat-image {
  height: 140px;
  width: 140px;
}

.post-toc-wechat-caption {
  font-size: 0.78rem;
}
```

- [ ] **Step 5：统一文章 Header、封面和普通页面**

在 `assets/css/theme/pages-post.css` 中保持 `min-height: 30vh`，并让 Header 使用：

```css
.post-hero {
  align-items: flex-end;
  border-bottom: 1px solid var(--theme-border);
  display: flex;
  min-height: 30vh;
  position: relative;
}

.post-hero::after {
  background: var(--theme-accent);
  bottom: -1px;
  content: "";
  height: 2px;
  left: 0;
  position: absolute;
  width: min(18vw, 220px);
}

.post-hero-inner {
  display: grid;
  gap: var(--theme-space-12);
  grid-template-columns: minmax(0, 1fr) 260px;
  margin: 0 auto;
  max-width: var(--theme-container);
  padding: var(--theme-space-12) var(--theme-space-6);
  width: 100%;
}
```

将 `assets/css/theme/post-hero-image.css` 替换为：

```css
.post-hero-image {
  margin: var(--theme-space-8) auto 0;
  max-width: var(--theme-container);
  padding: 0 var(--theme-space-6);
}

.post-hero-image-inner {
  border: 1px solid var(--theme-border);
  border-radius: var(--theme-radius-sm);
  overflow: hidden;
}

.post-hero-image img {
  display: block;
  height: auto;
  width: 100%;
}

@media (max-width: 768px) {
  .post-hero-image {
    margin-top: var(--theme-space-4);
    padding: 0 var(--theme-space-4);
  }
}
```

在 `assets/css/theme/pages-page.css` 中将页面标题明确设为：

```css
.theme-page-title {
  color: var(--theme-text);
  font-family: var(--theme-font-sans);
  font-size: clamp(2.2rem, 5vw, 4rem);
  font-weight: 700;
  letter-spacing: -0.04em;
  line-height: 1.08;
  margin: 0;
}
```

- [ ] **Step 6：增加减少动态效果和移动端降级**

在 `assets/css/theme/base.css` 末尾增加：

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    scroll-behavior: auto !important;
    transition-duration: 0.01ms !important;
  }
}
```

在 `assets/css/theme/pages-post.css` 的 `max-width: 900px` 查询中确保：

```css
@media (max-width: 900px) {
  .post-hero-inner {
    grid-template-columns: 1fr;
    padding-left: var(--theme-space-4);
    padding-right: var(--theme-space-4);
  }

  .post-toc {
    border-left: 0;
    border-top: 1px solid var(--theme-border);
    max-height: none;
    padding: var(--theme-space-6) 0 0;
    position: static;
  }

  .post-footer-nav {
    grid-template-columns: 1fr;
  }

  #post-directory-module {
    max-height: none;
  }
}
```

- [ ] **Step 7：验证阅读契约与构建**

Run:

```bash
bash scripts/check-theme-v21.sh reading
bundle exec jekyll build
```

Expected: reading 契约 `5 checks passed`；Jekyll 构建成功，不出现 Rouge 或 Liquid 错误。

- [ ] **Step 8：提交文章与页面体验**

```bash
git add assets/css/theme/base.css assets/css/theme/pages-post.css _includes/theme/post-toc.html assets/css/theme/post-hero-image.css assets/css/theme/pages-page.css
git commit -m "feat: align reading experience with v2.1"
```

## Task 6：执行全量验收与回归修正

**Files:**

- Verify: `scripts/check-theme-v21.sh`
- Verify: `_site/index.html`
- Verify: `_site/archives/index.html`
- Verify: 任一包含代码块、引用、表格和图片的 `_site/<post>/index.html`
- Modify only if required: 本计划列出的主题 CSS 或 includes

- [ ] **Step 1：运行完整主题契约**

Run:

```bash
bash scripts/check-theme-v21.sh all
```

Expected: 所有检查通过，结尾输出 `24 checks passed`。

- [ ] **Step 2：运行项目正式构建**

Run:

```bash
bundle exec jekyll clean
JEKYLL_ENV=production bundle exec jekyll build
```

Expected: 构建以 `done` 结束；无 Liquid、Rouge、缺失 include 或 CSS 语法相关错误。

- [ ] **Step 3：验证生成结果不含旧主题引用**

Run:

```bash
rg -n "yixing-hero-banner|Noto\\+Serif\\+SC|#C0392B|#D4A84B" \
  _site/index.html _site/assets/css/theme _site/archives/index.html
```

Expected: 无输出，退出码为 1。

Run:

```bash
rg -n "workbench-hero-panel|featured-post-list|brand-signal" _site/index.html
```

Expected: 三个结构均出现在生成首页。

- [ ] **Step 4：启动本地站点进行页面矩阵检查**

Run:

```bash
bundle exec jekyll serve --host 127.0.0.1
```

在浏览器检查：

| 页面 | 375px | 768px | 1440px | 浅色 | 深色 |
|---|---:|---:|---:|---:|---:|
| 首页 `/` | 必须 | 必须 | 必须 | 必须 | 必须 |
| 文章列表 `/archives/` | 必须 | 抽查 | 必须 | 必须 | 必须 |
| 一篇长文 | 必须 | 必须 | 必须 | 必须 | 必须 |
| 普通页面 `/about/` | 必须 | 抽查 | 必须 | 必须 | 必须 |
| Wiki `/wiki/` | 抽查 | 抽查 | 必须 | 必须 | 必须 |

每个页面确认：

- 无横向滚动条。
- 页面只呈现碳黑、冷白、终端绿及其透明度派生。
- 终端绿不形成大面积色块。
- 键盘 Tab 可见清晰 focus。
- 首页 Hero 在移动端变为上下双空间。
- 文章正文宽度、代码横向滚动、引用、表格和图片正常。
- 深色模式不出现低对比度文字或消失的边框。

- [ ] **Step 5：仅修复验收发现的主题回归**

如果发现问题，只修改本计划列出的 CSS 或 includes。每次修复后运行：

```bash
bash scripts/check-theme-v21.sh all
bundle exec jekyll build
git diff --check
```

Expected: 契约全部通过、构建成功、`git diff --check` 无输出。

- [ ] **Step 6：提交验收修正**

只有存在实际修正时执行：

```bash
git add scripts/check-theme-v21.sh assets/css/theme _includes/header.html _includes/footer.html _includes/theme
git commit -m "fix: resolve v2.1 theme visual regressions"
```

如果没有产生变更，不创建空提交。

- [ ] **Step 7：记录最终状态**

Run:

```bash
git status --short --branch
git log -6 --oneline --decorate
git stash list --max-count=3
```

Expected:

- 工作区干净。
- 最近提交包含五个主题原子提交。
- 先前保存的 `保留 RAG 04.png 待确认` stash 仍然存在且未被应用。
