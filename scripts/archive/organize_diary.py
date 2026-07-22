import os
import shutil
import re
from pathlib import Path

# 定义路径
BASE_DIR = Path("content/diary")
ENTRIES_DIR = BASE_DIR / "entries"
IMAGES_DIR = BASE_DIR / "images"
TARGET_DIR = BASE_DIR / "posts"

def organize():
    if not TARGET_DIR.exists():
        TARGET_DIR.mkdir(parents=True)

    # 遍历所有日记文件
    for entry in ENTRIES_DIR.glob("*.md"):
        filename = entry.stem
        # 提取日期 (例如: diary-2025-08-05 -> 2025-08-05)
        date_part = filename.replace("diary-", "")
        
        # 创建目录: content/diary/posts/2025-08-05/
        post_dir = TARGET_DIR / date_part
        post_dir.mkdir(parents=True, exist_ok=True)
        
        # 移动文件为 index.md
        shutil.move(str(entry), str(post_dir / "index.md"))
        print(f"Processed: {filename} -> {post_dir}/index.md")

if __name__ == "__main__":
    organize()
