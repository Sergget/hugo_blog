import os
import shutil
import re
from pathlib import Path

# 定义路径
BASE_DIR = Path("content/diary")
POSTS_DIR = BASE_DIR / "posts"

def fix_images():
    # 遍历所有日记文件夹
    for post_dir in POSTS_DIR.iterdir():
        if not post_dir.is_dir(): continue
        
        index_file = post_dir / "index.md"
        if not index_file.exists(): continue
        
        content = index_file.read_text(encoding='utf-8')
        
        # 查找所有图片引用: ![](path/to/image.jpg)
        # 提取文件名
        pattern = re.compile(r'!\[.*?\]\((.*?)\)')
        
        new_content = content
        for match in pattern.finditer(content):
            old_link = match.group(1)
            
            # 如果链接包含路径，提取文件名
            filename = os.path.basename(old_link)
            
            # 尝试在所有 posts 目录中查找该文件
            found = False
            for img_src in POSTS_DIR.rglob(filename):
                if img_src.parent != post_dir:
                    # 移动图片到当前 index.md 所在目录
                    dest = post_dir / filename
                    if not dest.exists():
                        shutil.copy2(img_src, dest)
                    found = True
            
            if found:
                # 替换 Markdown 中的链接为相对路径
                new_content = new_content.replace(f"({old_link})", f"({filename})")
        
        if new_content != content:
            index_file.write_text(new_content, encoding='utf-8')
            print(f"Fixed: {index_file}")

if __name__ == "__main__":
    fix_images()