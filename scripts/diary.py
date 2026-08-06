#!/usr/bin/env python3
from datetime import datetime
from pathlib import Path

POSTS_DIR = Path(__file__).resolve().parent.parent / "content" / "diary"


def create_diary_template() -> None:
    now = datetime.now()
    year = now.year
    month = now.month
    day = now.day

    today = now.strftime("%Y-%m-%d")
    title = f"{year}年{month:02d}月{day:02d}日"

    post_dir = POSTS_DIR / today

    if post_dir.exists():
        print(f"警告: 目录 {post_dir} 已经存在！")
        return

    post_dir.mkdir(parents=True, exist_ok=True)

    content = f"""---
title: \"{title} - \"
date: {today}
tags: [\"日记\"]
---

"""

    index_file = post_dir / "index.md"
    index_file.write_text(content, encoding="utf-8")

    print(f"成功创建日记模板: {index_file}")


if __name__ == "__main__":
    create_diary_template()
