// scripts/dev.js
const { spawn, execSync } = require('child_process');
const buildBooks = require('./build-books');

async function run() {
    const args = process.argv.slice(2);
    
    // 1. 构建书籍
    if (!args.includes('--skip-books')) {
        console.log('--- 开始初始化书籍构建 ---');
        try {
            execSync('node ./scripts/check-books-index.js', { stdio: 'inherit' });
            buildBooks();
        } catch (err) {
            console.error('构建过程出错');
            process.exit(1);
        }
    }

    // 2. 启动 Hugo
    console.log('--- 启动 Hugo ---');
    spawn('hugo', ['server', '-D', '-F'], { stdio: 'inherit', shell: true });
}

run();