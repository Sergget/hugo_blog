---
categories:
- 会用电脑
date: 2026-01-19
draft: false
slug: 20260119-01
tags: []
title: Windows Terminal 完整美化指南
---

## 1.前置准备

### 系统要求

- Windows 10 1903 (build 18362) 或更高版本

- Windows 11（推荐）

- PowerShell 5.1 或更高版本

### 检查 PowerShell 版本

```
$PSVersionTable.PSVersion
```

* * *

## 2.安装 Windows Terminal

### 方法 1：Microsoft Store（推荐）

1. 打开 Microsoft Store

3. 搜索 "Windows Terminal"

5. 点击"安装"

### 方法 2：使用 winget

```
winget install Microsoft.WindowsTerminal
```

### 验证安装

打开 Windows Terminal，应该能看到终端界面。

## 3.配置执行策略

### 为什么需要这一步？

PowerShell 默认不允许运行脚本，需要修改执行策略。

### 操作步骤

1. **以管理员身份打开 PowerShell**
    - 在开始菜单搜索 "PowerShell"
    
    - 右键选择"以管理员身份运行"

3. **执行以下命令** `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

5. **确认更改**
    - 提示时输入 `Y` 并回车

7. **验证设置** `Get-ExecutionPolicy -List` 应该看到 `CurrentUser` 的策略为 `RemoteSigned`

* * *

## 4.安装 Oh My Posh

### 什么是 Oh My Posh？

一个强大的提示符主题引擎，让终端更美观、信息更丰富。

### 安装步骤

1. **使用 winget 安装（推荐）** `winget install JanDeDobbeleer.OhMyPosh -s winget`

3. **完全关闭并重新打开 PowerShell**
    - 必须重启才能生效
    
    - 关闭所有 PowerShell 和 Windows Terminal 窗口

5. **验证安装** `oh-my-posh version` 应该显示版本号，如 `29.0.2`

### 检查主题路径

```
# 检查环境变量
$env:POSH_THEMES_PATH

# 验证主题文件是否存在
Test-Path $env:POSH_THEMES_PATH
```

### 如果主题路径不存在（常见问题）

**手动下载主题文件：**

```
# 1. 创建主题目录
New-Item -ItemType Directory -Path "$env:LOCALAPPDATA\Programs\oh-my-posh\themes" -Force

# 2. 下载常用主题
$themes = @("paradox", "atomic", "agnoster", "jandedobbeleer", "powerlevel10k_rainbow", "night-owl", "clean-detailed")

foreach ($theme in $themes) {
    $url = "https://raw.githubusercontent.com/JanDeDobbeleer/oh-my-posh/main/themes/$theme.omp.json"
    $output = "$env:LOCALAPPDATA\Programs\oh-my-posh\themes\$theme.omp.json"
    try {
        Invoke-WebRequest -Uri $url -OutFile $output
        Write-Host "✓ 已下载: $theme.omp.json" -ForegroundColor Green
    } catch {
        Write-Host "✗ 下载失败: $theme.omp.json" -ForegroundColor Red
    }
}

# 3. 验证下载
Get-ChildItem "$env:LOCALAPPDATA\Programs\oh-my-posh\themes"
```

* * *

## 5.安装字体

### 为什么需要 Nerd Font？

Oh My Posh 主题使用特殊图标，需要支持这些图标的字体。

### 推荐字体

#### 英文环境

- **CascadiaCode Nerd Font**（推荐）

- **FiraCode Nerd Font**

- **JetBrainsMono Nerd Font**

#### 中英文混排（推荐）

- **Sarasa Mono SC Nerd**（更纱黑体，完美支持中文）

### 安装方法

#### 方法 1：使用 Oh My Posh 字体安装工具（最简单）

```
oh-my-posh font install
```

选择推荐字体：

- 使用方向键选择 `CascadiaCode`

- 按回车确认

#### 方法 2：手动下载安装

**CascadiaCode Nerd Font：**

1. 访问：https://github.com/ryanoasis/nerd-fonts/releases/latest

3. 下载 `CascadiaCode.zip`

5. 解压 ZIP 文件

7. 选择所有 `.ttf` 文件

9. 右键 → "为所有用户安装"

**Sarasa Mono SC Nerd（中文支持）：**

1. 访问：https://github.com/be5invis/Sarasa-Gothic/releases

3. 下载 `Sarasa-TTF-<version>.7z`

5. 解压后找到 `sarasa-mono-sc-nerd-*.ttf`

7. 右键 → "为所有用户安装"

#### 方法 3：使用 Scoop（推荐给开发者）

```
# 安装 Scoop（如果没有）
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex

