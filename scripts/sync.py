#!/usr/bin/env python3
import argparse
import os
import re
import shutil
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

EXCLUDE_DIRS = {".obsidian", "secret", "images", "_frontmatter_backup"}
IMG_LINK_RE = re.compile(r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)')
H1_RE = re.compile(r'^#\s+(.+?)\s*$', re.MULTILINE)


def iter_md_files(vault: Path):
    for item in sorted(vault.iterdir(), key=lambda p: p.name):
        if not item.is_dir():
            continue
        if item.name in EXCLUDE_DIRS:
            continue
        for root, dirs, files in os.walk(item):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for filename in sorted(files):
                if filename.endswith(".md"):
                    full_path = Path(root) / filename
                    yield full_path, item.name


def parse_front_matter(text: str) -> Tuple[Dict[str, object], str]:
    if not text.startswith("---"):
        return {}, text

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text

    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            front_matter_text = "\n".join(lines[1:index])
            body = "\n".join(lines[index + 1 :])
            data = yaml.safe_load(front_matter_text) or {}
            normalized_data = {}
            for key, value in data.items():
                normalized_data[str(key).lower()] = value
            return normalized_data, body

    return {}, text


def render_front_matter(data: Dict[str, object], body: str) -> str:
    front_matter = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    body = body.lstrip("\n")
    if body:
        return f"---\n{front_matter}---\n\n{body}"
    return f"---\n{front_matter}---\n"


def parse_date(value: object) -> Optional[datetime]:
    if isinstance(value, datetime):
        return value
    if isinstance(value, date) and not isinstance(value, datetime):
        return datetime.combine(value, datetime.min.time())
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        text = text.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(text)
        except ValueError:
            pass

    return None


def format_date(value: datetime) -> str:
    return value.strftime("%Y%m%d")


def collect_used_slugs(vault: Path) -> set:
    used = set()
    for full_path, _category in iter_md_files(vault):
        text = full_path.read_text(encoding="utf-8")
        data, _body = parse_front_matter(text)
        slug = data.get("slug")
        if slug:
            used.add(str(slug))
    return used


def alloc_slug(date_value: datetime, used_slugs: set) -> str:
    base = format_date(date_value)
    index = 1
    while True:
        candidate = f"{base}-{index:02d}"
        if candidate not in used_slugs:
            used_slugs.add(candidate)
            return candidate
        index += 1


def resolve_image(md_path: Path, link: str, vault: Path) -> Optional[Path]:
    if link.startswith(("http://", "https://")):
        return None

    candidate = (md_path.parent / link).resolve()
    if candidate.exists():
        return candidate

    candidate = (vault / link.lstrip("/")).resolve()
    if candidate.exists():
        return candidate

    return None


def needs_rebuild(src_mtime: float, image_paths: List[Optional[Path]], dest_md: Path) -> bool:
    if not dest_md.exists():
        return True

    dest_mtime = dest_md.stat().st_mtime
    if src_mtime > dest_mtime:
        return True

    for image_path in image_paths:
        if image_path is not None and image_path.exists() and image_path.stat().st_mtime > dest_mtime:
            return True

    return False


def normalize_date_value(value: object) -> str:
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, date) and not isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")
    if value is None:
        return ""
    return str(value)


def sync_one(md_path: Path, category: str, vault: Path, content_dir: Path, used_slugs: set) -> str:
    text = md_path.read_text(encoding="utf-8")
    data, body = parse_front_matter(text)

    if not data.get("date"):
        print(f"[跳过-缺 date] {md_path.relative_to(vault)}")
        return "skipped"

    title = data.get("title")
    if not title:
        match = H1_RE.search(body)
        title = match.group(1).strip() if match else md_path.stem
        print(f"[title 兜底: {title}] {md_path.relative_to(vault)}")

    slug = data.get("slug")
    if not slug:
        parsed_date = parse_date(data.get("date"))
        if not parsed_date:
            print(f"[跳过-date 解析失败] {md_path.relative_to(vault)}")
            return "skipped"

        slug = alloc_slug(parsed_date, used_slugs)
        data["slug"] = slug
        md_path.write_text(render_front_matter(data, body), encoding="utf-8")
        print(f"[新分配 slug={slug}] {md_path.relative_to(vault)}")

    dest_dir = content_dir / str(slug)
    dest_md = dest_dir / "index.md"

    links = []
    for match in IMG_LINK_RE.finditer(body):
        links.append({"alt": match.group(1), "link": match.group(2), "full_match": match.group(0)})

    image_paths = [resolve_image(md_path, entry["link"], vault) for entry in links]
    src_mtime = md_path.stat().st_mtime

    if not needs_rebuild(src_mtime, image_paths, dest_md):
        return "unchanged"

    dest_dir.mkdir(parents=True, exist_ok=True)

    new_body = body
    for entry, image_path in zip(links, image_paths):
        if not image_path:
            print(f"  [警告] 图片未找到，保留原链接: {entry['link']}")
            continue

        dest_img = dest_dir / image_path.name
        if not dest_img.exists() or image_path.stat().st_mtime > dest_img.stat().st_mtime:
            shutil.copy2(image_path, dest_img)

        new_body = new_body.replace(entry["full_match"], f"![{entry['alt']}]({image_path.name})")

    new_post_data = {
        "title": title,
        "date": normalize_date_value(data.get("date")),
        "lastmod": datetime.fromtimestamp(src_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "slug": slug,
        "categories": [category],
        "tags": data.get("tags") or [],
        "draft": bool(data.get("draft", False)),
    }

    dest_md.write_text(render_front_matter(new_post_data, new_body), encoding="utf-8")
    return "updated"


def main() -> None:
    parser = argparse.ArgumentParser(description="将 Obsidian vault 中的 markdown 同步到 Hugo content 目录")
    parser.add_argument("vault")
    parser.add_argument("content_dir")
    args = parser.parse_args()

    vault = Path(args.vault).resolve()
    content_dir = Path(args.content_dir).resolve()
    content_dir.mkdir(parents=True, exist_ok=True)

    used_slugs = collect_used_slugs(vault)
    stats = {"updated": 0, "unchanged": 0, "skipped": 0}

    for full_path, category in iter_md_files(vault):
        result = sync_one(full_path, category, vault, content_dir, used_slugs)
        stats[result] += 1

    print(f"\n完成：更新 {stats['updated']}，未变化跳过 {stats['unchanged']}，缺字段跳过 {stats['skipped']}")


if __name__ == "__main__":
    main()
