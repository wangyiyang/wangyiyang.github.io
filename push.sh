#!/bin/bash

# 下载sitemap.xml文件
wget -O sitemap.xml "http://www.wangyiyang.cc/sitemap.xml"

echo "sitemap.xml下载完成"
# 提取xml文件中的URL，并保存到url.txt
grep -o '<loc>.*</loc>' sitemap.xml | sed 's/<loc>\(.*\)<\/loc>/\1/' > urls.txt
echo "urls.txt生成完成"

echo "显示urls.txt文件内容"
cat urls.txt

echo "百度链接提交开始"

# 使用curl进行推送
curl -H 'Content-Type:text/plain' --data-binary @urls.txt "http://data.zz.baidu.com/urls?site=https://www.wangyiyang.cc&token=CdA4XFsXkCy5ecpX"

echo "百度链接提交结束"
