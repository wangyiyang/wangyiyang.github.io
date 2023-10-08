import fetch from "node-fetch";
import fs from 'fs';
import path from 'path';
import chalk from 'chalk';
import matter from 'gray-matter';
import readFileList from './modules/readFileList';

const urlsRoot = path.join(__dirname, '..', 'urls.txt');
const DOMAIN = process.argv.splice(2)[0];

if (DOMAIN) {
  main();
} else {
  console.log(chalk('node utils/baiduPush.js https://www.wangyiyang.cc'));
}

/**
 * 主体函数
 */
function main() {
  fs.writeFileSync(urlsRoot, DOMAIN);
  const files = readFileList();

  files.forEach(file => {
    const { data } = matter(fs.readFileSync(file.filePath, 'utf8'));

    if (data.permalink) {
      const link = `\r\n${DOMAIN}${data.permalink}`;
      console.log(link);
      fs.appendFileSync(urlsRoot, link);
    }
  });
}

