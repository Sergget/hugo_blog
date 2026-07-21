---
categories:
- 网络漫游
date: 2026-07-03
draft: false
slug: 20260703-02
tags: []
title: 基于 IPv6 直连与 Cloudflare Tunnel 的 Immich 双链路高可用照片备份
---

### 痛点与背景

在搭建私有相册部署服务（如 Immich）时，远程访问通常面临两个抉择：

1. **Cloudflare Tunnel（内网穿透）**：免去公网 IP 的烦恼，且带有安全防护和标准 HTTPS。但免费版存在**单个文件上传最大 100MB** 的硬性限制，在备份动辄数 GB 的手机原画视频时极易断开。
2. **公网 IPv6 直连**：随着家宽 IPv6 的普及，端到端的直连速度极快，且**完全没有上传大小限制**。但 IPv6 地址是动态变化的，且直接暴露端口存在安全隐患。

为了兼顾“大文件无限制传输（IPv6直连）”与“全网无缝容灾（CF Tunnel）”，本文实践了一套双链路高可用方案。当处于良好 IPv6 网络下，客户端优先走高带宽直连；在纯 IPv4 环境下，自动降级走 Tunnel 容灾。
### 第一部分：方案架构设计
本方案的核心在于通过 Nginx 精确分流，将现有的 Web 服务（如 WordPress）与相册服务隔离，同时利用 `acme.sh` 的 DNS API 模式自动为 IPv6 直连申请原生 SSL 证书。
- **第一顺位（主力）**：`https://your-ipv6-subdomain.domain.com` $\rightarrow$ Nginx (443) $\rightarrow$ Immich (2283)【灰云直连，无限制】
- **第二顺位（容灾）**：`https://your-tunnel-subdomain.domain.com` $\rightarrow$ Cloudflare Tunnel $\rightarrow$ Immich (2283)【黄云穿透，100MB限制】

### 第二部分：核心配置步骤

#### 1. Nginx 宿主机反向代理与大文件优化

在 `/etc/nginx/sites-available/` 下为 IPv6 直连域名创建独立的虚拟主机配置，利用精确的 `server_name` 匹配，避免被已有的默认重定向规则（如 `server_name _`）拦截。
```nginx
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name your-ipv6-subdomain.domain.com;

    # SSL 证书路径
    ssl_certificate /etc/nginx/ssl/immich.crt;
    ssl_certificate_key /etc/nginx/ssl/immich.key;

    # 核心：解除 Nginx 自身的上传限制（0 代表无限）
    client_max_body_size 0;

    # 关闭临时文件缓冲，大文件直接透传给后端容器，避免磁盘 I/O 瓶颈
    proxy_buffering off;
    proxy_request_buffering off;

    location / {
        proxy_pass http://127.0.0.1:2283; 
        
        # 传递必要的 Header
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 开启 WebSocket 支持（Immich 实时同步必须）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 延长超时时间到 10 分钟以上，防止大视频切片传输时间过长
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;
        keepalive_timeout 620s;
    }
}
```

#### 2. 轻量化 SSL 证书自动化（acme.sh）

避免引入沉重的可视化证书管理容器，直接在宿主机利用 `acme.sh` 配合 Cloudflare DNS API 验证申请 ECC 证书：
```Bash
# 导入 Cloudflare 凭证
export CF_Token="your_cloudflare_dns_edit_token"
export CF_Account_ID="your_cloudflare_account_id"

# 申请证书
acme.sh --set-default-ca --server letsencrypt
acme.sh --issue --dns dns_cf -d your-ipv6-subdomain.domain.com --ecc

# 安全安装证书至 Nginx 目录并配置自动重载
acme.sh --install-cert -d your-ipv6-subdomain.domain.com --ecc \
--key-file       /etc/nginx/ssl/immich.key  \
--fullchain-file /etc/nginx/ssl/immich.crt \
--reloadcmd     "sudo systemctl reload nginx"
```

#### 3. 稳健的 Shell + Crontab IPv6 DDNS 脚本

