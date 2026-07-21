#!/usr/bin/env python3
"""
日常同步脚本：把 Obsidian vault 中的文章 + 图片，同步为 Hugo 的 Page Bundle。

结构约定：
    <hugo_content_dir>/<slug>/index.md
    <hugo_content_dir>/<slug>/图片1.png
    <hugo_content_dir>/<slug>/图片2.png

行为：
- 遍历 vault 根目录下的分类目录（跳过 .obsidian / secret / images / _frontmatter_backup）
- 分类（categories）= 文章所在的一级目录名，自动生成，不需要在 Obsidian 里手填
- slug：
    - 如果文章 frontmatter 里已经有 slug（比如跑过 normalize_frontmatter.py），直接用
    - 如果没有（新文章），按 date 自动分配一个 "YYYYMMDD-NN" 的 slug，
      并且写回 Obsidian 源文件的 frontmatter，以后就固定不变了
- 图片：扫描正文里的 Markdown 图片链接 ![alt](相对路径)，解析出 vault 内的真实文件，
  复制到对应的 slug 文件夹下，并把正文里的链接改写成同目录下的文件名（Hugo Page Bundle 里直接用文件名引用即可）
- 增量同步：只有当源 md 或引用的图片比目标新时才重新生成，没有变化的文章会跳过，加快日常同步速度

依赖：
    pip install python-frontmatter

用法：
    python sync_to_hugo.py /path/to/vault /path/to/hugo/content/posts

建议：写完/改完文章后手动跑一下，或者用 cron / 计划任务定时跑（比如每 10 分钟一次），
跑完再 `hugo` 构建 + 部署。
"""
import re
import sys
import shutil
from pathlib import Path
from datetime import date, datetime

import frontmatter

EXCLUDE_DIRS = {".obsidian", "secret", "images", "_frontmatter_backup"}
IMG_LINK_RE = re.compile(r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)')


def iter_md_files(vault: Path):
    for p in vault.rglob("*.md"):
        rel = p.relative_to(vault)
        if rel.parts and rel.parts[0] in EXCLUDE_DIRS:
            continue
        yield p, rel.parts[0]  # (路径, 一级目录名 = 分类)


def parse_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return datetime.strptime(str(value).strip(), "%Y-%m-%d").date()


def collect_used_slugs(vault: Path):
    used = set()
    for md_path, _ in iter_md_files(vault):
        post = frontmatter.load(md_path)
        s = post.metadata.get("slug")
        if s:
            used.add(s)
    return used


def alloc_slug(d: date, used_slugs: set):
    base = d.strftime("%Y%m%d")
    n = 1
    while True:
        candidate = f"{base}-{n:02d}"
        if candidate not in used_slugs:
            used_slugs.add(candidate)
            return candidate
        n += 1


def resolve_image(md_path: Path, link: str, vault: Path):
    """把正文里的相对图片链接解析成 vault 内的真实文件路径。"""
    if link.startswith(("http://", "https://")):
        return None
    candidate = (md_path.parent / link).resolve()
    if candidate.exists():
        return candidate
    candidate2 = (vault / link.lstrip("/")).resolve()
    if candidate2.exists():
        return candidate2
    return None


def needs_rebuild(src_mtime: float, image_paths, dest_md: Path):
    if not dest_md.exists():
        return True
    dest_mtime = dest_md.stat().st_mtime
    if src_mtime > dest_mtime:
        return True
    for img in image_paths:
        if img and img.stat().st_mtime > dest_mtime:
            return True
    return False


def sync_one(md_path: Path, category: str, vault: Path, content_dir: Path, used_slugs: set):
    post = frontmatter.load(md_path)

    if "title" not in post.metadata or "date" not in post.metadata:
        print(f"[跳过-缺 title/date] {md_path.relative_to(vault)}")
        return "skipped"

    slug = post.metadata.get("slug")
    if not slug:
        try:
            d = parse_date(post.metadata["date"])
        except Exception as e:
            print(f"[跳过-date 解析失败: {e}] {md_path.relative_to(vault)}")
            return "skipped"
        slug = alloc_slug(d, used_slugs)
        post.metadata["slug"] = slug
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(post, allow_unicode=True))
        print(f"[新分配 slug={slug}] {md_path.relative_to(vault)}")

    dest_dir = content_dir / slug
    dest_md = dest_dir / "index.md"

    links = IMG_LINK_RE.findall(post.content)
    image_paths = [resolve_image(md_path, link, vault) for _, link in links]

    src_mtime = md_path.stat().st_mtime
    if not needs_rebuild(src_mtime, image_paths, dest_md):
        return "unchanged"

    dest_dir.mkdir(parents=True, exist_ok=True)

    new_body = post.content
    for (alt, link), img_path in zip(links, image_paths):
        if img_path is None:
            print(f"  [警告] 图片未找到，保留原链接: {link}")
            continue
        dest_img = dest_dir / img_path.name
        if (not dest_img.exists()) or img_path.stat().st_mtime > dest_img.stat().st_mtime:
            shutil.copy2(img_path, dest_img)
        new_body = new_body.replace(f"![{alt}]({link})", f"![{alt}]({img_path.name})")

    new_post = frontmatter.Post(new_body)
    new_post.metadata = {
        "title": post.metadata.get("title"),
        "date": post.metadata.get("date"),
        "slug": slug,
        "categories": [category],
        "tags": post.metadata.get("tags") or [],
        "draft": post.metadata.get("draft", False),
    }

    with open(dest_md, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(new_post, allow_unicode=True))

    return "updated"


def main():
    if len(sys.argv) < 3:
        print("用法: python sync_to_hugo.py /path/to/vault /path/to/hugo/content/posts")
        sys.exit(1)

    vault = Path(sys.argv[1]).resolve()
    content_dir = Path(sys.argv[2]).resolve()
    content_dir.mkdir(parents=True, exist_ok=True)

    used_slugs = collect_used_slugs(vault)

    stats = {"updated": 0, "unchanged": 0, "skipped": 0}
    for md_path, category in iter_md_files(vault):
        result = sync_one(md_path, category, vault, content_dir, used_slugs)
        stats[result] += 1

    print(f"\n完成：更新 {stats['updated']}，未变化跳过 {stats['unchanged']}，缺字段跳过 {stats['skipped']}")


if __name__ == "__main__":
    main()
