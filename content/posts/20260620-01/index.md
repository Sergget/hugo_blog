---
categories:
- 网络漫游
date: 2026-06-20
draft: false
slug: 20260620-01
tags: []
title: 基于 Cloudflare Tunnel + Docker 搭建安全无公网的 Web RDP 远程桌面备份方案
---

在日常工作和运维中，我们经常需要远程控制办公室的 Windows 计算机。传统的 RDP（3389 端口）直连方式不仅需要公网 IP，还会将端口暴露在公网，极易遭受自动化脚本的暴力破解。

本文将分享如何利用 **Cloudflare Zero Trust (Tunnel)** 与 **Apache Guacamole (Docker)**，在**不暴露任何公网端口、不需要公网 IP** 的情况下，搭建一个纯网页端（Web-based）的远程桌面备份方案。在外只需通过浏览器输入专属域名，经过双重安全验证后即可秒变 Windows 桌面。

## 🛠️ 方案架构概述

整个架构的数据流向如下：

`外网浏览器` -> `Cloudflare Access (邮箱验证码拦截)` -> `Cloudflare Tunnel 边缘网络` -> `本地 cloudflared 守护进程` -> `Docker 内部 Guacamole 网关 (RDP转HTML5)` -> `Windows 本地远程桌面 (3389)`。

## 一、 计算机侧配置（Windows 10 宿主机）

### 1\. 安装docker

1. 在docker.com注册docker账户

3. 下载docker，并安装后登录

5. 确保本机wsl、虚拟机平台启用后打开docker

### 2\. 编写 Docker Compose 配置文件

在本地创建工作目录（如 `C:\Guacamole`），并在该目录下创建以下两个核心配置文件。

#### ① `docker-compose.yml`

最新版的 Guacamole 支持通过 `WEBAPP_CONTEXT` 环境变量直接将服务挂载到根路径（`/`），从而完美配合 Cloudflare Tunnel 的转发规则：

```
services:
  guacd:
    image: guacamole/guacd:latest
    restart: always
  guacamole:
    image: guacamole/guacamole:latest
    restart: always
    ports:
      - "8080:8080"
    environment:
      GUACD_HOSTNAME: guacd
      INDEX_AUTH_PROVIDER: basic
      # 核心配置：将 Web 路径直接映射为根目录，避免外网访问时输入 /guacamole 后缀
      WEBAPP_CONTEXT: ROOT
    volumes:
      - ./user-mapping.xml:/etc/guacamole/user-mapping.xml
```

#### ② `user-mapping.xml`（脱敏版）

用于配置登录 Guacamole 网页端的账号密码，以及映射本机的 RDP 连接。**出于安全考虑，强烈建议在 Windows 侧创建一个低权限的本地专用 RDP 账户，或在此配置文件中删掉密码参数，在网页端现场输入，避免将微软在线账户的明文密码暴露在本地配置文件中**。

```
<user-mapping>
    <authorize username="web_admin" password="your_secure_web_password">
        <connection name="Work Desktop Backup">
            <protocol>rdp</protocol>
            <param name="hostname">host.docker.internal</param> 
            <param name="port">3389</param>
            <param name="username">your_windows_username</param>
            <param name="password">your_windows_password</param>
            
            <param name="ignore-cert">true</param>
            <param name="resize-method">display-update</param>
        </connection>
    </authorize>
</user-mapping>
```

### 3\. 启动容器网关

在当前目录下打开终端，执行以下命令后台运行服务：

```
docker-compose up -d
```

此时在本地浏览器访问 `http://localhost:8080` 即可看到原生的登录窗并成功连接桌面。

## 二、 网页端与 Cloudflare 侧配置

### 1\. 创建 Cloudflare Tunnel

1. 登录 [Cloudflare Zero Trust 控制台](https://one.dash.cloudflare.com/)。

3. 选择 **Networks** -> **Tunnels** -> **Create a tunnel**。

5. 环境选择 **Windows**，复制页面上给出的命令行安装包指令。

7. 回到单位电脑，以**管理员身份**打开 PowerShell 粘贴并运行该指令。`cloudflared` 将会自动注册为 Windows 本地系统服务，实现开机自启。

### 2\. 配置公网域名路由 (Public Hostnames)

当 Tunnel 状态变为 **Healthy** 后，添加一条 Ingress 路由规则：

- **Subdomain**: `rdp` _(可自定义)_

- **Domain**: `yourdomain.com` _(选择你接入 CF 的自备域名)_

- **Path**: `留空`

- **Type**: `HTTP`

- **URL**: `http://localhost:8080`

> **⚠️ 注意**：Cloudflare Tunnel 的 Ingress 规则由于安全架构限制，**不支持**在转发时进行路径重写（例如不能在 URL 后面加 `/guacamole/`）。我们已经在 Docker 侧通过 `WEBAPP_CONTEXT: ROOT` 彻底解决了这个问题，此处保持纯净的端口映射即可。

## 三、 📝 终极安全加固 (Cloudflare Access 零信任策略)

为了防止域名暴露后网页端密码遭遇暴力破解，必须引入 Cloudflare Edge 端的**身份验证拦截（自托管应用策略）**：

1. 在 Zero Trust 控制台，前往 **Access** -> **Applications** -> **Add an application** -> 选择 **Self-hosted**。

3. **Application URL**: 填写你刚才配置的完整二级域名（如 `rdp.yourdomain.com`）。

5. **Session Duration**: 建议设为 `24 Hours`（一天只需认证一次）。

7. 进入 **Rules (策略配置)**：
    - **Action**: `Allow`
    
    - **Include**: 选择 **Emails**，并在右侧输入你**私人的常用电子邮箱**（如 Gmail/Outlook）。

9. 保存策略。

## 🚀 紧急情况下的实际使用流体验

当下班回家或在外出差，遭遇紧急情况需要控制单位电脑时：

1. **第一道防线**：打开任意设备浏览器访问 `https://rdp.yourdomain.com`，页面会被 Cloudflare 强行拦截，要求输入预设的邮箱。

3. **安全验证**：输入邮箱后，查收 6 位数动态验证码并填入网页。

5. **第二道防线**：通过拦截后，页面无缝展露出 Guacamole 登录窗，输入你在 `user-mapping.xml` 中设置的网页端账密。

7. **完美控端**：登录成功，整个浏览器窗口秒变单位的 Windows 10 桌面。键盘、鼠标、丝滑全屏以及剪贴板双向同步均能完美工作。