# 添加 nerd-fonts bucket
scoop bucket add nerd-fonts

# 安装字体
scoop install CascadiaCode-NF
# 或
scoop install Sarasa-Gothic
```

* * *

## 6.配置 Windows Terminal

### 设置字体

1. **打开 Windows Terminal**

3. **按 `Ctrl + ,` 打开设置**

5. **左侧选择 "配置文件" → "默认值"**（或选择特定的 PowerShell 配置）

7. **点击 "外观" 选项卡**

9. **在 "字体" 下拉菜单中选择：**
    - 纯英文：`CaskaydiaCove Nerd Font`
    
    - 中英文：`CaskaydiaCove Nerd Font, Microsoft YaHei UI`
    
    - 完美中文：`Sarasa Mono SC Nerd`

11. **字体大小设置为 `11`**

13. **点击 "保存"**

### 设置配色方案（可选）

1. 在设置界面左侧选择 "配色方案"

3. 推荐方案：
    - **One Half Dark** - 优雅深色
    
    - **Campbell Powershell** - 经典
    
    - **Dracula** - 流行主题

5. 返回 "配置文件" → 选择你的 PowerShell

7. 在 "外观" 中选择配色方案

### JSON 配置示例

如果想直接编辑配置文件：

1. 按 `Ctrl + ,` 打开设置

3. 点击左下角 "打开 JSON 文件"

5. 找到你的 PowerShell 配置，添加或修改：

```
{
    "profiles": {
        "list": [
            {
                "guid": "{你的PowerShell GUID}",
                "name": "PowerShell",
                "font": {
                    "face": "CaskaydiaCove Nerd Font, Microsoft YaHei UI",
                    "size": 11
                },
                "colorScheme": "One Half Dark",
                "useAcrylic": true,
                "acrylicOpacity": 0.85,
                "cursorShape": "bar",
                "padding": "8"
            }
        ]
    }
}
```

* * *

## 7.配置 PowerShell

### 创建配置文件

1. **检查配置文件是否存在** `Test-Path $PROFILE`

3. **如果不存在，创建配置文件** `New-Item -Path $PROFILE -Type File -Force`

5. **编辑配置文件** `notepad $PROFILE`

### 基础配置（推荐）

将以下内容粘贴到配置文件中：

```
# Oh My Posh - 使用本地主题
oh-my-posh init pwsh --config "$env:LOCALAPPDATA\Programs\oh-my-posh\themes\paradox.omp.json" | Invoke-Expression

# Terminal Icons（文件和文件夹图标）
Import-Module -Name Terminal-Icons
```

### 如果本地主题不存在，使用在线主题

```
# Oh My Posh - 使用在线主题
oh-my-posh init pwsh --config "https://raw.githubusercontent.com/JanDeDobbeleer/oh-my-posh/main/themes/paradox.omp.json" | Invoke-Expression

# Terminal Icons
Import-Module -Name Terminal-Icons
```

### 推荐主题

本地主题路径格式：`$env:LOCALAPPDATA\Programs\oh-my-posh\themes\<主题名>.omp.json`

在线主题格式：`https://raw.githubusercontent.com/JanDeDobbeleer/oh-my-posh/main/themes/<主题名>.omp.json`

**轻量简洁：**

- `jandedobbeleer` - 默认主题

- `paradox` - 简洁现代

- `agnoster` - 经典设计

**信息丰富：**

- `atomic` - 详细信息（需要 Nerd Font）

- `powerlevel10k_rainbow` - 彩色炫酷

- `night-owl` - 深色优雅

### 保存并加载配置

```
# 保存配置文件后，重新加载
. $PROFILE
```

* * *

## 8.安装增强模块

### PSReadLine（命令行增强）

**检查版本：**

```
Get-Module PSReadLine -ListAvailable
```

**更新到最新版（需要管理员权限）：**

```
Install-Module PSReadLine -Force -SkipPublisherCheck
```

**添加到配置文件：**

编辑 `$PROFILE`，添加以下内容：

