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
        const booksDir = path.join(__dirname, '../books');
        if (fs.existsSync(booksDir)) {
            const books = fs.readdirSync(booksDir, { withFileTypes: true })
                .filter(dirent => dirent.isDirectory())
                .map(dirent => dirent.name);

            for (const book of books) {
                console.log(`构建书籍: ${book}`);
                const bookPath = path.join(booksDir, book);
                const outputPath = path.join(__dirname, `../static/books/${book}`);
                
                try {
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
