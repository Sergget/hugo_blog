# 8.2.1 FTP 服务器（vsftpd）
本节以 `vsftpd`（Very Secure FTP Daemon）为例，介绍如何快速在 Debian/Ubuntu 系统上搭建一个轻量且安全的 FTP 服务，适合用于文件临时共享与学习环境。内容保持简单，便于练习和理解基本概念。

## 1 安装
```bash
sudo apt update
sudo apt install vsftpd
```

## 2 启动与状态
```bash
sudo systemctl enable --now vsftpd
sudo systemctl status vsftpd
```

## 3 常见配置项（/etc/vsftpd.conf）
说明只列常用且安全的选项：
- `anonymous_enable=NO`      # 关闭匿名访问
- `local_enable=YES`         # 允许系统本地用户登录
- `write_enable=YES`         # 允许写操作（上传、删除）
- `chroot_local_user=YES`    # 将本地用户限制在其家目录
- `listen=YES` 或 `listen_ipv6=YES` # 以单独守护进程模式监听

示例（修改 `/etc/vsftpd.conf`）：
```text
anonymous_enable=NO
local_enable=YES
write_enable=YES
chroot_local_user=YES
user_sub_token=$USER
local_root=/home/$USER/ftp
```
修改后重启服务：
```bash
sudo systemctl restart vsftpd
```

## 4 创建一个受限的 FTP 用户示例
```bash
# 创建用户并设置家目录结构
sudo adduser ftpuser
sudo mkdir -p /home/ftpuser/ftp/upload
sudo chown nobody:nogroup /home/ftpuser/ftp
sudo chown ftpuser:ftpuser /home/ftpuser/ftp/upload
```
将 `ftpuser` 的登录目录与 `vsftpd.conf` 中的 chroot 配合使用，可以限制其访问范围。

## 5 被动模式与防火墙
被动模式需要指定端口范围并在防火墙上打开，常见步骤：
- 在 `/etc/vsftpd.conf` 中添加：
```
pasv_min_port=30000
pasv_max_port=30100
pasv_address=你的公网IP  # 仅在 NAT/公网场景需要
```
- 在防火墙（ufw）上允许 20/tcp、21/tcp 及被动端口范围：
```bash
sudo ufw allow 20/tcp
sudo ufw allow 21/tcp
sudo ufw allow 30000:30100/tcp
```

## 6 使用 TLS（提高安全性）
FTP 明文传输密码，建议启用 FTPS（TLS）：
- 生成自签名证书或使用有效证书。
- 在 `/etc/vsftpd.conf` 中启用：
```
ssl_enable=YES
rsa_cert_file=/etc/ssl/certs/vsftpd.pem
rsa_private_key_file=/etc/ssl/private/vsftpd.key
```
启用后客户端需配置使用 FTPS（Explicit/Implicit）连接。

## 7 测试连接
- 使用命令行 ftp 或 `lftp`、图形客户端（FileZilla）连接测试。
- 简单命令行测试：
```bash
ftp 127.0.0.1
# 或者
curl -v --ftp-ssl -u ftpuser:password ftp://127.0.0.1/
```

## 8 小结与建议
- 对公网服务务必启用 TLS，并限制被动端口范围。
- 若仅用于内部或临时共享，可通过 `chroot_local_user`+本地用户实现足够的隔离。
- 生产环境可考虑 SFTP（基于 SSH 的文件传输）作为更安全的替代方案。
