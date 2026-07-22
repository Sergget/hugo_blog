# 6.3 systemd与服务管理

在 Linux 系统中，服务（Service）通常指提供特定功能的守护进程，例如 Web 服务器、数据库等。Ubuntu 通过 service 命令可以方便地管理这些服务。本章将介绍 service 命令的基本用法，并深入讲解如何手动创建和管理自定义服务（基于传统的 SysV init 脚本），以及如何控制服务的开机自启动。

## 1. service 命令基本用法
service 命令用于运行系统服务，常用的命令包括：
| |命令|
|-|-|
|启动服务|sudo service <服务名> start|
|停止服务|sudo service <服务名> stop|
|重启服务|sudo service <服务名> restart|
|查看服务状态|sudo service <服务名> status|
|查看所有服务状态|sudo service --status-all|

该命令会列出所有可用服务及其当前状态（[ + ] 表示运行中，[ - ] 表示已停止，[ ? ] 表示状态未知）。

注意：所有由 service 管理的服务脚本均存放在 `/etc/init.d/` 目录下。你也可以直接调用该目录下的脚本，效果与 service 命令相同。例如：

```bash
sudo service mysql restart
# 等价于
sudo /etc/init.d/mysql restart
```
## 2. service 命令的工作原理
根据 `man service` 的说明，service 命令实际上执行的是位于 `/etc/init.d/` 目录下的脚本（或者 /etc/init 下的 upstart 任务）。当执行 service <服务名> start 时，系统会调用 `/etc/init.d/<服务名>` 脚本，并将 start 作为第一个参数传递给它。

因此，添加一个服务本质上就是向 `/etc/init.d/` 中添加一个可执行的脚本。

注意：在较新版本的 Ubuntu（如 22.04）中，系统默认使用 systemd 作为 init 系统。但为了向后兼容，service 命令仍然可以操作传统的 SysV init 脚本。如果你希望使用更现代的方式管理服务，推荐学习 systemctl 命令（参见本章末的扩展阅读）。

## 3. 手动添加一个自定义服务
下面我们通过一个简单的例子，演示如何手动创建一个名为 hello 的服务。

### 3.1 创建服务脚本
在 `/etc/init.d/` 下创建一个脚本文件（需要 root 权限）：

```bash
sudo touch /etc/init.d/hello
sudo chmod +x /etc/init.d/hello
```
此时，Ubuntu 已经识别出一个名为 hello 的服务。你可以尝试按 Tab 键补全 sudo service hello 来验证。

### 3.2 编写服务脚本内容
服务脚本本质上是一个 Shell 脚本，它根据传入的参数（如 start、stop）执行相应的操作。一个基本的脚本结构如下：

```bash
#!/binbash

case "$1" in
    start)
        echo "Starting hello service..."
        # 这里放置启动服务的命令，例如启动一个守护进程
        ;;
    stop)
        echo "Stopping hello service..."
        # 这里放置停止服务的命令
        ;;
    restart)
        echo "Restarting hello service..."
        $0 stop   # 调用自身执行 stop
        $0 start  # 调用自身执行 start
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}"
        exit 1
        ;;
esac

exit 0
```
第一行 `#!/bin/```bash` 必须保留，否则脚本可能无法正确执行。

### 3.3 测试服务
保存脚本后，即可通过 service 命令测试：

```bash
sudo service hello start
```
如果一切正常，终端会输出 `Starting hello service...`。同样地，执行 stop 和 restart 也会看到对应的输出。

## 4. 控制服务的开机自启动
手动添加的服务默认不会随系统启动而自动运行。要让它在开机时自启动，需要在相应的运行级别目录中创建符号链接。Ubuntu 提供了 `update-rc.d` 命令来简化这一过程。

### 4.1 运行级别简介
Linux 系统有多个运行级别（runlevel），分别代表不同的系统状态：

- 0：关机（halt）
- 1：单用户模式（single user mode）
- 2~5：多用户模式（Ubuntu 桌面版通常默认进入级别 2，且 2~5 无区别）
- 6：重启（reboot）
- S：早期启动阶段（先于其他级别运行）

每个运行级别对应一个目录 `/etc/rc<级别>.d/`，里面存放着指向 `/etc/init.d/` 中脚本的符号链接。链接名称的格式为 `S<数字><服务名>`（表示启动）或 `K<数字><服务名>`（表示停止），数字越小优先级越高。

### 4.2 使用 update-rc.d 添加自启动
执行以下命令为 hello 服务添加默认的自启动配置：

```bash
sudo update-rc.d hello defaults
```
系统会在各个运行级别目录中创建相应的符号链接。执行后终端会显示类似下面的信息：

```text
update-rc.d: warning: /etc/init.d/hello missing LSB information
update-rc.d: see <http://wiki.debian.org/LSBInitScripts>
 Adding system startup for /etc/init.d/hello ...
   /etc/rc0.d/K20hello -> ../init.d/hello
   /etc/rc1.d/K20hello -> ../init.d/hello
   /etc/rc6.d/K20hello -> ../init.d/hello
   /etc/rc2.d/S20hello -> ../init.d/hello
   /etc/rc3.d/S20hello -> ../init.d/hello
   /etc/rc4.d/S20hello -> ../init.d/hello
   /etc/rc5.d/S20hello -> ../init.d/hello
```

`K20hello` 表示在关机（级别 0）、重启（级别 6）等场景下会执行停止操作。

`S20hello` 表示在进入多用户模式（级别 2~5）时会启动服务。

关于警告：提示缺少 LSB 信息（如 Provides、Required-Start 等）并不影响基本功能，可以忽略。若想消除警告，可在脚本中添加 LSB 头，具体参考 Debian Wiki。

### 4.3 移除自启动
若要从自启动中移除该服务（但保留脚本本身），执行：

```bash
sudo update-rc.d -f hello remove
```
这会删除所有运行级别目录中的符号链接。

## 5. 扩展阅读：systemd 与服务管理
自 Ubuntu 15.04 起，系统默认使用 systemd 作为 init 系统。在 systemd 环境下，服务由 unit 文件 定义（通常位于 `/etc/systemd/system/` 或 `/lib/systemd/system/`），并通过 systemctl 命令管理。

例如，查看所有服务状态：

```bash
systemctl list-units --type=service
```
启动/停止服务：

```bash
sudo systemctl start <服务名>
sudo systemctl stop <服务名>
```
启用/禁用开机自启动：

```bash
sudo systemctl enable <服务名>
sudo systemctl disable <服务名>
```
尽管 systemd 已成为主流，但传统的 `/etc/init.d/` 脚本仍然兼容，并且 service 命令在 systemd 系统上会自动将调用转发给 systemctl（如果存在同名的 systemd 服务）。对于简单的自定义服务，编写 SysV init 脚本依然是一种快速有效的方式。若需更精细的控制（如依赖关系、并行启动等），建议学习编写 systemd unit 文件。

## 6. 总结
service 命令是管理传统 SysV init 服务的便捷工具，其本质是调用 `/etc/init.d/` 下的脚本。

通过向 `/etc/init.d/` 添加可执行脚本并实现 `start/stop/restart` 等逻辑，可以轻松创建自定义服务。

使用 `update-rc.d` 可以控制服务是否开机自启动，它会在各运行级别目录中创建符号链接。

现代 Ubuntu 推荐使用 systemd，但掌握传统服务管理仍有助于理解 Linux 服务的演进和兼容性。
