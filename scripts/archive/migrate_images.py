import shutil
from pathlib import Path

# 定义路径
BASE_DIR = Path("content/diary")
IMAGES_SRC = BASE_DIR / "images"
POSTS_DIR = BASE_DIR / "posts"

def migrate_images():
    # 查找所有图片，假设图片按年份/月份存储
    # 例如: content/diary/images/2025/11/微信图片_...jpg
    # 将其匹配到 2025-11 的文件夹中
    
    for year_dir in IMAGES_SRC.glob("*"):
        if not year_dir.is_dir(): continue
        
        for month_dir in year_dir.glob("*"):
            if not month_dir.is_dir(): continue
            
            # 目标日期字符串部分 (例如: 2025-11)
            date_prefix = f"{year_dir.name}-{month_dir.name}"
            
            # 查找所有以该日期为前缀的 post 目录
            target_posts = list(POSTS_DIR.glob(f"{date_prefix}-*"))
            
            for img in month_dir.glob("*"):
                # 如果有多个帖子在同一个月，这里简化处理：
                # 默认拷贝到该月第一个帖子中，或者根据文件名关联
                # 实际场景通常需要更复杂的逻辑
                if target_posts:
                    dest = target_posts[0] / img.name
                    shutil.copy2(img, dest)
                    print(f"Copied: {img} -> {dest}")

if __name__ == "__main__":
    migrate_images()
