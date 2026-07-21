---
categories:
- 会用电脑
date: 2025-12-18
draft: false
slug: 20251218-01
tags: []
title: Edge 浏览器 IE 模式按钮强制开启指南
---

### 问题描述

在 Windows 10 环境下，尽管已在系统功能中勾选 IE11 并在 Edge 设置中开启了“允许重新加载”，但 Edge 143+ 版本的“外观”设置中仍不显示 **IE 模式切换按钮**。

### 核心原理

通过修改注册表，下发 Microsoft Edge 的管理策略（Policy），强制浏览器激活 IE 整合功能。

* * *

### 自动化修复方案（脚本版）

您可以选择以下任意一种脚本运行，效果相同。请务必以**管理员身份**运行。

#### 选项 A：快捷批处理脚本 (.bat)

新建一个文本文档，粘贴以下内容，保存为 `FixEdgeIE.bat`，右键选择 **“以管理员身份运行”**。

```
@echo off
:: 强制开启 Edge IE 模式策略脚本
echo 正在写入注册表策略...

reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Edge" /v "InternetExplorerIntegrationLevel" /t REG_DWORD /d 1 /f
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Edge" /v "InternetExplorerIntegrationReloadInIEModeAllowed" /t REG_DWORD /d 1 /f

echo.
echo 注册表项已添加！请重启 Edge 浏览器。
pause
```

#### 选项 B：PowerShell 脚本 (.ps1)

右键点击开始菜单，选择 **“Windows PowerShell (管理员)”**，复制并执行以下命令：

```
# 定义注册表路径
$registryPath = "HKLM:\SOFTWARE\Policies\Microsoft\Edge"

# 如果路径不存在则创建
if (!(Test-Path $registryPath)) {
    New-Item -Path $registryPath -Force
}

# 写入策略值
Set-ItemProperty -Path $registryPath -Name "InternetExplorerIntegrationLevel" -Value 1
Set-ItemProperty -Path $registryPath -Name "InternetExplorerIntegrationReloadInIEModeAllowed" -Value 1

Write-Host "策略已生效，请重启 Edge 浏览器。" -ForegroundColor Green
```

* * *

### 脚本执行后的后续操作

1. **重启浏览器**：在 Edge 地址栏输入 `edge://policy` 并回车，点击 **“刷新策略”**，确保能看到上述两条策略显示为“正常”。

3. **显示按钮**：
    - 进入 **设置 -> 外观**。
    
    - 在“选择要在工具栏上显示的按钮”下方，**“Internet Explorer 模式按钮”** 开关现在应该已经出现并可以手动开启了。

5. **验证**：点击工具栏新出现的蓝色的 IE 图标，页面应能成功切换至兼容模式。

* * *

**需要注意：** 开启策略后，设置页面可能会显示“由你的组织管理”，这是正常现象，说明注册表策略已生效。