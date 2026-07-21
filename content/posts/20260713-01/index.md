---
categories:
- 来点码吧
date: 2026-07-13
draft: false
slug: 20260713-01
tags: []
title: Claude Code 免订阅桥接 DeepSeek
---

通过配置系统环境变量，可绕过 Anthropic 官方订阅限制，将 Claude Code 命令行客户端的底层大模型切换为 DeepSeek 引擎。所有请求和扣费均通过个人的 DeepSeek API 账户处理。

## 一、 客户端安装

由于存在地区限制，直接使用官方 `curl` 或 `powershell` 脚本下载可能会触发风控阻断。请使用各系统的原生包管理器绕过限制进行安装：

### 1. 全平台通用（使用 Node.js / npm 推荐）
```bash
npm install -g @anthropic-ai/claude-code
```

### 2. Mac 用户（使用 Homebrew）
```Bash
brew install anthropic-ai/claude-code/claude-code
```

### 3. Windows 用户（使用 winget）
```PowerShell
winget install Anthropic.ClaudeCode
```

## 二、 永久系统环境变量配置

将环境变量写入系统，使 Claude Code 全局默认重定向至 DeepSeek 服务器。

### 1. Linux / macOS 环境

打开终端配置文件（以 `~/.zshrc` 为例，若使用 Bash 请改为 `~/.bashrc`）：
```bash
vim ~/.zshrc
```

在文件末尾添加以下配置内容：
```Bash
# Claude Code 切换为 DeepSeek 引擎
export ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
export ANTHROPIC_AUTH_TOKEN="你的_DEEPSEEK_API_KEY"

# 模型映射配置
export ANTHROPIC_MODEL=deepseek-v4-pro
export ANTHROPIC_DEFAULT_OPUS_MODEL=deepseek-v4-pro
export ANTHROPIC_DEFAULT_SONNET_MODEL=deepseek-v4-pro
export ANTHROPIC_DEFAULT_HAIKU_MODEL=deepseek-v4-flash
export CLAUDE_CODE_SUBAGENT_MODEL=deepseek-v4-flash
export CLAUDE_CODE_EFFORT_LEVEL=max
```

保存并退出编辑器后，使配置在当前终端生效：
```Bash
source ~/.zshrc
```

### 2. Windows 环境（图形界面配置）

1. 按下 `Win + S`，搜索并打开“编辑系统环境变量”。
2. 点击右下角“环境变量”按钮。
3. 在“用户变量”区域点击“新建”，依次将下列键值对添加至系统中：

|**变量名 (Variable Name)**|**变量值 (Variable Value)**|
|---|---|
|`ANTHROPIC_BASE_URL`|`https://api.deepseek.com/anthropic`|
|`ANTHROPIC_AUTH_TOKEN`|_你的_DEEPSEEK_API_KEY_|
|`ANTHROPIC_MODEL`|`deepseek-v4-pro`|
|`ANTHROPIC_DEFAULT_OPUS_MODEL`|`deepseek-v4-pro`|
|`ANTHROPIC_DEFAULT_SONNET_MODEL`|`deepseek-v4-pro`|
|`ANTHROPIC_DEFAULT_HAIKU_MODEL`|`deepseek-v4-flash`|
|`CLAUDE_CODE_SUBAGENT_MODEL`|`deepseek-v4-flash`|
|`CLAUDE_CODE_EFFORT_LEVEL`|`max`|

> ⚠️ **注意**：配置完成后，必须重新启动当前打开的终端（或关闭并重新打开 VS Code），新加的环境变量方能生效。

## 三、 启动与验证

完成上述配置后，**无需使用 Claude Desktop 桌面软件**。直接在终端中切换到项目目录并执行以下命令：
```Bash
claude
```

交互式编程助手将被拉起，其底层交互全面由绑定的 DeepSeek 账户承载。