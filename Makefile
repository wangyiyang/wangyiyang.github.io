# 定义变量
JEKYLL = bundle exec jekyll
SASS = bundle exec sass

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

syncfile:
	qshell qupload2 --src-dir=_site --bucket=blog-wangyy

.PHONY: all build serve sass clean