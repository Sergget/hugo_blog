#!/usr/bin/env python3
"""
一次性脚本：规范化 Obsidian vault 中所有已有文章的 frontmatter。

只需要跑一次，用来把历史文章的 frontmatter 从：
    ---
    title: xxx
    date: 2020-04-18
    categories:
    - 来点码吧
    ---
统一成新格式：
    ---
    title: xxx
    date: 2020-04-18
    slug: 20200418-01
    tags: []
    draft: false
    ---

要点：
- categories 字段被去掉。以后分类完全由文章所在的一级目录名决定，
  发布时由 sync_to_hugo.py 自动推导，不需要在 Obsidian 里手填。
- slug 规则：按 date 分组，组内按文件相对路径排序（保证多次运行结果一致），
  生成 20200418-01 / 20200418-02 这样的序号。
- 修改前会把原文件备份到 vault 根目录下的 _frontmatter_backup/，
  目录结构和原 vault 保持一致，出问题可以直接对比/还原。
- 以后新写的文章不需要再跑这个脚本——slug 由 sync_to_hugo.py
  在第一次同步时自动分配并写回 Obsidian 源文件。这个脚本只用来处理存量文章。

依赖：
    pip install python-frontmatter

用法：
    python normalize_frontmatter.py /path/to/vault           # 实际执行
    python normalize_frontmatter.py /path/to/vault --dry-run # 只打印，不修改文件
"""
import sys
import shutil
from pathlib import Path
from datetime import date, datetime
from collections import defaultdict

import frontmatter

EXCLUDE_DIRS = {".obsidian", "secret", "images", "_frontmatter_backup"}


def iter_md_files(vault: Path):
    for p in vault.rglob("*.md"):
        rel = p.relative_to(vault)
        if rel.parts and rel.parts[0] in EXCLUDE_DIRS:
            continue
        yield p


def parse_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return datetime.strptime(str(value).strip(), "%Y-%m-%d").date()


def main():
    if len(sys.argv) < 2:
        print("用法: python normalize_frontmatter.py /path/to/vault [--dry-run]")
        sys.exit(1)

    vault = Path(sys.argv[1]).resolve()
    dry_run = "--dry-run" in sys.argv

    posts = []
    for path in iter_md_files(vault):
        post = frontmatter.load(path)
        if "date" not in post.metadata or "title" not in post.metadata:
            print(f"[跳过-缺 title/date] {path.relative_to(vault)}")
            continue
        try:
            d = parse_date(post.metadata["date"])
        except Exception as e:
            print(f"[跳过-date 解析失败: {e}] {path.relative_to(vault)}")
            continue
        posts.append((path, post, d))

    # 按 (date, 相对路径) 排序，保证同一批 slug 分配可复现
    posts.sort(key=lambda item: (item[2], str(item[0].relative_to(vault))))
    seq_by_date = defaultdict(int)
    backup_dir = vault / "_frontmatter_backup"

    for path, post, d in posts:
        seq_by_date[d] += 1
        slug = f"{d.strftime('%Y%m%d')}-{seq_by_date[d]:02d}"

        old_meta = dict(post.metadata)
        new_meta = {
            "title": old_meta.get("title"),
            "date": d,
            "slug": slug,
            "tags": old_meta.get("tags") or [],
            "draft": old_meta.get("draft", False),
        }

        note = f"  (原 categories: {old_meta.get('categories')})" if "categories" in old_meta else ""
        print(f"{path.relative_to(vault)}  ->  slug={slug}{note}")

        if dry_run:
            continue

        backup_path = backup_dir / path.relative_to(vault)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        if not backup_path.exists():
            shutil.copy2(path, backup_path)

        post.metadata = new_meta
        with open(path, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(post, allow_unicode=True))

    print(f"\n共处理 {len(posts)} 篇文章。"
          + ("(dry-run，未实际写入)" if dry_run else " 原文件已备份至 _frontmatter_backup/"))


if __name__ == "__main__":
    main()
