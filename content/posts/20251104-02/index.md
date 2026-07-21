---
categories:
- 网络漫游
date: 2025-11-04
draft: false
slug: 20251104-02
tags: []
title: PowerShell远程连接教程
---

## 1 PowerShell远程管理基础

PowerShell远程管理功能基于WS-Management协议，由Windows远程管理服务实现，允许用户跨网络在一台或多台远程计算机上执行命令和脚本。与仅支持单个命令的cmdlet不同，PowerShell Remoting支持交互式会话和复杂的脚本执行。

​**核心组件**是WinRM服务，它默认使用HTTP端口5985或HTTPS端口5986进行通信。这种基于标准HTTP/S的设计使其能够较容易地穿透防火墙。

## 2 环境配置步骤

### 2.1 远程主机配置

远程主机是需要被管理的计算机，必须首先启用PowerShell远程处理功能。

​1.**以管理员身份启动PowerShell**​：右键点击PowerShell图标，选择“以管理员身份运行”。

​2.**设置执行策略**​（可选，但建议设置）：

```
Set-ExecutionPolicy RemoteSigned -Force
```

​3.**启用PowerShell远程处理**​：

```
Enable-PSRemoting -Force
```

此命令将：

- 启动或重启WinRM服务

- 将WinRM服务启动类型设置为“自动”

- 创建侦听程序以接受任意IP地址上的请求

- 为WS-Management通信启用Windows防火墙入站规则例外

​4.**检查网络连接类型**​：确保网络位置不是“公用”，因为Windows防火墙例外不能在公用网络位置启用。如果是公用网络，需更改为“专用”：

```
Set-NetConnectionProfile -InterfaceAlias "以太网" -NetworkCategory Private
```

### 2.2 客户端配置

客户端是用于发起远程连接的管理计算机。

​1.**设置TrustedHosts**​：在非域环境中，必须将远程主机添加到客户端的信任主机列表。

```
Set-Item WSMan:\localhost\Client\TrustedHosts -Value "远程主机IP" -Force
```

如需信任所有计算机（测试环境），可使用：

```
Set-Item WSMan:\localhost\Client\TrustedHosts -Value "*" -Force
```

2.**启用客户端远程支持**​：

```
Enable-PSRemoting -SkipNetworkProfileCheck -Force
```

## 3 远程连接方法

### 3.1 交互式会话

交互式会话允许用户像在远程计算机上直接操作一样执行命令。

```
Enter-PSSession -ComputerName 192.168.1.100 -Credential administrator
```

连接成功后，提示符会变为`[远程主机IP]: PS ...`，此时输入的命令将在远程主机上执行。

退出会话使用：

```
Exit-PSSession
```

### 3.2 执行单条命令

对于单条命令或简单任务，使用`Invoke-Command`更高效：

```
Invoke-Command -ComputerName 192.168.1.100 -Credential administrator -ScriptBlock {
    Get-Process | Where-Object { $_.CPU -gt 10 }
}
```

### 3.3 持久连接

对于需要多次执行的相关命令，可创建持久连接以提高效率：

```
$session = New-PSSession -ComputerName 192.168.1.100 -Credential administrator
Invoke-Command -Session $session -ScriptBlock {$processes = Get-Process}
Invoke-Command -Session $session -ScriptBlock {$processes.Count}
Remove-PSSession $session
```

## 4 高级配置与故障排除

### 4.1 常见错误及解决方案

​**错误**​：WinRM 客户端无法处理该请求。如果身份验证方案与 Kerberos 不同...​

**解决方案**​：将远程主机IP添加到客户端的TrustedHosts列表。

```
Set-Item WSMan:\localhost\Client\TrustedHosts -Value "本地机ip" -Force
```

### 4.2 认证方式选择

在不同网络环境下，可能需要指定不同的认证机制：

```
Enter-PSSession -ComputerName 192.168.1.100 -Credential administrator -Authentication CredSSP
```

特别是当需要从远程会话访问另一台服务器资源时，CredSSP认证可以传递凭据。

### 4.3 服务管理与诊断

1. ​**检查WinRM服务状态**​：`Get-Service WinRM Test-WSMan -ComputerName 192.168.1.100`

3. ​**查看当前WinRM配置**​：`winrm get winrm/config`

5. ​**快速检查配置**​：`winrm quickconfig`

## 5 安全注意事项

1. ​**最小权限原则**​：只授予必要的远程访问权限

3. ​**使用HTTPS传输**​：生产环境建议配置证书并使用5986端口

5. ​**限制TrustedHosts**​：尽量避免使用`*`，而是指定具体IP或计算机名

7. ​**定期审查**​：定期检查远程访问日志和配置