#!/usr/bin/env bash

set -u

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
checks=0
failures=0

pass() {
  checks=$((checks + 1))
  printf 'PASS: %s\n' "$1"
}

fail() {
  failures=$((failures + 1))
  printf 'FAIL: %s\n' "$1" >&2
}

expect_contains() {
  local file="$1"
  local pattern="$2"
  local label="$3"
  local result

  grep -Fq -- "$pattern" "$root_dir/$file"
  result=$?
  case "$result" in
    0) pass "$label" ;;
    1) fail "$label" ;;
    *) fail "${label}（检查执行失败：${file}，grep 退出码 ${result}）" ;;
  esac
}

expect_absent() {
  local file="$1"
  local pattern="$2"
  local label="$3"
  local result

  grep -Fq -- "$pattern" "$root_dir/$file"
  result=$?
  case "$result" in
    0) fail "$label" ;;
    1) pass "$label" ;;
    *) fail "${label}（检查执行失败：${file}，grep 退出码 ${result}）" ;;
  esac
}

expect_tree_absent() {
  local directory="$1"
  local pattern="$2"
  local label="$3"
  local result

  grep -REiq -- "$pattern" "$root_dir/$directory"
  result=$?
  case "$result" in
    0) fail "$label" ;;
    1) pass "$label" ;;
    *) fail "${label}（检查执行失败：${directory}，grep 退出码 ${result}）" ;;
  esac
}

check_foundations() {
  expect_contains 'assets/css/theme/tokens.css' '--yx-carbon: #0A0A0A;' '定义碳黑 token'
  expect_contains 'assets/css/theme/tokens.css' '--yx-off-white: #FAFAFA;' '定义冷白 token'
  expect_contains 'assets/css/theme/tokens.css' '--yx-terminal: #00E676;' '定义终端绿 token'
  expect_contains 'assets/css/theme/tokens.css' '"Noto Sans SC"' '使用思源黑字体'
  expect_absent 'assets/css/theme/tokens.css' '--yx-vermilion' '移除朱红 token'
  expect_absent 'assets/css/theme/tokens.css' '--yx-gold' '移除哑金 token'
  expect_contains '_includes/header.html' 'family=Noto+Sans+SC' '请求思源黑字体'
  expect_absent '_includes/header.html' 'family=Noto+Serif+SC' '不再请求思源宋体'
}

check_shell() {
  expect_absent '_includes/header.html' 'class="site-logo"' '头部移除旧 logo 类'
  expect_absent '_includes/footer.html' 'yixing-logo.svg' '页脚移除旧 logo 资源'
  expect_absent '_includes/theme/post-header.html' 'yixing-logo.svg' '文章头部移除旧 logo 资源'
  expect_contains '_includes/header.html' 'brand-signal' '头部使用信号品牌标识'
  expect_contains '_includes/footer.html' 'footer-brand' '页脚使用品牌标识'
  expect_contains '_includes/theme/post-header.html' 'post-hero-brand' '文章头部使用品牌标识'
}

check_home() {
  expect_absent '_includes/theme/hero-manifesto.html' 'yixing-hero-banner.jpg' '首页移除旧横幅图'
  expect_contains '_includes/theme/hero-manifesto.html' 'workbench-hero-panel' '首页包含工作台面板'
  expect_contains '_includes/theme/hero-manifesto.html' 'workbench-signal-line' '首页包含工作台信号线'
  expect_contains '_includes/theme/featured-posts.html' 'featured-post-list' '精选文章使用列表结构'
  expect_absent 'assets/css/theme/featured-posts.css' 'box-shadow' '精选文章不使用阴影'
}

check_reading() {
  expect_contains 'assets/css/theme/base.css' 'var(--theme-accent)' '基础样式使用主题强调色'
  expect_contains 'assets/css/theme/base.css' 'prefers-reduced-motion' '基础样式支持减少动画'
  expect_absent '_includes/theme/post-toc.html' 'style=' '目录不含内联样式'
  expect_tree_absent 'assets/css/theme' '#C0392B|#D4A84B|#9E2B20|#E04A3A' '主题目录不含旧配色'
  expect_tree_absent 'assets/css/theme' 'theme-font-serif|Noto Serif SC' '主题目录不含衬线字体'
}

run_checks() {
  case "$1" in
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
      printf '用法: %s {foundations|shell|home|reading|all}\n' "$0" >&2
      exit 2
      ;;
  esac
}

run_checks "${1:-all}"

if [ "$failures" -gt 0 ]; then
  printf '%s checks passed, %s checks failed\n' "$checks" "$failures" >&2
  exit 1
fi

printf '%s checks passed\n' "$checks"