```
# PSReadLine 配置（需要 2.2.0+ 版本）
if ((Get-Module PSReadLine).Version -ge '2.2.0') {
    Set-PSReadLineOption -PredictionSource History
    Set-PSReadLineOption -PredictionViewStyle ListView
}

Set-PSReadLineOption -EditMode Windows
Set-PSReadLineKeyHandler -Key Tab -Function MenuComplete
Set-PSReadLineKeyHandler -Key UpArrow -Function HistorySearchBackward
Set-PSReadLineKeyHandler -Key DownArrow -Function HistorySearchForward
```

### Terminal-Icons（文件图标）

**安装：**

```
Install-Module -Name Terminal-Icons -Repository PSGallery -Force
```

**已在基础配置中包含，无需额外配置**

* * *

## 9.常见问题排查

### 问题 1：禁止运行脚本

**错误信息：**

```
无法加载文件...因为在此系统上禁止运行脚本
```

**解决方案：**

```
# 以管理员身份运行
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

* * *

### 问题 2：CONFIG NOT FOUND

**错误信息：**

```
CONFIG NOT FOUND
```

**原因：** 主题文件路径不存在

**解决方案 1：检查路径**

```
Test-Path $env:POSH_THEMES_PATH
```

**解决方案 2：手动下载主题（见"安装 Oh My Posh"章节）**

**解决方案 3：使用在线主题**

```
# 编辑配置文件
notepad $PROFILE

# 使用在线主题
oh-my-posh init pwsh --config "https://raw.githubusercontent.com/JanDeDobbeleer/oh-my-posh/main/themes/paradox.omp.json" | Invoke-Expression
```

* * *

### 问题 3：图标显示为问号或方框

**原因：** 没有安装 Nerd Font 字体或 Windows Terminal 未配置正确字体

**解决方案：**

1. **安装 Nerd Font 字体**（见"安装字体"章节）

3. **在 Windows Terminal 中设置字体**
    - 按 `Ctrl + ,`
    
    - 配置文件 → 默认值 → 外观
    
    - 字体选择：`CaskaydiaCove Nerd Font` 或 `Sarasa Mono SC Nerd`

5. **完全关闭并重启 Windows Terminal**

* * *

### 问题 4：PSReadLine 参数错误

**错误信息：**

```
找不到与参数名称"PredictionSource"匹配的参数
```

**原因：** PSReadLine 版本过旧

**解决方案：**

```
# 以管理员身份运行
Install-Module PSReadLine -Force -SkipPublisherCheck

# 或使用兼容配置
notepad $PROFILE
```

**兼容配置：**

```
# 只使用基础功能
Set-PSReadLineOption -EditMode Windows
Set-PSReadLineKeyHandler -Key Tab -Function Complete
```

* * *

### 问题 5：加载时间过长（2000+ 毫秒）

**原因：** 使用在线主题或模块加载慢

**解决方案 1：使用本地主题**

```
# 下载主题到本地（见"安装 Oh My Posh"章节的手动下载部分）
# 使用本地路径
oh-my-posh init pwsh --config "$env:LOCALAPPDATA\Programs\oh-my-posh\themes\paradox.omp.json" | Invoke-Expression
```

**解决方案 2：优化配置**

```
# 使用更轻量的主题
oh-my-posh init pwsh --config "$env:LOCALAPPDATA\Programs\oh-my-posh\themes\jandedobbeleer.omp.json" | Invoke-Expression

# 延迟加载 Terminal Icons
$null = Register-EngineEvent PowerShell.OnIdle -Action {
    Import-Module Terminal-Icons
    Unregister-Event PowerShell.OnIdle
}
```

**测试加载时间：**

```
Measure-Command { . $PROFILE }
```

正常应该在 300-800 毫秒之间。

* * *

### 问题 6：中文显示问题

**解决方案：** 使用支持中文的字体配置

**Windows Terminal 设置：**

```
字体：CaskaydiaCove Nerd Font, Microsoft YaHei UI
或
字体：Sarasa Mono SC Nerd
```

* * *

## 10.进阶优化

### 完整配置示例

编辑 `$PROFILE`：

```
# ============================================
# Oh My Posh 主题配置
# ============================================
oh-my-posh init pwsh --config "$env:LOCALAPPDATA\Programs\oh-my-posh\themes\paradox.omp.json" | Invoke-Expression

# ============================================
# 模块导入
# ============================================
Import-Module -Name Terminal-Icons
Import-Module -Name z

# ============================================
# PSReadLine 配置
# ============================================
if ((Get-Module PSReadLine).Version -ge '2.2.0') {
    # 历史记录预测
    Set-PSReadLineOption -PredictionSource History
    Set-PSReadLineOption -PredictionViewStyle ListView
}

