---
categories:
- 来点码吧
date: 2026-07-03
draft: false
slug: 20260703-01
tags: []
title: WordPress导航栏添加带 Iconify 图标的常用服务下拉菜单
---

## 背景

自建了 RDP 远程桌面、Immich 相册、Aria2 下载、SSH 面板等一批常用服务的入口，想在博客导航栏里加一个下拉菜单集中收纳，点开就能跳转，并且每一项都带上对应的图标（图标来自 [iconify.design](https://iconify.design/)）。

站点主题是 **Blogsy**（Peregrine Themes 出品），确认下来是**经典/混合主题**：内容用 Gutenberg 编辑，但整站结构（导航菜单、头部/尾部）走的是外观 → 自定义（Customizer）和外观 → 菜单，不是 FSE 站点编辑器。因此方案完全基于 WordPress 原生的「菜单」组件，不需要额外装插件（除了一个可选的头部代码插件）。
## 思路

1. 全站加载 Iconify 的 Web Component 脚本，让 `<iconify-icon>` 标签能正常渲染成图标
2. 在「外观 → 菜单」里建一个带子菜单的导航项，子菜单每一项的「导航标签」里直接写入 `<iconify-icon>` + 文字的 HTML（WordPress 菜单标签字段允许写入 HTML，不会被转义）
3. 用一段 CSS，让图标和文字在下拉菜单里对齐、间距合理

## 一、加载 Iconify 脚本

装一个免费插件 **WPCode**（或 Insert Headers and Footers），在"代码片段 → 头部"粘贴：

```html
<script src="https://code.iconify.design/iconify-icon/2.1.0/iconify-icon.min.js"></script>
```

如果 Blogsy 主题设置里自带「自定义代码 / Header Scripts」选项，也可以直接填在那里，省得装插件。

## 二、建立菜单结构

外观 → 菜单：

1. 添加一个「自定义链接」，URL 填 `#`，链接文字填 **"常用服务"**，作为呼出下拉菜单的顶级按钮
2. 依次添加若干个「自定义链接」，URL 填各服务地址，**链接文字直接粘贴带图标的 HTML**，例如：

```html
<iconify-icon icon="devicon:windows11"></iconify-icon> RDP 远程桌面
```

```html
<iconify-icon icon="selfhst:immich"></iconify-icon> Immich 相册
```

```html
<iconify-icon icon="mdi:download-circle" style="color:#f59e0b"></iconify-icon> Aria2 下载
```

```html
<iconify-icon icon="famicons:terminal"></iconify-icon> SSH homeserver
```

```html
<iconify-icon icon="devicon:linux"></iconify-icon> Linux 学习
```

3. 把这几个自定义链接**向右拖动缩进**到"常用服务"下面一级（WordPress 菜单编辑器里拖动即可产生父子关系），保存菜单

保存后前台会出现一个"常用服务"顶级菜单项，悬停/点击会弹出下拉子菜单，每一项都带图标。

## 三、CSS 美化（关键坑点）

**踩坑记录**：Blogsy 实际渲染出的下拉菜单结构，是把图标和文字**包在同一个 `<span>`** 里：

```html
<li class="menu-item ...">
  <a href="...">
    <span><iconify-icon icon="...">...</iconify-icon> RDP 远程桌面</span>
  </a>
</li>
```

不是"图标、文字各自独立"的结构。所以 flex 布局必须加在这个内层 `<span>` 上，而不是 `<a>` 标签本身，否则样式不会生效。

外观 → 自定义 → 附加CSS，加入：

```css
/* 子菜单容器宽度 */
.menu-item-has-children .sub-menu {
  min-width: 240px;
}

/* 每一行链接的内边距 */
.sub-menu .menu-item > a {
  padding: 10px 16px !important;
}

/* 关键：图标+文字都在这个 span 里，flex 要加在这里 */
.sub-menu .menu-item > a > span {
  display: inline-flex !important;
  align-items: center;
  gap: 10px;
}

/* 图标本身的大小和对齐 */
.sub-menu iconify-icon {
  font-size: 20px;
  display: inline-flex;
  vertical-align: middle;
  flex-shrink: 0;
}
```

## 小结

- 图标直接调用 iconify.design 的在线图标库，去 [https://icon-sets.iconify.design/](https://icon-sets.iconify.design/) 搜索关键词即可换用其他图标，写法是 `icon="集合前缀:图标名"`
- 核心坑点：Blogsy 主题把图标和文字包在同一个 `<span>` 里渲染，CSS 的 flex 布局必须作用在这个内层 `<span>` 上