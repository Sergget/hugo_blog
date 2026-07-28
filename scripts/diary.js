const fs = require('fs-extra');
const path = require('path');

const POSTS_DIR = path.join(__dirname, '../content/diary');

function createDiaryTemplate() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    
    const today = `${year}-${month}-${day}`;
    const title = `${year}年${month}月${day}日`;
    
    const postDir = path.join(POSTS_DIR, today);
    
    if (fs.existsSync(postDir)) {
        console.warn(`警告: 目录 ${postDir} 已经存在！`);
        return;
    }
    
    fs.ensureDirSync(postDir);
    
    const content = `---
title: "${title} - "
date: ${today}
tags: ["日记"]
---

`;
    
    const indexFile = path.join(postDir, 'index.md');
    fs.writeFileSync(indexFile, content, 'utf-8');
    
    console.log(`成功创建日记模板: ${indexFile}`);
}

createDiaryTemplate();
