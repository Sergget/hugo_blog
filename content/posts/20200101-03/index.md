---
categories:
- 网络漫游
date: 2020-01-01
draft: false
slug: 20200101-03
tags: []
title: 搭建一个webdav 服务器
---

## 什么是WebDAV？

WebDAV（Web Distributed Authoring and Versioning）是HTTP/1.1协议的扩展，支持：

- 文件锁定（防止编辑冲突）

- 元数据管理（作者、修改日期等）

- 命名空间操作（移动/复制文件）

- 版本控制（通过DeltaV扩展）

相比FTP，WebDAV使用标准HTTP端口（80/443），更易穿透防火墙，且支持加密传输。

## 环境准备

### 1\. 安装Apache2

```
sudo apt update && sudo apt install apache2 -y
```

### 2\. 安装测试工具（可选）

cadaver是命令行WebDAV客户端：

```
sudo apt install cadaver -y
```

## 配置步骤

### 1\. 启用Apache模块

```
sudo a2enmod dav_fs        # 自动包含dav模块
sudo a2enmod dav_lock      # 文件锁定支持
sudo systemctl restart apache2
```

### 2\. 创建共享目录

```
sudo mkdir -p /var/www/webdav
sudo chown -R www-data:www-data /var/www/webdav
sudo chmod -R 775 /var/www/webdav  # 确保可写权限
```

### 3\. 创建认证用户

```
#创建密码文件（首次使用-c参数）
sudo htpasswd -c /etc/apache2/webdav.passwd sergget

#添加额外用户（省略-c参数）
sudo htpasswd /etc/apache2/webdav.passwd user2

#设置权限
sudo chown root:www-data /etc/apache2/webdav.passwd
sudo chmod 640 /etc/apache2/webdav.passwd
```

### 4\. 配置虚拟主机

创建配置文件：

```
sudo nano /etc/apache2/sites-available/webdav.conf
```

添加以下内容：

```
<VirtualHost *:80>
    ServerAdmin admin@example.com
    DocumentRoot /var/www/html

    # WebDAV专属路径
    Alias /webdav "/var/www/webdav"
    
    <Directory "/var/www/webdav">
        DAV On
        Options Indexes FollowSymLinks
        
        # 认证配置
        AuthType Basic
        AuthName "WebDAV Access"
        AuthUserFile /etc/apache2/webdav.passwd
        Require valid-user
        
        # 权限设置
        <LimitExcept GET POST OPTIONS>
            Require valid-user
        </LimitExcept>
    </Directory>
    
    ErrorLog ${APACHE_LOG_DIR}/webdav-error.log
    CustomLog ${APACHE_LOG_DIR}/webdav-access.log combined
</VirtualHost>
```

### 5\. 启用站点

```
sudo a2dissite 000-default.conf    # 禁用默认站点
sudo a2ensite webdav.conf          # 启用WebDAV配置
sudo systemctl reload apache2      # 平滑重载配置
```

## 连接验证

### 命令行测试

```
cadaver http://localhost/webdav/
#输入创建的用户名/密码

ls        # 列出文件
put test.txt  # 上传文件
get document.pdf  # 下载文件
```

### 客户端支持

常用支持WebDAV的客户端：

- Windows：映射网络驱动器

- macOS：Finder > 连接服务器

- Linux：Dolphin/GNOME Files

- 手机：Solid Explorer, FE File Explorer

## 高级配置建议

1.**启用HTTPS加密**

```
sudo apt install certbot python3-certbot-apache
sudo certbot --apache
```

2.**存储配额限制**  
在`<Directory>`块中添加：

```
DavQuota on
DavQuotaLimit "1 GB"
```

**增强安全设置**

```
# 禁用目录列表
Options -Indexes

# 限制IP访问
Require ip 192.168.1.0/24
```

## 故障排查

- **权限问题**：确保`www-data`用户对目录有写权限

- **连接拒绝**：检查防火墙设置 `sudo ufw allow 80/tcp`

- **认证失败**：验证密码文件路径和权限

- **查看日志**：`tail -f /var/log/apache2/webdav-*.log`

> 最佳实践提示：生产环境务必启用HTTPS，定期使用`htpasswd`命令更新密码，敏感文件避免使用WebDAV共享。