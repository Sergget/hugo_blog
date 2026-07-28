const fs = require('fs-extra');
const path = require('path');
const matter = require('gray-matter');

const EXCLUDE_DIRS = new Set([".obsidian", "secret", "images", "_frontmatter_backup"]);
const IMG_LINK_RE = /!\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)/g;
const H1_RE = /^#\s+(.+?)\s*$/m;

function* iterMdFiles(vault) {
    const items = fs.readdirSync(vault, { withFileTypes: true });
    for (const item of items) {
        if (item.isDirectory()) {
            if (EXCLUDE_DIRS.has(item.name)) continue;
            const subDir = path.join(vault, item.name);
            const subFiles = fs.readdirSync(subDir, { recursive: true, withFileTypes: true });
            for (const subItem of subFiles) {
                if (subItem.isFile() && subItem.name.endsWith('.md')) {
                    yield {
                        fullPath: path.join(subDir, subItem.path || '', subItem.name),
                        category: item.name
                    };
                }
            }
        }
    }
}

function parseDate(value) {
    if (value instanceof Date) return value;
    const d = new Date(value);
    if (!isNaN(d.getTime())) return d;
    return null;
}

function formatDate(d) {
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}${month}${day}`;
}

function collectUsedSlugs(vault) {
    const used = new Set();
    for (const { fullPath } of iterMdFiles(vault)) {
        const fileContent = fs.readFileSync(fullPath, 'utf-8');
        const { data } = matter(fileContent);
        if (data.slug) {
            used.add(data.slug);
        }
    }
    return used;
}

function allocSlug(date, usedSlugs) {
    const base = formatDate(date);
    let n = 1;
    while (true) {
        const candidate = `${base}-${String(n).padStart(2, '0')}`;
        if (!usedSlugs.has(candidate)) {
            usedSlugs.add(candidate);
            return candidate;
        }
        n++;
    }
}

function resolveImage(mdPath, link, vault) {
    if (link.startsWith('http://') || link.startsWith('https://')) return null;
    
    // 相对路径
    const candidate1 = path.resolve(path.dirname(mdPath), link);
    if (fs.existsSync(candidate1)) return candidate1;
    
    // Vault 根目录路径
    const candidate2 = path.resolve(vault, link.startsWith('/') ? link.slice(1) : link);
    if (fs.existsSync(candidate2)) return candidate2;
    
    return null;
}

function needsRebuild(srcMtime, imagePaths, destMd) {
    if (!fs.existsSync(destMd)) return true;
    const destMtime = fs.statSync(destMd).mtimeMs;
    if (srcMtime > destMtime) return true;
    for (const img of imagePaths) {
        if (img && fs.statSync(img).mtimeMs > destMtime) return true;
    }
    return false;
}

function syncOne(mdPath, category, vault, contentDir, usedSlugs) {
    const fileContent = fs.readFileSync(mdPath, 'utf-8');
    const parsed = matter(fileContent);
    const { data, content } = parsed;

    if (!data.date) {
        console.log(`[跳过-缺 date] ${path.relative(vault, mdPath)}`);
        return "skipped";
    }

    let title = data.title;
    if (!title) {
        const match = H1_RE.exec(content);
        title = match ? match[1].trim() : path.parse(mdPath).name;
        console.log(`[title 兜底: ${title}] ${path.relative(vault, mdPath)}`);
    }

    let slug = data.slug;
    if (!slug) {
        const d = parseDate(data.date);
        if (!d) {
            console.log(`[跳过-date 解析失败] ${path.relative(vault, mdPath)}`);
            return "skipped";
        }
        slug = allocSlug(d, usedSlugs);
        data.slug = slug;
        // 写回原文件
        fs.writeFileSync(mdPath, matter.stringify(content, data), 'utf-8');
        console.log(`[新分配 slug=${slug}] ${path.relative(vault, mdPath)}`);
    }

    const destDir = path.join(contentDir, slug);
    const destMd = path.join(destDir, 'index.md');

    const links = [];
    let match;
    while ((match = IMG_LINK_RE.exec(content)) !== null) {
        links.push({ alt: match[1], link: match[2], fullMatch: match[0] });
    }
    
    const imagePaths = links.map(l => resolveImage(mdPath, l.link, vault));
    const srcMtime = fs.statSync(mdPath).mtimeMs;

    if (!needsRebuild(srcMtime, imagePaths, destMd)) {
        return "unchanged";
    }

    fs.ensureDirSync(destDir);

    let newBody = content;
    links.forEach((linkObj, index) => {
        const imgPath = imagePaths[index];
        if (!imgPath) {
            console.log(`  [警告] 图片未找到，保留原链接: ${linkObj.link}`);
            return;
        }
        const imgName = path.basename(imgPath);
        const destImg = path.join(destDir, imgName);
        
        if (!fs.existsSync(destImg) || fs.statSync(imgPath).mtimeMs > fs.statSync(destImg).mtimeMs) {
            fs.copySync(imgPath, destImg);
        }
        newBody = newBody.replace(linkObj.fullMatch, `![${linkObj.alt}](${imgName})`);
    });

    const newPostData = {
        title: title,
        date: data.date,
        lastmod: new Date(srcMtime),
        slug: slug,
        categories: [category],
        tags: data.tags || [],
        draft: data.draft || false
    };

    fs.writeFileSync(destMd, matter.stringify(newBody, newPostData), 'utf-8');
    return "updated";
}

function main() {
    const args = process.argv.slice(2);
    if (args.length < 2) {
        console.log("用法: node sync-to-hugo.js /path/to/vault /path/to/hugo/content/posts");
        process.exit(1);
    }

    const vault = path.resolve(args[0]);
    const contentDir = path.resolve(args[1]);
    fs.ensureDirSync(contentDir);

    const usedSlugs = collectUsedSlugs(vault);
    const stats = { updated: 0, unchanged: 0, skipped: 0 };

    for (const { fullPath, category } of iterMdFiles(vault)) {
        const result = syncOne(fullPath, category, vault, contentDir, usedSlugs);
        stats[result]++;
    }

    console.log(`\n完成：更新 ${stats.updated}，未变化跳过 ${stats.unchanged}，缺字段跳过 ${stats.skipped}`);
}

main();
