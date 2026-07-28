const fs = require('fs');
const path = require('path');

const BOOKS_DIR = 'books';

// 检查 books 目录是否存在
if (!fs.existsSync(BOOKS_DIR)) {
  console.error(`❌ 错误：未找到 ${BOOKS_DIR} 目录`);
  process.exit(1);
}

// 读取 books 目录下的所有子目录
const bookSlugs = fs.readdirSync(BOOKS_DIR, { withFileTypes: true })
  .filter(d => d.isDirectory())
  .map(d => d.name)
  .sort();

let totalBooks = 0;
let missingConfigCount = 0;

console.log('🔍 开始检测 books 目录下的书籍配置...\n');

for (const slug of bookSlugs) {
  const dirPath = path.join(BOOKS_DIR, slug);
  const bookJsonPath = path.join(dirPath, 'book.json');
  const siteJsonPath = path.join(dirPath, 'site.json');

  const hasBookJson = fs.existsSync(bookJsonPath);
  const hasSiteJson = fs.existsSync(siteJsonPath);

  totalBooks++;

  if (!hasBookJson && !hasSiteJson) {
    missingConfigCount++;
    console.warn(`⚠️  [缺失配置] ${slug}：既未找到 book.json，也未找到 site.json`);
  } else {
    const foundFiles = [];
    if (hasBookJson) foundFiles.push('book.json');
    if (hasSiteJson) foundFiles.push('site.json');
    console.log(`✅ [通过] ${slug} -> 发现配置: ${foundFiles.join(', ')}`);
  }
}

console.log('\n----------------------------------------');
console.log(`📊 检测完成：共检查 ${totalBooks} 本书，发现 ${missingConfigCount} 个目录缺少配置文件。`);

// 如果有缺失配置的书籍，可根据需要设置退出码（常用于 CI/CD 检查）
if (missingConfigCount > 0) {
  process.exit(1);
}