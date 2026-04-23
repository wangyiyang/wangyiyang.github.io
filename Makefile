# 定义变量
JEKYLL = bundle exec jekyll
SASS = bundle exec sass
QSHELL ?= qshell
SITE_DIR ?= _site
ifneq (,$(wildcard .env))
include .env
export
endif

QINIU_BUCKET ?= blog-wangyy
QINIU_ACCOUNT_NAME ?= blog-wangyy

# 定义目标
all: build

build:
	$(JEKYLL) build

serve:
	$(JEKYLL) serve

sass:
	$(SASS) --watch _sass:css

clean:
	$(JEKYLL) clean

check-qshell:
	@command -v $(QSHELL) >/dev/null 2>&1 || { \
		echo "错误：未找到 $(QSHELL)，请先安装 qshell 并完成七牛账号配置。"; \
		echo "参考：https://developer.qiniu.com/kodo/1302/qshell"; \
		exit 1; \
	}

check-qiniu-bucket:
	@test -n "$(QINIU_BUCKET)" || { \
		echo "错误：未找到 QINIU_BUCKET，请在 .env 中配置。"; \
		exit 1; \
	}

check-qiniu-account:
	@env_file="./.env"; \
	if [ -f "$$env_file" ]; then \
		set -a; . "$$env_file"; set +a; \
	fi; \
	test -n "$${QINIU_AK:-}" || { \
		echo "错误：未找到 QINIU_AK，请在 .env 中配置。"; \
		exit 1; \
	}; \
	test -n "$${QINIU_SK:-}" || { \
		echo "错误：未找到 QINIU_SK，请在 .env 中配置。"; \
		exit 1; \
	}

qiniu-login: check-qshell check-qiniu-account
	@env_file="./.env"; \
	if [ -f "$$env_file" ]; then \
		set -a; . "$$env_file"; set +a; \
	fi; \
	account_name="$${QINIU_USERNAME:-$(QINIU_ACCOUNT_NAME)}"; \
	$(QSHELL) account --overwrite "$${QINIU_AK}" "$${QINIU_SK}" "$$account_name" >/dev/null; \
	echo "已配置 qshell 账号别名：$$account_name"

cdn-upload:
	@test -d "$(SITE_DIR)" || { \
		echo "错误：未找到 $(SITE_DIR) 目录，请先运行 make build。"; \
		exit 1; \
	}
	$(QSHELL) qupload2 --src-dir="$(SITE_DIR)" --bucket="$(QINIU_BUCKET)" --overwrite --rescan-local

cdn-sync: check-qshell check-qiniu-bucket qiniu-login clean build cdn-upload

syncfile: cdn-sync

.PHONY: all build serve sass clean check-qshell check-qiniu-bucket check-qiniu-account qiniu-login cdn-upload cdn-sync syncfile
