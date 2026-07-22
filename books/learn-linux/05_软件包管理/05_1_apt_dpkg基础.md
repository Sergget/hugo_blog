# 5.1 apt 与 dpkg 基础教程
## 1. 简介
在 Ubuntu/Debian 系统中，软件包管理基于 dpkg（底层工具）和 apt（高层前端）。

dpkg：直接操作 .deb 包，处理安装、卸载、查询，但不自动处理依赖关系。

apt（Advanced Package Tool）：在 dpkg 之上封装，自动解决依赖、管理软件源，推荐日常使用。

## 2. dpkg 基础命令
### 2.1 安装本地 .deb 包
```
sudo dpkg -i 包名.deb
```
若提示依赖缺失，随后需运行``` sudo apt install -f ```修复。

### 2.2 卸载软件包
```
sudo dpkg -r 包名          # 保留配置文件
sudo dpkg -P 包名          # 彻底删除（含配置文件）
```
### 2.3 查询已安装的包
```
dpkg -l                    # 列出所有已安装包
dpkg -l | grep 关键字       # 搜索特定包
dpkg -L 包名                # 列出包安装的文件列表
dpkg -S 文件路径            # 查询文件属于哪个包
```
### 2.4 查看包状态
```
dpkg -s 包名                # 显示包状态信息
```
## 3. apt 基础命令
apt 命令需 sudo 权限（查询类除外）。

### 3.1 更新软件源
```
sudo apt update            # 从源获取最新软件包列表
sudo apt upgrade           # 升级所有可升级的包（不处理依赖变更）
sudo apt full-upgrade      # 智能升级，必要时安装/卸载依赖
```
### 3.2 安装与卸载
```
sudo apt install 包名       # 安装（可自动补全）
sudo apt install 包名=版本  # 安装指定版本
sudo apt remove 包名        # 卸载（保留配置文件）
sudo apt purge 包名         # 卸载并清除配置
sudo apt autoremove         # 自动删除不再需要的依赖包
```
### 3.3 搜索与信息
```
apt search 关键字           # 搜索软件包
apt show 包名               # 显示包详细信息（版本、依赖、描述）
apt list --installed        # 列出已安装包（类似 dpkg -l）
apt list --upgradable       # 列出可升级包
```
### 3.4 清理缓存
```
sudo apt clean              # 清空 /var/cache/apt/archives/ 下的所有 .deb
sudo apt autoclean           # 仅删除过时的 .deb
```
## 4. 配置文件
### 4.1 软件源列表
主配置文件：```/etc/apt/sources.list```

扩展配置目录：```/etc/apt/sources.list.d/```（通常每个源一个 .list 文件）

源格式示例（Ubuntu 22.04）：

```
deb http://archive.ubuntu.com/ubuntu jammy main restricted universe multiverse
deb-src http://archive.ubuntu.com/ubuntu jammy main restricted universe multiverse
```
deb 表示二进制包，deb-src 表示源码包。

组件：main（官方支持）、universe（社区维护）、restricted（专有驱动）、multiverse（版权受限）。

### 4.2 apt 配置文件
主配置：```/etc/apt/apt.conf```，或放在 ```/etc/apt/apt.conf.d/``` 下。
常用配置示例（设置代理）：

```
Acquire::http::Proxy "http://proxy.example.com:8080";
```
## 5. 基本排障
### 5.1 无法锁定 /var/lib/dpkg/lock
```
sudo rm /var/lib/dpkg/lock          # 删除锁文件（谨慎）
sudo rm /var/cache/apt/archives/lock  # 也可删除缓存锁
```
原因：另一个 apt/dpkg 进程正在运行。先确认无其他进程再删除。

### 5.2 依赖损坏或破损包
```
sudo apt --fix-broken install       # 修复破损依赖
sudo dpkg --configure -a             # 重新配置未完成的包
```
### 5.3 源错误导致更新失败
检查``` /etc/apt/sources.list ```是否正确（备份后修改）。

尝试更换镜像源（如阿里云、清华源）。

### 5.4 软件包被保持（hold）
```
apt-mark showhold                   # 查看被锁定的包
sudo apt-mark unhold 包名            # 解除保持
```
### 5.5 安装时提示“无法找到包”
先``` sudo apt update ```更新列表。

确认包名是否正确，或是否属于特定组件（如 multiverse）未开启。

## 6. 实用技巧
apt-mark：标记包为自动/手动安装，用于 autoremove 控制。

```
sudo apt-mark auto 包名     # 标记为自动安装
sudo apt-mark manual 包名   # 标记为手动安装
```
apt-cache：查询缓存信息（老命令，现可用 apt show/search 替代）。

```
apt-cache policy 包名        # 查看可安装版本及优先级
apt-cache depends 包名       # 查看依赖关系
```
下载源码：

```
apt source 包名              # 需在 sources.list 中启用 deb-src
```
## 7. 总结
- 日常操作：优先使用 apt（自动解决依赖）。
- 本地包操作：使用 dpkg，配合 apt install -f 修复依赖。
- 遇到问题：先 update，再 --fix-broken，最后检查源。
- 配置文件：源列表和 apt 配置是系统更新的基础，谨慎修改。