---
categories:
- 网络漫游
date: 2026-06-30
draft: false
slug: 20260630-01
tags: []
title: 优雅的外网离线下载：Aria2 + AriaNg + Cloudflare Tunnel 安全长常驻方案
---

在现代私有云与数字化工作流中，拥有一个能够“随时随地、即添加即走”的远程离线下载服务器是极大地提升生产力的利器。本文将完整记录如何从零开始，在服务器侧部署 Aria2 核心，通过 Systemd 实现无缝系统常驻，并利用 Cloudflare Tunnel 与 Zero Trust 构建免公网 IP、免配置 SSL 证书的超安全外网访问控制。同时，本文还包含了一套全自动、具备错误熔断机制的 BT Tracker 定态跟踪优化脚本。

## 🛠 一、 后端核心：Aria2 安装、配置与 Systemd 常驻服务

### 1.1 基础目录准备与配置分离

为了保证系统升级或脚本读写时不破坏核心参数，推荐将 **主配置** 与 **动态变化的 Tracker 列表** 进行文件分离。

在当前用户的家目录下创建配置目录（以用户 `user` 为例）：

```
mkdir -p ~/.aria2
touch ~/.aria2/aria2.conf
touch ~/.aria2/tracker.conf
touch ~/.aria2/aria2.session
```

打开 `~/.aria2/aria2.conf`，写入以下经过优化的核心基础配置：

```
# ====== 基础与下载设置 ======
dir=/path/to/your/downloads
log-level=warn
input-file=/home/user/.aria2/aria2.session
save-session=/home/user/.aria2/aria2.session
save-session-interval=60
max-concurrent-downloads=5
continue=true

# ====== RPC 远程控制设置 ======
enable-rpc=true
rpc-allow-origin-all=true
rpc-listen-all=true
rpc-listen-port=6800
# 强烈建议设置复杂的 Secret Token 保护接口
rpc-secret=YOUR_HEAVY_RPC_SECRET_TOKEN

# ====== BT 特殊设置 ======
bt-max-peers=55
enable-dht=true
enable-peer-exchange=true

# ====== 核心重点：解耦引入外部 Tracker ======
include=/home/user/.aria2/tracker.conf
```

> **注意**：Aria2 的 `include` 语法要求被引入文件绝不能为空。请在 `tracker.conf` 中首行预先写入 `bt-tracker=` 占位，否则启动会报错。

### 1.2 构建 Systemd 服务实现无缝常驻

为了让 Aria2 在系统崩溃或重启时能够自动拉起，我们需要将其托管给系统的 init 进程。

创建服务单元文件：

Bash

```
sudo nano /etc/systemd/system/aria2.service
```

写入以下配置（**关键点在于显式指定普通用户 `User` 运行，避免遭遇权限壁垒**）：