# 基础配置
Set-PSReadLineOption -EditMode Windows
Set-PSReadLineOption -BellStyle None

# 快捷键绑定
Set-PSReadLineKeyHandler -Key Tab -Function MenuComplete
Set-PSReadLineKeyHandler -Key UpArrow -Function HistorySearchBackward
Set-PSReadLineKeyHandler -Key DownArrow -Function HistorySearchForward

# ============================================
# 别名和函数
# ============================================
# 快速清屏
Set-Alias -Name cls -Value Clear-Host

# 快速编辑配置文件
function Edit-Profile {
    notepad $PROFILE
}
Set-Alias -Name ep -Value Edit-Profile

# 快速重载配置
function Reload-Profile {
    . $PROFILE
}
Set-Alias -Name rp -Value Reload-Profile

# ============================================
# 欢迎信息
# ============================================
Write-Host "PowerShell $($PSVersionTable.PSVersion) - " -NoNewline
Write-Host "Oh My Posh $(oh-my-posh version)" -ForegroundColor Cyan
```

### 自定义配色方案

创建自定义 Dracula 主题：

1. 按 `Ctrl + ,` 打开设置

3. 点击左下角 "打开 JSON 文件"

5. 在 `schemes` 数组中添加：

```
{
    "schemes": [
        {
            "name": "Dracula",
            "background": "#282A36",
            "foreground": "#F8F8F2",
            "black": "#21222C",
            "blue": "#BD93F9",
            "cyan": "#8BE9FD",
            "green": "#50FA7B",
            "purple": "#FF79C6",
            "red": "#FF5555",
            "white": "#F8F8F2",
            "yellow": "#F1FA8C",
            "brightBlack": "#6272A4",
            "brightBlue": "#D6ACFF",
            "brightCyan": "#A4FFFF",
            "brightGreen": "#69FF94",
            "brightPurple": "#FF92DF",
            "brightRed": "#FF6E6E",
            "brightWhite": "#FFFFFF",
            "brightYellow": "#FFFFA5"
        }
    ]
}
```

4. 在配置文件中使用：`"colorScheme": "Dracula"`

### 背景图片和透明效果

在 Windows Terminal 设置 JSON 中添加：

```
{
    "profiles": {
        "list": [
            {
                "backgroundImage": "C:/Users/YourName/Pictures/background.jpg",
                "backgroundImageOpacity": 0.2,
                "useAcrylic": true,
                "acrylicOpacity": 0.8
            }
        ]
    }
}
```

* * *

## 11.验证最终效果

### 检查清单

- \[ \] Windows Terminal 已安装

- \[ \] PowerShell 执行策略已配置

- \[ \] Oh My Posh 已安装并显示版本号

- \[ \] Nerd Font 字体已安装

- \[ \] Windows Terminal 字体已配置

- \[ \] PowerShell 配置文件已创建

- \[ \] 主题正常显示，无 "CONFIG NOT FOUND"

- \[ \] 图标正常显示，无乱码

- \[ \] 加载时间在 800ms 以内

- \[ \] PSReadLine 自动补全正常工作

### 测试命令

```
# 查看版本
oh-my-posh version
$PSVersionTable.PSVersion
Get-Module PSReadLine | Select-Object Version

# 测试加载时间
Measure-Command { . $PROFILE }

# 测试图标显示
Get-ChildItem
```

* * *

## 快速参考

### 常用命令

```
# 编辑配置文件
notepad $PROFILE

# 重载配置
. $PROFILE

# 查看主题
Get-ChildItem $env:POSH_THEMES_PATH

# 预览所有主题
Get-PoshThemes

# 切换主题（临时）
oh-my-posh init pwsh --config "$env:POSH_THEMES_PATH\atomic.omp.json" | Invoke-Expression
```

### 推荐资源

- Oh My Posh 官方文档：https://ohmyposh.dev/

- Oh My Posh 主题预览：https://ohmyposh.dev/docs/themes

- Nerd Fonts：https://www.nerdfonts.com/

- Windows Terminal 文档：https://docs.microsoft.com/zh-cn/windows/terminal/

* * *

## 12.总结

完成以上配置后，你将拥有：

✅ 现代化、美观的终端界面  
✅ 丰富的 Git 信息显示  
✅ 智能命令补全和历史记录  
✅ 文件和文件夹图标  
✅ 快速的加载速度  
✅ 完美的中英文支持

享受你的全新终端体验！🎉