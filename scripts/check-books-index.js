const fs = require('fs');
const path = require('path');

// 指向实际存放书籍内容的目录
const BOOKS_BASE_DIR = 'books/';
// 排除非书籍的系统文件或目录
const IGNORE_DIRS = ['_gen'];

if (!fs.existsSync(BOOKS_BASE_DIR)) {
  console.error(`❌ 错误：未找到 ${BOOKS_BASE_DIR} 目录`);
  process.exit(1);
}

const bookSlugs = fs.readdirSync(BOOKS_BASE_DIR, { withFileTypes: true })
  .filter(d => d.isDirectory() && !IGNORE_DIRS.includes(d.name))
  .map(d => d.name)
  .sort();

let totalBooks = 0;
let missingConfigCount = 0;

console.log(`🔍 开始检测 ${BOOKS_BASE_DIR} 目录下的书籍配置...\n`);

for (const slug of bookSlugs) {
  const dirPath = path.join(BOOKS_BASE_DIR, slug);
  const bookJsonPath = path.join(dirPath, 'book.json');
  const siteJsonPath = path.join(dirPath, 'site.json');

  const hasBookJson = fs.existsSync(bookJsonPath);
  const hasSiteJson = fs.existsSync(siteJsonPath);

  // 如果是 _index.md 所在的目录或者是其他非书籍目录，可以进一步过滤
  // 这里我们认为如果目录里没有 book.json 或 site.json，可能不是要构建的书籍
  if (!hasBookJson && !hasSiteJson) {
     continue; // 跳过不包含配置的目录
  }

  totalBooks++;
  console.log(`✅ [通过] ${slug} -> 发现配置: ${hasBookJson ? 'book.json' : ''} ${hasSiteJson ? 'site.json' : ''}`);
}
console.log('\n----------------------------------------');
console.log(`📊 检测完成：共扫描 ${bookSlugs.length} 个目录，确认 ${totalBooks} 本书籍。`);


