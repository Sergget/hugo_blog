---
categories:
- 网络漫游
date: 2026-06-26
draft: false
slug: 20260626-01
tags: []
title: 通过 Cloudflare Tunnel 在浏览器中远程访问 Windows 桌面（RDP）
---

Cloudflare 于 2025 年推出了浏览器内 RDP 功能，基于 Zero Trust Access 实现。无需在客户端安装任何 RDP 软件，也无需开放任何入站端口，只需一个浏览器即可远程访问 Windows 桌面。

前面我们讲了使用Apache Guacamole (Docker)作为中转来远程访问，但实际上，将windows密码明文写在配置文件中不安全，新开一个本地账户也需要重新安装、登录软件，配置权限等。总之非常不方便，今天我们使用cloudflare直接在浏览器中远程访问windows桌面。

## 前提条件

- Windows 10/11 主机已开启远程桌面（RDP）

- 已安装 cloudflared 并建立了 Tunnel

- 域名已托管在 Cloudflare（需要 DNS 管理权）

- 拥有 Cloudflare Zero Trust 账户（免费计划即可）

## 第一步：Windows 开启远程桌面

进入 **设置 → 系统 → 远程桌面**，开启远程桌面功能。建议同时启用 **网络级别身份验证（NLA）**。

> **注意**：Windows 账户必须设置有传统密码，Windows Hello PIN 无法用于 RDP 登录。若使用 Microsoft 账户，需确认密码已在本地缓存。

## 第二步：配置 Tunnel 私有网络路由

进入 [Cloudflare Zero Trust 控制台](https://one.dash.cloudflare.com/)，依次进入：

**Networks → Connectors → Cloudflare Tunnels → 选择你的 Tunnel → 编辑**

切换到 **Private Networks（CIDR）** 标签，添加 Win10 所在的内网网段，例如：

```
192.168.0.0/24
```

## 第三步：创建 Target（目标资源）

进入 **Access controls → Targets → Add a target**，填写以下信息：

| 字段 | 示例值 | ||--| | Target hostname | `win10-home`（自定义友好名称） | | IP address | `192.168.0.10`（Win10 内网 IP） | | Port | `3389` | | Virtual network | `default` |

> Target hostname 是自定义名称，不是域名也不是 IP，后续在 Application 中需要引用这个名称。

## 第四步：创建 DNS 记录

在 Cloudflare DNS 面板为你的域名新建一条 CNAME 记录，例如 `rdp.yourdomain.com`。

- **类型**：CNAME

- **名称**：`rdp`（或其他自定义前缀）

- **目标**：`<tunnel-id>.cfargotunnel.com`

- **Proxy 状态**：橙色云朵（Proxied）

> 这条 DNS 记录不需要指向实际服务器 IP，Cloudflare 的 RDP 代理会处理路由。

## 第五步：创建 Access Application

进入 **Access controls → Applications → Add an application → Self-hosted**，配置如下：

| 字段 | 填写内容 | ||| | Application name | 自定义，如 `Win10 RDP` | | Public hostname | `rdp.yourdomain.com` | | **Browser rendering** | **RDP**（关键步骤） | | Target hostname | 选择第三步创建的 Target 名称 | | Port | `3389` |

然后配置 **Policy（访问策略）**：

- 类型选 **Allow**

- Include 条件选 **Emails**，填入允许访问的邮箱地址

- 多个邮箱分别添加为独立的 Include 条目（OR 逻辑）

最后在 **Experience Settings** 中勾选 **Show application in App Launcher**。

## 使用方式

### 方式一：通过 App Launcher 访问（推荐）

访问你的 Access 团队地址：

```
https://<your-team-name>.cloudflareaccess.com
```

输入邮箱，接收验证码登录后，在 App Launcher 中点击 RDP 应用即可在浏览器中启动会话。

### 方式二：收藏完整 URL 直接访问

App Launcher 启动 RDP 时会跳转到如下格式的 URL：

```
https://rdp.yourdomain.com/rdp/<vnet-id>/<target-ip>/3389
```

将此完整 URL 加入浏览器书签，以后可直接访问，无需每次经过 App Launcher。

`直接访问根域名 rdp.yourdomain.com 会报错 Unable to find your RDP target，这是 Cloudflare 的产品设计限制，必须携带完整的 target 参数。`

## 登录流程

完整的连接流程如下：

```
1. 访问 https://<team-name>.cloudflareaccess.com
2. 输入邮箱 → 接收验证码 → 完成 Access 身份验证
3. 在 App Launcher 中点击 RDP 应用
4. 在浏览器 RDP 窗口中输入 Windows 用户名和密码
5. 进入 Windows 桌面
```

`建议将 Access Session Duration 设置为 1 month，这样在同一台设备的同一浏览器中，一次登录后长期有效，无需频繁接收验证码。`

## 安全特性

- **零端口暴露**：3389 端口完全不对外开放，所有流量通过 Cloudflare 出站隧道传输

- **无需客户端软件**：任何支持现代浏览器的设备均可访问

- **Access 身份验证**：连接前必须通过 Cloudflare Access 验证，支持邮件 OTP、Google、GitHub 等多种登录方式

- **Cloudflare 不保存 Windows 凭据**：每次会话需手动输入 Windows 用户名和密码

## 常见问题

**Q：报错 `Unable to find your RDP target`**  
A：通常是以下原因之一：Browser rendering 未选择 RDP；Application 中 Target criteria 未关联 Target；访问的是根域名而非完整 URL。

**Q：App Launcher 中看不到应用**  
A：检查 Application 的 Experience Settings 是否勾选了 Show in App Launcher；检查 Policy 中的邮箱是否与登录邮箱一致。

**Q：Target 创建时 IP 下拉框为空**  
A：说明 Tunnel 的 Private Networks CIDR 未配置，或路由未生效，先检查 Networks → Routes 中是否有对应条目。