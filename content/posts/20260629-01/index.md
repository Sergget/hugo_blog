---
title: 零额外功耗！利用 Tailscale + 自建私有 DERP 完美搞定跨地域异地组网
date: '2026-06-29'
lastmod: '2026-07-22T02:50:02Z'
slug: 20260629-01
categories:
- 网络漫游
tags: []
draft: false
---

在跨地域或严格的内网环境下，Tailscale 经常因打洞失败而不得不求助于官方的 DERP 中转服务器。由于官方节点均在海外，动辄 200ms+ 的延迟和极低的带宽严重影响体验。本文将详细介绍如何在拥有**动态公网 IPv4** 且常开的 Windows 11 设备上，利用**纯原生工具**（不依赖任何第三方服务注册软件）搭建高速、低延迟的私有 DERP 中转站，并配置故障自愈和完全隐身运行。

## 🛠️ 第一步：用 Go 纯净环境编译 derper 核心

新版的 `derper` 强制要求验证和本地配置文件。我们直接在本地的 Go 环境下进行编译。

1. **准备 Go 语言环境**：前往 [Go 官网](https://go.dev/) 下载 Windows 版本的安装包（`.msi`）并完成安装。

3. 打开 PowerShell 窗口，配置国内代理加速并下载编译 `derper`：PowerShell`$env:GO111MODULE="on" $env:GOPROXY="https://goproxy.cn,direct" # 下载并编译二进制文件 go install tailscale.com/cmd/derper@main`

5. 编译完成后，核心程序 `derper.exe` 会生成在 `C:\Users\你的用户名\go\bin\` 目录下。

## 🔐 第二步：一键用 Go 生成合规的自签名 SSL 证书

由于 DERP 强制要求 HTTPS 且新版对密钥格式审查严格，Windows 自带的 `certutil` 导出的私钥经常触发 `found a certificate rather than a key` 的报错。最稳妥的办法是直接用 Go 的标准加密库生成纯正的 PEM 格式证书。

确保在 `C:\Users\你的用户名\go\bin` 路径下，运行以下长命令。它会在本地临时创建一个 `gen.go` 脚本，生成专用的 `.crt` 和 `.key` 文件后自动自我销毁：

```
go run qiniupkg.com/x/crypto.v7/keypair/main.go -host "你的DDNS域名" 2>$null; if (-not $?) { go run (New-Item -Path . -Name "gen.go" -ItemType "File" -Value 'package main; import ("crypto/rand"; "crypto/rsa"; "crypto/x509"; "crypto/x509/pkix"; "encoding/pem"; "math/big"; "net"; "os"; "time"); func main() { priv, _ := rsa.GenerateKey(rand.Reader, 2048); template := x509.Certificate{SerialNumber: big.NewInt(1), Subject: pkix.Name{CommonName: "你的DDNS域名"}, NotBefore: time.Now(), NotAfter: time.Now().AddDate(10, 0, 0), KeyUsage: x509.KeyUsageKeyEncipherment | x509.KeyUsageDigitalSignature, ExtKeyUsage: []x509.ExtKeyUsage{x509.ExtKeyUsageServerAuth}, DNSNames: []string{"你的DDNS域名"}, IPAddresses: []net.IP{net.ParseIP("127.0.0.1")}}; certBytes, _ := x509.CreateCertificate(rand.Reader, &template, &template, &priv.PublicKey, priv); certFile, _ := os.Create("你的DDNS域名.crt"); pem.Encode(certFile, &pem.Block{Type: "CERTIFICATE", Bytes: certBytes}); certFile.Close(); keyFile, _ := os.Create("你的DDNS域名.key"); pem.Encode(keyFile, &pem.Block{Type: "RSA PRIVATE KEY", Bytes: x509.MarshalPKCS1PrivateKey(priv)}); keyFile.Close() }' -Force).FullName; go run .\gen.go; Remove-Item .\gen.go }
```

确认目录下成功生成了 `你的DDNS域名.crt` 和 `你的DDNS域名.key`。

## 🌐 第三步：主路由端口转发配置

前往公网 IPv4 所在的路由器后台（例如华硕路由器），为运行 `derper` 的本地 Win11 笔记本配置虚拟服务器/端口转发：

| **服务名称** | **外网端口** | **内网 IP 地址** | **内网端口** | **协议** |
| --- | --- | --- | --- | --- |
| DERP-HTTPS | `8443` | `你的Win11本地内网IP` | `8443` | `TCP` |
| DERP-STUN | `3478` | `你的Win11本地内网IP` | `3478` | `UDP` |

> _注：Windows 防火墙可能会拦截入站流量，建议在 Win11 高级防火墙中同样为 `8443(TCP)` 和 `3478(UDP)` 放行。_

## 📝 第四步：Tailscale 控制台 ACL 接入

登录 Tailscale 管理后台，在 **Access Controls** 配置文件中加入自签名白名单节点。注意：**新版 Tailscale 参数字段严格区分大小写，且不支持 JSON 注释**。

请粘贴以下标准格式：

```
{
	"grants": [
		{"src": ["*"], "dst": ["*"], "ip": ["*"]}
	],
	"ssh": [
		{
			"action": "check",
			"src":    ["autogroup:member"],
			"dst":    ["autogroup:self"],
			"users":  ["autogroup:nonroot", "root"]
		}
	],
	"derpMap": {
		"OmitDefaultRegions": false,
		"Regions": {
			"901": {
				"RegionID":   901,
				"RegionCode": "my-home-derp",
				"RegionName": "Private Home DERP",
				"Nodes": [
					{
						"Name":             "win11-derp",
						"RegionID":         901,
						"HostName":         "你的DDNS域名",
						"derpPort":         8443,
						"stunPort":         3478,
						"InsecureForTests": true
					}
				]
			}
		}
	}
}
```

## 第五步：完美隐身、开机延迟自启与断网自愈配置

为了避免桌面上一直挂着一个易被误关的 PowerShell 黑色窗口，同时为了让服务在设备重启、网络恢复后能自动重连，我们采用 **VBS 脚本 + Windows 任务计划程序**的纯原生方案。

### 1\. 编写隐身 VBS 启动脚本

在 `C:\Users\你的用户名\go\bin` 目录下，新建一个文本文档，重命名为 `run_derp.vbs`（注意后缀名切换）。用记事本写入以下 1 行代码：

```
CreateObject("Wscript.Shell").Run "C:\Users\你的用户名\go\bin\derper.exe -hostname 你的DDNS域名 -certmode manual -certdir C:\Users\你的用户名\go\bin -a :8443 -stun-port 3478 -verify-clients -c C:\Users\你的用户名\go\bin\derp.conf", 0, False
```

_(末尾的 `, 0` 参数代表彻底隐藏该进程引发的所有黑窗口)_

### 2\. 配置任务计划程序（Task Scheduler）

1. 管理员身份打开“任务计划程序”，点击右侧 **创建基本任务**，命名为 `TailscaleDERP`。

3. **触发器**：选择“计算机启动时”。

5. **操作**：选择“启动程序”。
    - **程序或脚本**：输入 `wscript.exe`
    
    - **添加参数**：输入 `"C:\Users\你的用户名\go\bin\run_derp.vbs"`
    
    - **起始于**：输入 `C:\Users\你的用户名\go\bin`

7. 勾选“当单击完成时，打开此任务的属性对话框”并点击完成。

### 3\. 高级属性微调（防灾核心）

在弹出的属性面板中调整三个关键标签页：

- **常规**：选择“不管用户是否登录都要运行”，彻底压制潜在的交互弹窗。

- **触发器**：双击“计算机启动时”，勾选 **“延迟任务时间”** 改为 **1 分钟**。给系统网络和 DDNS 解析留出初始化时间。

- **设置（断网自愈）**：勾选 **“如果任务失败，按以下时间间隔重新启动”** 改为 **1 分钟**，并将 **“尝试重新启动的次数”** 改为 **99 次**。这样一旦遭遇宽带偶发断网，Windows 会在后台无限期每隔 1 分钟自动拉起进程，直至网络恢复。

## ⚡ 验证连接状态

在远端任意一台 Tailscale 节点上打开终端执行验证：

1. 运行 `tailscale netcheck`：在返回的 `DERP latency` 列表中可以清晰地看到 `my-home-derp` 已经榜上有名，且延迟会从海外节点的 150ms+ 断崖式下跌到 **15ms~25ms**。

3. 运行 `tailscale status` 确认流量不再绕道海外。

在 Windows 任务管理器中，该服务会以一个隐身的 `wscript.exe` 宿主和独立的 `derper.exe` 进程在后台默默工作，至此，一套**零额外功耗、纯原生自愈**的 Tailscale 加速方案搭建完成。