家宽 IPv6 变化频繁，且 Cloudflare API 对于 Token 鉴权较为严格。当使用局部的 `DNS:Edit` 权限 Token 时，必须通过特定的 `ZONE_ID` 精确发起 `PATCH` 请求，否则极易触发误导性的 `10000 Authentication error`。
编写自动化更新脚本 `~/scripts/cf-ddns.sh`：
```Bash
#!/bin/bash

# --- 配置区域 ---
CF_TOKEN="your_cloudflare_dns_edit_token"
ZONE_ID="your_cloudflare_zone_id"
SUBDOMAIN="your-ipv6-subdomain.domain.com"
# ----------------

# 1. 获取服务器当前的公网 IPv6 地址（排除本地链路和临时地址）
CURRENT_IPV6=$(ip -6 addr show scope global | grep -v "deprecated" | grep -oE '([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}' | head -n 1)

if [ -z "$CURRENT_IPV6" ]; then
    echo "$(date): 未检测到公网 IPv6 地址"
    exit 1
fi

# 2. 查询 Cloudflare 当前的 AAAA 记录
DNS_RECORD_INFO=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records?type=AAAA&name=$SUBDOMAIN" \
     -H "Authorization: Bearer $CF_TOKEN" \
     -H "Content-Type: application/json")

if [[ "$DNS_RECORD_INFO" == *"\"success\":false"* ]]; then
    echo "$(date): Cloudflare API 鉴权失败！详细报错: $DNS_RECORD_INFO"
    exit 1
fi

RECORD_ID=$(echo "$DNS_RECORD_INFO" | awk -F'"id":"' '{print $2}' | awk -F'"' '{print $1}')
CLOUDFLARE_IPV6=$(echo "$DNS_RECORD_INFO" | awk -F'"content":"' '{print $2}' | awk -F'"' '{print $1}')

if [ -z "$RECORD_ID" ]; then
    echo "$(date): 未在 Cloudflare 中找到 $SUBDOMAIN 的 AAAA 记录，请确认后台已手动添加过该记录。"
    exit 1
fi

# 3. 比对并执行轻量更新
if [ "$CURRENT_IPV6" = "$CLOUDFLARE_IPV6" ]; then
    echo "$(date): IP 未发生改变 ($CURRENT_IPV6)，无需更新。"
else
    echo "$(date): IP 发生改变，正在将 [$CLOUDFLARE_IPV6] 更新为 [$CURRENT_IPV6]..."
    
    UPDATE_RESULT=$(curl -s -X PATCH "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records/$RECORD_ID" \
         -H "Authorization: Bearer $CF_TOKEN" \
         -H "Content-Type: application/json" \
         --data "{\"content\":\"$CURRENT_IPV6\"}")
         
    if [[ "$UPDATE_RESULT" == *"\"success\":true"* ]]; then
        echo "$(date): Cloudflare DNS 更新成功！"
    else
        echo "$(date): Cloudflare DNS 更新失败！错误信息: $UPDATE_RESULT"
    fi
fi
```

通过 `crontab -e` 设置每 5 分钟定时对齐：

```
*/5 * * * * /bin/bash /home/username/scripts/cf-ddns.sh >> /home/username/scripts/ddns.log 2>&1
```

### 第三部分：避坑指南总结

1.   **Cloudflare 10000 报错陷阱**：CF API Token 在进行 `zones` 查询或修改时，如果传入的 `ZONE_ID` 实际上是 `Account ID`，接口不会返回“未找到该区域”，而是直接抛出权限不足的混淆报错。可通过 `curl -s -X GET "https://api.cloudflare.com/client/v4/zones" -H "Authorization: Bearer <TOKEN>"` 准确核对专属的 32 位 Zone ID。
    
2. **安全性防探测兜底**：灰云直连意味着向公网暴露了 443 端口。建议修改全局 `nginx.conf` 引入 `server_tokens off;` 隐藏版本。同时配置未匹配域名的默认 `443` 虚拟主机，对直接扫描公网 IPv6 地址的请求直接返回 `444`（断开连接），确保只有通过专属合法域名访问的客户端才能安全握手。