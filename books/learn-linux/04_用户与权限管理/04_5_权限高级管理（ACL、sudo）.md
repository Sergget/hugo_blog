# 4.5 权限高级管理（ACL、sudo）
本节介绍一些超过传统`rwx`三位表示法的权限管理工具，包括访问控制列表（ACL）和`sudo`。对于需要给特定用户或组赋予细粒度权限，以及让普通账号执行管理员命令时很有用。

## 1. ACL 简介
标准的`chmod`只能处理所有者、所属组和其他用户三类权限。当需要为额外的用户或组设置不同权限时，可以使用ACL。

- 查看文件或目录的ACL：
  ```bash
  getfacl filename
  ```
- 设置ACL：
  ```bash
  setfacl -m u:alice:rw file   # 给alice读写权限
  setfacl -m g:dev:rx dir      # 给dev组读执行权限
  ```
- 删除ACL条目：
  ```bash
  setfacl -x u:alice file       # 移除alice的ACL
  setfacl -b file               # 删除所有ACL，恢复传统权限
  ```
- 默认ACL：可用于目录，设置后新文件继承此ACL
  ```bash
  setfacl -d -m u:bob:rwX project/
  ```

简要例子：
```bash
# 文件foo的所有者为root，所属组为staff
$ ls -l foo
-rw-r--r-- 1 root staff 0 foo
$ setfacl -m u:guest:rw foo   # guest也可读写
$ getfacl foo
# 结果中会有额外的user:guest:rw条目
```

ACL通常在多用户协作、共享目录时使用，习惯上应与标准权限配合使用。

## 2. sudo 基础
`sudo`允许普通用户以另一个身份（通常是root）运行命令，同时记录日志。管理员通过`/etc/sudoers`文件控制谁可以使用`sudo`以及可以执行哪些命令。

- 编辑`sudoers`时必须使用`visudo`，它会做语法检查：
  ```bash
  sudo visudo
  ```

- 典型条目：
  ```text
  # 允许alice以任何身份在任何主机上运行所有命令
  alice ALL=(ALL) ALL

  # bob可以运行特定命令，无需密码
  bob ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart apache2
  ```

- `sudo`使用：
  ```bash
  sudo command        # 提示输入当前用户密码
  sudo -i             # 以root交互式登录
  sudo -l             # 列出该用户的sudo权限
  ```

配置建议：

1. 最小权限原则，只授权必要命令。
2. 将常用组如wheel/adm添加至sudoers以便统一管理。
3. 使用`Defaults`选项控制超时、日志等，例如：
   ```text
   Defaults timestamp_timeout=5   # 5分钟后需重新输入
   ```

通过ACL和sudo，管理员可以在不放松整个系统安全的前提下提供灵活的访问与执行能力。

