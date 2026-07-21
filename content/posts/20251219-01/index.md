---
categories:
- 会用电脑
date: 2025-12-19
draft: false
slug: 20251219-01
tags: []
title: WordPress大图、HEIC上传故障排查
---

> 适用环境：
> 
> - Ubuntu Server 22.04
> 
> - 自建 LNMP（Nginx + PHP-FPM + MySQL）
> 
> - WordPress（后台上传 / WP-CLI 上传）
> 
> - 图片来源：iPhone（HEIC / Live Photo / 高分辨率 JPEG 4000×3000+）
> 
> - 服务器物理内存：4GB

## 一、问题背景

- 后台上传高分辨率图片（4032×3024 及以上）持续报错：服务器无法处理图片。如果服务器繁忙或没有足够的资源来完成任务，就会发生这种情况。建议的最大尺寸为 2560 像素。

- HEIC 图片、MOV 视频上传失败或上传后：
    - 媒体库无缩略图
    
    - 插入文章/页面不显示

- PHP / Nginx / WordPress 日志无明显错误输出

## 二、排查与尝试过的操作（事实记录）

### 1\. PHP 层

- 修改 PHP 配置：`memory_limit = -1 max_execution_time = 0`

- 结论：
    - **无效**
    
    - WordPress 图像处理失败并非 PHP 限制，而是 ImageMagick / Imagick 资源策略

### 2\. WordPress 调试

- 启用调试：`define('WP_DEBUG', true); define('WP_DEBUG_LOG', true); define('WP_DEBUG_DISPLAY', false);`

- 现象：
    - `wp-content/debug.log` 未生成
    
    - 上传失败时无 PHP / Nginx 错误日志

- 结论：
    - 图像处理失败发生在底层库（Imagick），并未抛出 PHP 致命错误

### 3\. ImageMagick / Imagick

#### 3.1 系统默认版本（失败）

- Ubuntu 22.04 apt 安装版本：
    - ImageMagick 6.9.x
    
    - php-imagick 3.6.x

- 问题：
    - HEIC 支持不稳定
    
    - 高分辨率图片裁剪 / 生成缩略图失败

#### 3.2 编译安装 ImageMagick 7（尝试）

- 手动编译安装 ImageMagick 7.1.x

- 安装 libheif-dev 以支持 HEIC

- 通过 pecl 安装 imagick（指向 IM7）

- WordPress 站点健康显示：
    - Imagick 可用
    
    - 资源限制显示为几十 GB（虚高）

- 实际结果：
    - **问题仍然存在**
    
    - HEIC 报错：`Too many auxiliary image references`

- 结论：
    - IM7 + HDRI + HEIC 在 **4GB 内存服务器** 上不稳定
    
    - WordPress 对 HEIC 的支持并不成熟

### 4\. ImageMagick policy.xml 调整（失败）

- 调整内容：`<policy domain="resource" name="memory" value="256MiB"/> <policy domain="resource" name="map" value="512MiB"/> <policy domain="resource" name="width" value="16KP"/> <policy domain="resource" name="height" value="16KP"/> <policy domain="resource" name="area" value="128MP"/> <policy domain="resource" name="disk" value="1GiB"/>`

- 结论：
    - 仅能解决 **部分尺寸 JPEG**
    
    - 无法根本解决 HEIC / 超大图上传失败

### 5\. WordPress 层自定义代码（风险点）

- 禁用大图裁剪（`big_image_size_threshold`）

- 使用 mu-plugin / functions.php 强行放宽限制

- 后果：
    - 媒体库无缩略图
    
    - 插入内容失败

- 结论：
    - **不建议禁用 WordPress 默认大图裁剪**

### 6\. WP-CLI 批量上传（部分成功）

- 问题：
    - 未指定 `--path` → 报错不是 WordPress 安装
    
    - 权限不一致 → 无法移动文件
    
    - HEIC 仍然无法稳定生成元数据

- 结论：
    - WP-CLI **不能绕过 WordPress 的图像处理限制**

### 7\. Imagick 卸载与还原

- pecl 卸载：`sudo pecl uninstall imagick`

- 现象：
    - 卸载成功
    
    - PHP 启动报错（残留配置）：`Unable to load dynamic library 'imagick.so'`

- 原因：
    - php.ini / mods-available 中仍有 `extension=imagick.so`

## 三、最终结论（经验总结）

### ✅ 关键结论

1. **WordPress 对 HEIC 的支持不可靠**（尤其是 Live Photo / HDR）

2. **4GB 内存服务器不适合在线处理超大图 + HEIC**

3. ImageMagick 7 并不能从根本解决 WordPress 媒体处理问题

4. 禁用大图裁剪会直接破坏媒体库显示

## 四、推荐的稳定方案（最终方案）

### ✅ 推荐方案：上传后自动转小尺寸 JPEG（插件）

#### 插件 1：Resize Image After Upload（推荐）

- 功能：
    - 上传后自动调整图片尺寸
    
    - 可设置最大长边（如 2560px）
    
    - 输出 JPEG

- 优点：
    - 不依赖 HEIC 原生支持
    
    - 使用 WordPress 官方图像流程
    
    - 稳定、低风险

#### 插件 2：ImageMagick Engine（可选）

- 作用：
    - 指定使用 Imagick
    
    - 配合 Resize Image After Upload 使用

### 🚫 不推荐方案

- 后台直接上传 HEIC / Live Photo

- 禁用 WordPress 默认大图裁剪

- 在低内存服务器上强行启用 HDRI Imagick

## 五、服务器还原清单（可操作）

### 1️⃣ Imagick 清理

```
grep -R "imagick.so" /etc/php/
# 注释或删除 extension=imagick.so
sudo rm -f /usr/lib/php/*/imagick.so
sudo systemctl restart php-fpm
```

### 2️⃣ 恢复 PHP 配置

```
memory_limit = 256M
max_execution_time = 30
```

### 3️⃣ 恢复 WordPress 默认行为

- 删除 mu-plugin

- 删除禁用大图裁剪的代码

## 六、一句话经验

> **WordPress + 小内存服务器的正确姿势：**  
> **让图片在进入媒体库之前或上传后尽早变小，  
> 而不是试图让服务器“强行处理原图”。**