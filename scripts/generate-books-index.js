const fs = require('fs');
const path = require('path');

const BOOKS_DIR = 'books';
const OUT_FILE = 'data/books.yaml';

// 简单安全的 YAML 双引号转义
function esc(s) {
  if (s == null) return '';
  return String(s).replace(/\\/g, '\\\\').replace(/"/g, '\\"');
}

// 读取目录
const bookSlugs = fs.readdirSync(BOOKS_DIR, { withFileTypes: true })
  .filter(d => d.isDirectory())
  .map(d => d.name)
  .sort();

const books = [];

for (const slug of bookSlugs) {
  const dirPath = path.join(BOOKS_DIR, slug);
  const bookJsonPath = path.join(dirPath, 'book.json');
  if (!fs.existsSync(bookJsonPath)) {
    console.warn(`跳过 ${slug}：未找到 book.json（不是有效的 honkit 书目录）`);
    continue;
  }

  let title = slug;
  let description = '';
  let icon = '📘'; // 默认图标，Node 原生支持 UTF-8
  let order = 999;

  // 读取 book.json
  try {
    const book = JSON.parse(fs.readFileSync(bookJsonPath, 'utf8'));
    if (book.title) title = book.title;
    if (book.description) description = book.description;
  } catch (e) {
    console.warn(`${slug} 的 book.json 解析失败，使用默认值`);
  }

  // 读取可选的 site.json
  const siteJsonPath = path.join(dirPath, 'site.json');
  if (fs.existsSync(siteJsonPath)) {
    try {
      const site = JSON.parse(fs.readFileSync(siteJsonPath, 'utf8'));
      if (site.title) title = site.title;
      if (site.description) description = site.description;
      if (site.icon) icon = site.icon;
      if (site.order != null) order = Number(site.order);
    } catch (e) {
      console.warn(`${slug} 的 site.json 解析失败，忽略`);
    }
  }

  books.push({
    slug, title, description, icon, order,
    url: `/books/${slug}/`
  });
}

// 排序：先按 order，再按 title
books.sort((a, b) => a.order - b.order || a.title.localeCompare(b.title));

// 生成 YAML（所有字符串用双引号包裹，消除 BOM 问题）
const lines = [];
for (const b of books) {
  lines.push(`- slug: "${esc(b.slug)}"`);
  lines.push(`  title: "${esc(b.title)}"`);
  lines.push(`  description: "${esc(b.description)}"`);
  lines.push(`  icon: "${esc(b.icon)}"`);
  lines.push(`  order: ${b.order}`);
  lines.push(`  url: "${esc(b.url)}"`);
}

// 确保输出目录存在
const outDir = path.dirname(OUT_FILE);
if (outDir && !fs.existsSync(outDir)) {
  fs.mkdirSync(outDir, { recursive: true });
}

// 写入文件（Node 默认写 UTF-8 无 BOM）
fs.writeFileSync(OUT_FILE, lines.join('\n') + '\n');

console.log(`✅ 已生成 ${OUT_FILE}，共 ${books.length} 本书：`);
books.forEach(b => console.log(`  - ${b.title} → ${b.url}`));