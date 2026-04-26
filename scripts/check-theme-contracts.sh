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
