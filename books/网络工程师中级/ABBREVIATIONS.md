# 缩写表

按文档来源与在文档中出现的顺序列出。每行格式：缩写 | 英文全称 | 中文名 | 简要说明。

---

## 来源：[1.1 硬件知识](part1/1.1-hardware.md)

| 缩写 | 英文全称 | 中文名 | 简要说明 |
|---|---|---|---|
| PC | Program Counter | 程序计数器 | 存储下一条指令地址的寄存器 |
| IR | Instruction Register | 指令寄存器 | 存放当前正在执行的指令内容 |
| AC | Accumulator | 累加寄存器 | 暂存算术/逻辑运算的操作数或结果 |
| PSW | Program Status Word | 程序状态字/状态寄存器 | 存放运算产生的标志位（进位、溢出等） |
| DMA | Direct Memory Access | 直接内存存取 | 允许设备直接与内存交换数据，减轻 CPU 负担 |
| CRC | Cyclic Redundancy Check | 循环冗余校验 | 基于多项式的检错方法，常用于链路层 |

---

## 来源：[3.2 网络体系结构](part1/3.2-architecture.md)

| 缩写 | 英文全称 | 中文名 | 简要说明 |
|---|---|---|---|
| OSI | Open Systems Interconnection | 开放系统互连模型 | 七层网络参考模型，用于说明网络功能分层 |
| TCP/IP | Transmission Control Protocol/Internet Protocol | 传输控制协议/网际协议族 | 互联网使用的协议族，包含 TCP、IP 等 |
| TCP | Transmission Control Protocol | 传输控制协议 | 面向连接、可靠的传输层协议 |
| IP | Internet Protocol | 网际协议 | 负责分组寻址与路由的网络层协议 |
| ICMP | Internet Control Message Protocol | 因特网控制报文协议 | 用于网络设备间差错与诊断（如 ping） |
| OSPF | Open Shortest Path First | 开放最短路径优先协议 | 一种链路状态路由协议，属于网络层协议，用于在路由器之间动态选择最优路径。 |
| RIP | Routing Information Protocol | 路由信息协议 | 一种距离向量路由协议 |
| BGP | Border Gateway Protocol | 边界网关协议 | 用于自治系统间路由选择的协议 |
| UDP | User Datagram Protocol | 用户数据报协议 | 无连接、不保证可靠性的传输层协议 |
| ARP | Address Resolution Protocol | 地址解析协议 | 将 IP 地址映射为 MAC 地址，工作在二层/三层交界处 |
| VLAN | Virtual LAN | 虚拟局域网 | 在二层划分逻辑广播域的技术 |
| STP | Spanning Tree Protocol | 生成树协议 | 防止二层环路的协议 |
| SSL | Secure Sockets Layer | 安全套接字层 | 用于加密的协议（已由 TLS 取代） |
| HTTP | HyperText Transfer Protocol | 超文本传输协议 | Web 应用层协议 |
| FTP | File Transfer Protocol | 文件传输协议 | 用于文件上传/下载的应用层协议 |
| DNS | Domain Name System | 域名系统 | 将域名解析为 IP 地址的系统与协议 |
| SMTP | Simple Mail Transfer Protocol | 简单邮件传输协议 | 用于电子邮件发送的应用层协议 |
| MAC | Media Access Control | 媒体访问控制地址 | 数据链路层的硬件地址（物理地址） |
| RJ45 | Registered Jack 45 | RJ45 接口 | 常见以太网物理接口类型 |
| SYN | Synchronize (flag) | 同步标志 | TCP 三次握手中的同步报文标志 |
| ACK | Acknowledgement | 确认标志 | TCP 报文中的确认位 |

---

## 来源：`README.md` / `SUMMARY.md`（常见术语与工具）

| 缩写 | 英文全称 | 中文名 | 简要说明 |
|---|---|---|---|
| eNSP | (Huawei) eNSP | 华为仿真器 | 华为网络设备模拟器与实验平台 |
| Packet Tracer | Cisco Packet Tracer | 思科仿真器 | 网络拓扑与设备配置模拟工具 |
| Wireshark | Wireshark | 抓包工具 | 网络协议分析与抓包工具 |
| VMware | VMware | 虚拟化平台 | 常用虚拟机软件 |
| RAID | Redundant Array of Independent Disks | 冗余磁盘阵列 | 提供冗余与性能的磁盘组织方式 |
| FCAPS | Fault/Configuration/Accounting/Performance/Security | FCAPS 管理域 | 网络管理的五大功能域 |
| SNMP | Simple Network Management Protocol | 简单网络管理协议 | 用于设备监控与管理的协议 |
| IDS/IPS | Intrusion Detection/Prevention System | 入侵检测/防御系统 | 检测/阻止网络入侵的安全设备 |
| WAF | Web Application Firewall | Web 应用防火墙 | 针对 Web 应用层攻击的防护设备 |
| TLS | Transport Layer Security | 传输层安全协议 | SSL 的继任者，提供加密与认证 |
| IPsec | Internet Protocol Security | IP 层安全协议 | 为 IP 数据流提供加密与认证 |
| DHCP | Dynamic Host Configuration Protocol | 动态主机配置协议 | 自动分配 IP 等配置信息 |
| VLSM | Variable Length Subnet Mask | 可变长子网掩码 | 灵活的子网划分方法 |
| CIDR | Classless Inter-Domain Routing | 无类域间路由 | 更灵活的地址分配与路由聚合 |
| IPv4/IPv6 | Internet Protocol v4 / v6 | 第4/6版网际协议 | 不同版本的 IP 协议，地址长度不同 |
| VRRP | Virtual Router Redundancy Protocol | 虚拟路由冗余协议 | 实现路由器冗余与热切换 |
| HDLC | High-Level Data Link Control | 高级数据链路控制 | 面向比特的点对点链路协议 |
| PPP | Point-to-Point Protocol | 点对点协议 | 用于点对点链路的链路层协议 |
| SONET/SDH | Synchronous Optical Network / Synchronous Digital Hierarchy | 同步光网 / 同步数字体系 | 光纤传输网的标准体系 |
| PON | Passive Optical Network | 无源光网络 | 光纤接入的一种实现方式 |
| xDSL | Digital Subscriber Line (various) | 各类数字用户线技术 | 家庭和商用宽带接入技术总称 |
| HFC | Hybrid Fiber-Coax | 光纤同轴混合网 | 有线宽带常见网络结构 |
| ACL | Access Control List | 访问控制列表 | 用于过滤流量的规则集合 |
| NAT | Network Address Translation | 网络地址转换 | 将私有地址映射为公网地址的技术 |
| L2TP | Layer 2 Tunneling Protocol | 第二层隧道协议 | VPN 中常见的隧道协议之一 |
| SDN | Software Defined Networking | 软件定义网络 | 控制面与转发面分离的网络架构 |
| IoT | Internet of Things | 物联网 | 互联设备与传感器构成的网络体系 |
| QoS | Quality of Service | 服务质量 | 保证流量优先级与带宽分配的机制 |

---

> 说明：本表以当前仓库根目录中标题列出的文档为来源并按出现顺序摘取缩写；若同一缩写在不同文档重复出现，则以各文档独立列出，以便追溯出处。
