// scripts/build-books.js
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

function buildBooks() {
    const booksDir = path.join(__dirname, '../books');
    const staticBooksDir = path.join(__dirname, '../static/resources');

    if (!fs.existsSync(booksDir)) return;
    if (!fs.existsSync(staticBooksDir)) fs.mkdirSync(staticBooksDir, { recursive: true });

    const books = fs.readdirSync(booksDir).filter(f => fs.statSync(path.join(booksDir, f)).isDirectory());

    for (const book of books) {
        const bookPath = path.join(booksDir, book);
        if (!fs.existsSync(path.join(bookPath, 'book.json')) && !fs.existsSync(path.join(bookPath, 'SUMMARY.md'))) continue;

        console.log(`--- 构建书籍: ${book} ---`);
        const outputPath = path.join(staticBooksDir, book);
        
        if (fs.existsSync(outputPath)) fs.rmSync(outputPath, { recursive: true, force: true });
        
        try {
            execSync(`npx honkit build "${bookPath}" "${outputPath}"`, { stdio: 'inherit' });
        } catch (err) {
            console.error(`❌ 构建书籍 ${book} 失败`);
        }
    }
}

// 如果直接运行该脚本则执行构建
if (require.main === module) {
    buildBooks();
}

module.exports = buildBooks;