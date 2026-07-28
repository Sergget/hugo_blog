const { spawn, execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

async function run() {
    const args = process.argv.slice(2);
    const skipBooks = args.includes('--skip-books');

    // 1. 检查导航数据
    console.log('--- 检查导航数据 ---');
    try {
        execSync('node ./scripts/check-books-index.js', { stdio: 'inherit' });
    } catch (err) {
        console.error('检查导航数据失败');
        process.exit(1);
    }

    // 2. 构建 HonKit 书籍
    if (skipBooks) {
        console.log('--- 跳过构建 HonKit 书籍 ---');
    } else {
        console.log('--- 构建 HonKit 书籍 ---');
        // 修改：指向 content/books
        const booksDir = path.join(__dirname, '../books');
        // 修改：输出到 static/resources
        const staticBooksDir = path.join(__dirname, '../static/resources');

        if (fs.existsSync(booksDir)) {
            // 确保 static/resources 目录存在
            if (!fs.existsSync(staticBooksDir)) {
                fs.mkdirSync(staticBooksDir, { recursive: true });
            }

            const books = fs.readdirSync(booksDir, { withFileTypes: true })
                .filter(dirent => dirent.isDirectory())
                .map(dirent => dirent.name);

            for (const book of books) {
                // 排除非书籍目录（例如可能的 _index.md 所在文件夹或其他非 honkit 目录）
                const bookPath = path.join(booksDir, book);
                if (!fs.existsSync(path.join(bookPath, 'book.json')) && !fs.existsSync(path.join(bookPath, 'SUMMARY.md'))) {
                    continue;
                }

                console.log(`构建书籍: ${book}`);
                const outputPath = path.join(staticBooksDir, book);
                
                try {
                    // 构建前清除旧的输出目录
                    if (fs.existsSync(outputPath)) {
                        fs.rmSync(outputPath, { recursive: true, force: true });
                    }
                    // 使用 npx honkit build
                    execSync(`npx honkit build "${bookPath}" "${outputPath}"`, { stdio: 'inherit' });
                } catch (err) {
                    console.error(`构建书籍 ${book} 失败`);
                }
            }
        }
    }

    // 3. 启动 Hugo 本地服务器
    console.log('--- 启动 Hugo 本地服务器 ---');
    const hugo = spawn('hugo', ['server', '-D', '-F'], { stdio: 'inherit', shell: true });

    hugo.on('close', (code) => {
        console.log(`Hugo server 退出，退出码: ${code}`);
    });
}

run();
