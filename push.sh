#!/bin/bash

# 下载sitemap.xml文件
wget -O sitemap.xml "http://www.wangyiyang.cc/sitemap.xml"

# 提取xml文件中的URL，并保存到url.txt
grep -o '<loc>.*</loc>' sitemap.xml | sed 's/<loc>\(.*\)<\/loc>/\1/' > urls.txt

# 使用curl进行推送
curl -H 'Content-Type:text/plain' --data-binary @urls.txt "http://data.zz.baidu.com/urls?site=https://www.wangyiyang.cc&token=CdA4XFsXkCy5ecpX"
