# 5.2 snap包管理入门
snap 是 Canonical 公司推出的跨 Linux 发行版的软件包格式，旨在实现“一次打包，处处运行”。它解决了传统包管理（如 apt）的依赖复杂、版本碎片化等问题，并自带沙箱安全机制。Ubuntu 22.04 默认已安装 snap，可直接使用。

## 1. 核心概念
- snap：软件包文件（扩展名为 .snap），包含应用及其所有依赖。
- snapd：后台服务，负责安装、更新、运行 snap 应用。
- channel：软件发布渠道，如 stable（稳定版）、candidate（候选版）、beta（测试版）、edge（每日构建版）。
- confinement：运行限制等级。
- strict：严格沙箱，默认，只能访问特定资源。
- classic：经典模式，权限与传统包类似，需手动授权。
- devmode：开发模式，完全开放但仅用于调试。

## 2. 常用命令
|操作|命令|
|-|-|
|查找软件|snap find <关键词>|
|查看软件详情|snap info <软件名>|
|安装软件|sudo snap install <软件名>|
|指定渠道安装|sudo snap install <软件名> --channel=<渠道>|
|经典模式安装|sudo snap install <软件名> --classic|
|列出已安装|snap list|
|更新单个软件|sudo snap refresh <软件名>|
|更新所有软件|sudo snap refresh|
|回滚到上一版本|sudo snap revert <软件名>|
|卸载软件|sudo snap remove <软件名>|
|查看变更记录|snap changes|
|查看某次变更详情|snap change <变更ID>|
## 3. 实用示例
安装 Nextcloud 私有云
```bash
sudo snap install nextcloud
```
安装完成后，访问 http://你的IP 即可开始配置。

安装 VLC 媒体播放器
```bash
sudo snap install vlc
```
安装经典模式软件（如 helm）
有些软件需要经典模式才能访问系统全部资源：

```
sudo snap install helm --classic
```
切换软件发布渠道
例如将 Nextcloud 切换到候选版：

```bash
sudo snap switch nextcloud --channel=candidate
sudo snap refresh nextcloud
```
查看已安装软件的权限（接口）
```bash
snap connections nextcloud
```
可查看该软件使用的 plug（请求权限）和 slot（提供权限）。

## 4. 管理 snap 的磁盘占用
snap 会保留旧版本以便回滚，但可能占用大量磁盘空间。查看已保留版本：

```bash
snap list --all
```
清理旧版本（保留最新两个）：

```bash
sudo snap set system refresh.retain=2
```
或手动删除某软件的旧版本：

```bash
sudo snap remove <软件名> --revision=<版本号>
```
## 5. 常见问题
命令找不到：某些 snap 安装后，其可执行文件不在 PATH 中，但 snap 会自动将命令链接到``` /snap/bin```，确保该目录在 PATH 中（Ubuntu 默认已添加）。

权限不足：如果软件需要访问摄像头、蓝牙等资源，需手动连接接口，例如：
```bash
sudo snap connect <软件名>:camera :camera
```
更新策略：snap 默认每天自动检查更新，可通过 ```sudo snap refresh --hold``` 临时暂停。

## 6. 进阶学习
snap 还有丰富的安全机制、接口管理、打包工具（snapcraft）等。如果你对底层原理或如何制作自己的 snap 包感兴趣，可参考后续章节《snap 深入剖析》或官方文档 snapcraft.io。