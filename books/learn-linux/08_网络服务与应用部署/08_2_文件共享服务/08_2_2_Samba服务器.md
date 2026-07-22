# 8.2.2 Samba 服务器
Samba 提供与 Windows 文件共享（SMB/CIFS）兼容的服务，常用于在 Linux 与 Windows 之间共享文件或在局域网内部搭建共享目录。本节给出快速上手步骤与常见配置示例，便于学习和实操。

## 1 安装
```bash
sudo apt update
sudo apt install samba
```

## 2 基本配置文件位置
主配置文件位于 `/etc/samba/smb.conf`。

## 3 简单共享示例
在 `smb.conf` 的末尾添加一个共享：
```ini
[shared]
   path = /srv/samba/shared
   browseable = yes
   read only = no
   guest ok = no
   create mask = 0644
   directory mask = 0755
```
创建目录并设置权限：
```bash
sudo mkdir -p /srv/samba/shared
sudo chown -R nobody:nogroup /srv/samba/shared
sudo chmod 0775 /srv/samba/shared
```

## 4 本地用户与 Samba 用户
Samba 可使用系统用户进行认证，需要为用户设置 Samba 密码：
```bash
sudo useradd -M smbuser -s /usr/sbin/nologin   # 如需独立账户可创建系统用户
sudo smbpasswd -a smbuser
sudo smbpasswd -e smbuser
```
然后重启 Samba 服务：
```bash
sudo systemctl restart smbd nmbd
```

## 5 访问测试
- 在 Linux 上使用 `smbclient`：
```bash
smbclient //localhost/shared -U smbuser
```
- 在另一台 Linux 挂载：
```bash
sudo mount -t cifs -o username=smbuser //server_ip/shared /mnt
```
- 在 Windows 上通过 `\\server_ip\shared` 访问。

## 6 权限与安全建议
- 使用文件系统权限配合 Samba 的 `create mask`/`directory mask` 控制新文件权限。
- 如需匿名共享，可将 `guest ok = yes`，但要注意安全风险。
- 如果系统启用了 SELinux，请同时配置 SELinux 上的共享权限（例如 `setsebool -P samba_enable_home_dirs on` 或调整 `semanage fcontext`）。

## 7 进阶（提示）
- 配置基于组的共享访问，使用 `valid users = @groupname` 或 `write list` 管理写权限。
- 若需在企业环境使用，请配置 Samba 的域控制器功能或与 Active Directory 集成（超出本笔记范围）。

## 8 小结
Samba 是局域网中文件互通的常用工具，适合桌面/小型服务器共享。初学时先用简单共享与本地用户验证流程，熟练后再考虑权限与安全增强措施。
