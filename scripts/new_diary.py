import datetime
import os
from pathlib import Path

# 配置路径
POSTS_DIR = Path("content/diary/")

def create_diary_template():
    # 获取今天日期
    today = datetime.date.today().strftime("%Y-%m-%d")
    title = datetime.date.today().strftime("%Y年%m月%d日")
    
    # 创建文件夹
    post_dir = POSTS_DIR / today
    if post_dir.exists():
        print(f"警告: 目录 {post_dir} 已经存在！")
        return
    
    post_dir.mkdir(parents=True)
    
    # 创建 index.md 模板
    content = f"""---
title: "{title} - "
date: {today}
tags: ["日记"]
---

"""
    
    index_file = post_dir / "index.md"
    index_file.write_text(content, encoding='utf-8')
    
    print(f"成功创建日记模板: {index_file}")

if __name__ == "__main__":
    create_diary_template()