```
[Unit]
Description=Aria2 Download Manager
After=network.target

[Service]
Type=simple
User=user
ExecStart=/usr/bin/aria2c --conf-path=/home/user/.aria2/aria2.conf
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

确保文件的所有权正确，然后启动并启用开机自启：

```
sudo chown -R user:user /home/user/.aria2
sudo systemctl daemon-reload
sudo systemctl enable aria2
sudo systemctl start aria2
```

通过 `sudo systemctl status aria2` 验证，若看到一片绿色的 `active (running)` 则说明后端核心部署成功。

## 🌐 二、 网络穿透：Nginx 转发与 Cloudflare Tunnel 边缘映射

### 2.1 应对 RPC 协议限制的痛点

Cloudflare Tunnel 默认只转发标准的 HTTP/HTTPS（80/443）流量，而 Aria2 RPC 采用的是原生的 TCP 协议（6800端口）。为了规避浏览器的“混合内容安全策略（Mixed Content）”拦截，最优雅的解法是**通过 Nginx 拦截 RPC 的 WebSocket 长连接，将其伪装并合并到 80 端口，再交给 Tunnel 加密上云**。

### 2.2 Nginx 反向代理配置

在 Nginx 的站点配置文件中，为 RPC 请求专门开辟一条伪装路径（例如 `/jsonrpc`），并开启对 WebSocket 协议头（Upgrade）的支持：

Nginx

```
server {
    listen 80;
    server_name aria.yourdomain.com; # 你的 Cloudflare 映射域名

    # 转发 Aria2 RPC 信号
    location /jsonrpc {
        proxy_pass http://127.0.0.1:6800/jsonrpc;
        proxy_redirect off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # 核心：支持 WebSocket 长连接
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 可选：如果你将 AriaNg 前端静态文件也托管在该服务器
    location / {
        root /var/www/aria-ng;
        index index.html;
    }
}
```

配置完成后重载服务：`sudo nginx -s reload`。

### 2.3 Cloudflare Tunnel 绑定

进入 Cloudflare Zero Trust 控制台，在 Tunnels 页面下为该容器或守护进程添加一个 **Public Hostname**：

- **Subdomain / Domain:** `aria.yourdomain.com`

- **Service Type:** `HTTP`

- **URL:** `localhost:80` (指向 Nginx 端口，而不是直连 6800)

此时，Cloudflare 会在边缘自动为你生成 SSL 证书，全权接管 HTTPS 443 加密。

## 🔒 三、 访问控制：Zero Trust 拦截下的 RPC 策略穿透

当我们在 Cloudflare Access 中为 `aria.yourdomain.com` 部署了身份验证（如邮箱验证码）后，由于 AriaNg 前端发起的 RPC 异步长连接无法自动携带 Cloudflare 的认证 Cookie，会导致前端报错“Aria2 未连接”。

### 最佳安全策略：Bypass 路由分割

为了既保护网页前端（防止不法分子窥探下载列表），又保障 RPC 通道顺畅，我们可以**针对具体的 RPC 路径配置免认证白名单**（由 Aria2 自带的 `rpc-secret` 进行二次鉴权，安全性完备）。

1. 登录 Cloudflare Zero Trust 平台，进入 **Access -> Applications**，编辑你的 Aria2 应用。

3. 导航至 **Policies** 选项卡，点击 **Add a policy**。

5. 创建名为 `Bypass-RPC` 的策略：
    - **Action:** 必须选择 **Bypass**（绕过）

7. 在下面的 **Configure rules** 规则选择器中：
    - **Selector:** 选择 **Path** (部分中文面板可能归类在 URL/HTTP 属性下)
    
    - **Value:** 精确填写 `/jsonrpc`

9. 保存应用。

> ⚠️ **国内网络连通性贴士**：因 WebSocket 协议对网络丢包极其敏感，在国内直连海外 Cloudflare 节点时可能会因跨境网络波动导致 RPC 偶尔断开。但由于 Aria2 后端进程是独立常驻的，**一旦点击下载开始，关闭网页、断开网络或关闭代理均不影响服务器的正常下载流程**。

## 🚀 四、 动态调优：Tracker 自动更新脚本

下载 BitTorrent 资源极其依赖优质的 Tracker 服务器，然而网络上的节点瞬息万变。我们可以编写一套 Bash 脚本，既能免代理直连国内优化的加速源，又能在网络异常时实施“熔断”，保护服务器配置不被洗白。

### 4.1 编写高鲁棒性脚本

创建并编辑 `~/.aria2/trackers-update.sh`：

```
#!/bin/bash

# ================= 配置区域 =================
TRACKER_FILE="/home/user/.aria2/tracker.conf"
# 采用作者 XIU2 官方提供的 Cloudflare 边缘加速源，国内直连极度丝滑
TRACKER_URL="https://cf.trackerslist.com/best.txt"
TMP_FILE="/tmp/aria2_trackers.tmp"
# ============================================

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始更新 Tracker 列表..."

# 1. 抓取远程列表，设置超时限制
curl -sS -L --connect-timeout 15 --max-time 30 "${TRACKER_URL}" -o "${TMP_FILE}"

# 2. 容错校验：检查网络请求是否遭遇中断
if [ $? -ne 0 ]; then
    echo "【错误】网络请求失败，无法连接到远程服务器！保持原本地可用配置不变。"
    [ -f "${TMP_FILE}" ] && rm "${TMP_FILE}"
    exit 1
fi

# 3. 容错校验：检查下载到的内容是否为空
if [ ! -s "${TMP_FILE}" ]; then
    echo "【错误】下载到的文件内容为空！保持原本地可用配置不变。"
    rm -f "${TMP_FILE}"
    exit 1
fi

# 4. 容错校验：通过特征字符检测内容合法性，防止被 404 等网页内容覆盖
if ! grep -qE "udp://|http://|ws://" "${TMP_FILE}"; then
    echo "【错误】下载的文件内容格式不正确（未检测到有效协议）！保持原本地可用配置不变。"
    rm -f "${TMP_FILE}"
    exit 1
fi

# 5. 格式化处理：将换行符替换为 Aria2 所需的逗号分隔符
NEW_TRACKERS=$(awk '{if(NR==1){printf "%s", $0}else{printf ",%s", $0}}' "${TMP_FILE}" | sed 's/,,*/,/g' | sed 's/,$//')

if [ -z "${NEW_TRACKERS}" ]; then
    echo "【错误】数据格式化转换异常！保持原本地可用配置不变。"
    rm -f "${TMP_FILE}"
    exit 1
fi

# 6. 安全覆盖原独立配置文件并重载服务
echo "bt-tracker=${NEW_TRACKERS}" > "${TRACKER_FILE}"
echo "【成功】最新 Tracker 列表已安全写入: ${TRACKER_FILE}"
rm -f "${TMP_FILE}"

echo "正在重启 Aria2 服务..."
sudo systemctl restart aria2
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 全步聚更新完成，新 Tracker 已生效！"
```

赋予脚本可执行权限：

```
chmod +x /home/user/.aria2/trackers-update.sh
```

### 4.2 配置 Linux Cron 定时任务

为了实现无需人工干预的动态跟踪，设置 Linux 定时任务：

```
crontab -e
```

在末尾添加一行，使其在每天凌晨 04:00 自动执行该脚本并过滤日常冗余日志：

Plaintext

```
0 4 * * * /bin/bash /home/user/.aria2/trackers-update.sh > /dev/null 2>&1
```

## 🎛 五、 最终客户端连接配置指南

当你在外网环境打开 AriaNg 网页前端时，请定位到 **AriaNg 设置 -> RPC**，按照以下映射关系进行填写：

- **Aria2 RPC 别名**：自定义

- **RPC 协议**：选择 **WebSocket (WXS)** (必须是带安全加密的 WSS)

- **RPC 主机**：填写你在 Cloudflare 绑定的主域名（例如：`aria.yourdomain.com`）

- **RPC 端口**：填写 **443** (因为外网 HTTPS 默认为 443)

- **RPC 路径**：填写 **`/jsonrpc`** (契合你在 Nginx 与 Cloudflare Bypass 策略中指定的路径)

- **RPC 密匙**：填写你在 `aria2.conf` 中配置的 `rpc-secret` 令牌。

至此，整套离线下载系统已完美闭环。你可以享受到安全、干净、不受公网 IP 限制且具备高容错更新能力的私有云下载体验。