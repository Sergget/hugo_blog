# 7.3 ifconfig与ip命令详解

## 7.3.1 引言
ifconfig 是传统的网络接口配置工具，属于 net-tools 包，自 Linux ## 7.3.2 内核后已停止维护。现代 Linux 系统推荐使用 ip 命令（来自 iproute2 包），它功能更全面，输出更清晰。

本文会同时介绍两者，但重点放在 ip 命令上，并给出对照关系。

## 7.3.2 ifconfig 常用操作
查看网络接口信息
```bash
ifconfig                 # 查看所有已启用的接口
ifconfig -a              # 查看所有接口（包括禁用）
ifconfig enp1s0          # 查看指定接口
ifconfig -s              # 以缩略形式显示
```
输出示例解读（以 enp1s0 为例）：

```text
enp1s0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.1.4  netmask 255.255.255.0  broadcast 192.168.1.255
        inet6 fe80::2e0:4cff:fe68:d4c  prefixlen 64  scopeid 0x20<link>
        ether 00:e0:4c:68:0d:4c  txqueuelen 1000  (Ethernet)
        RX packets 6137  bytes 1344568 (1.3 MB)
        RX errors 0  dropped 154  overruns 0  frame 0
        TX packets 7164  bytes 942487 (942.4 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```
- UP：接口已启用；RUNNING：网线已连接；MULTICAST：支持组播。
- inet：IPv4 地址、子网掩码、广播地址。
- inet6：IPv6 地址。
- ether：MAC 地址。
- RX/TX：接收/发送的数据包统计。

临时配置接口
```bash
# 启用/禁用接口
sudo ifconfig enp1s0 up
sudo ifconfig enp1s0 down

# 临时设置 IP 地址（重启失效）
sudo ifconfig enp1s0 192.168.1.10 netmask 255.255.255.0

# 同时设置 MTU
sudo ifconfig enp1s0 192.168.1.10 netmask 255.255.255.0 mtu 1400

# 修改 MAC 地址（需先禁用接口）
sudo ifconfig enp1s0 down
sudo ifconfig enp1s0 hw ether 00:11:22:33:44:55
sudo ifconfig enp1s0 up
```
⚠️ `ifconfig` 的 man 手册非常详细，可通过 `man ifconfig` 查阅所有选项，但日常使用以上命令已足够。

## 7.3.3 ip 命令详解
ip 命令功能强大，它使用对象（object）来管理不同网络组件。最常用的对象有：

- link：网络设备（如网卡）
- addr：协议地址（IP）
- route：路由表

查看信息
```bash
ip link show                 # 查看所有网络接口状态（相当于 ifconfig -a）
ip link show enp1s0          # 查看指定接口
ip addr show                 # 查看 IP 地址（相当于 ifconfig）
ip addr show enp1s0
ip route show                # 查看路由表（相当于 route -n）
```
启用/禁用接口
```bash
sudo ip link set enp1s0 up
sudo ip link set enp1s0 down
```
管理 IP 地址
```bash
# 添加临时 IP（相当于 ifconfig 设置）
sudo ip addr add 192.168.1.10/24 dev enp1s0

# 删除 IP
sudo ip addr del 192.168.1.10/24 dev enp1s0

# 刷新接口（DHCP 重获地址）
sudo ip addr flush dev enp1s0
```
管理路由
```bash
# 添加默认网关
sudo ip route add default via 192.168.1.1 dev enp1s0

# 删除路由
sudo ip route del default
```
修改 MAC 地址
```bash
sudo ip link set dev enp1s0 address 00:11:22:33:44:55
```
查看统计信息
```bash
ip -s link show enp1s0        # 显示接口统计（类似 ifconfig 的 RX/TX）
```
## 7.3.4 ifconfig 与 ip 命令对比
|操作|ifconfig 命令|ip 命令|
|-|-|-|
|查看所有接口|ifconfig 或 ifconfig -a|ip addr show 或 ip link show|
|查看指定接口|ifconfig eth0|ip addr show eth0|
|启用接口|ifconfig eth0 up|ip link set eth0 up|
|禁用接口|ifconfig eth0 down|ip link set eth0 down|
|设置 IP 地址|ifconfig eth0 192.168.1.2/24|ip addr add 192.168.1.2/24 dev eth0|
|删除 IP 地址|（无直接命令，可设 0.0.0.0 清除）|ip addr del 192.168.1.2/24 dev eth0|
|设置 MAC 地址|ifconfig eth0 hw ether 00:...|ip link set dev eth0 address 00:...|
|查看路由表|route -n|ip route show|
|添加默认网关|route add default gw 192.168.1.1|ip route add default via 192.168.1.1|
## 7.3.5 小结
- 查看网络信息：两者皆可，但 ip 输出更规范，推荐使用。
- 临时修改：ip 命令语法更统一，功能更全面，应优先掌握。
- 持久化配置：不要依赖 ifconfig 或 ip 的临时修改，需使用 netplan 写入配置文件。