# Summary

## 备考指南
*   [README](README.md)

## 科目一：计算机与网络知识（基础知识）
*   [第1章：计算机系统知识](part1/1-computer-system.md)
    *   [1.1 硬件知识](part1/1.1-hardware.md)
        *   计算机组成（运算器、控制器、存储器、I/O部件）
        *   指令系统与处理器性能（含流水线技术）
        *   存储系统（主存、辅存、Cache、虚拟存储器、内存编址）
        *   I/O结构（中断、DMA、通道）
        *   可靠性基础
    *   [1.2 操作系统知识](part1/1.2-os.md)
        *   基本概念（进程与线程、内核）
        *   处理机管理（状态转换、调度算法）
        *   存储管理（分区、分页、分段、虚拟内存）
        *   设备管理与文件管理
    *   [1.3 系统配置与性能评价](part1/1.3-system-config.md)
        *   系统构架模式（C/S、B/S）
        *   RAID技术与高可用性
        *   性能与可靠性评估（含性能参数）

*   [第2章：系统开发与运行基础知识](part1/2-devops.md)
    *   需求分析与设计基础
    *   软件生命周期与开发模型
    *   测试与评审方法
    *   项目管理基础（PERT图、甘特图）
    *   系统维护知识

*   [第3章：网络技术（核心）](part1/3-network-tech.md)
    *   [3.1 数据通信基础](part1/3.1-datacom.md)
        *   信道特性与传输介质（双绞线、光纤）
        *   调制与编码（ASK/FSK/PSK、PCM）
        *   传输技术（多路复用、差错控制编码）
        *   网络性能参数（带宽、时延、吞吐量）
    *   [3.2 网络体系结构](part1/3.2-architecture.md)
        *   OSI/RM七层模型
        *   TCP/IP协议族（核心协议）
    *   [3.3 局域网技术](part1/3.3-lan.md)
        *   IEEE 802标准与以太网
        *   交换技术（VLAN、GVRP、STP/RSTP、链路聚合）
        *   无线局域网（WLAN）与802.11标准
        *   综合布线系统与传输介质
    *   [3.4 网络互连与因特网](part1/3.4-internet.md)
        *   网络层协议（IPv4/IPv6地址、ARP、ICMP）
        *   传输层协议（TCP、UDP）
        *   路由基础概念与路由器基本配置
        *   动态路由协议（RIP、OSPF、BGP）
        *   应用层协议（DNS、DHCP、HTTP/HTTPS、FTP、Telnet、电子邮件）
        *   QoS技术与网络新技术
    *   [3.5 网络操作系统与管理](part1/3.5-network-os.md)
        *   网络操作系统功能
        *   网络管理功能域（FCAPS）与SNMP协议
        *   Linux系统管理基础（常用命令、目录结构、配置文件）
        *   Windows网管命令

*   [第4章：网络安全](part1/4-security.md)
    *   [4.1 加密与认证技术](part1/4.1-crypto.md)
        *   加密算法（对称/非对称）
        *   密钥管理
        *   数字签名、报文摘要、PKI数字证书
        *   认证技术
    *   [4.2 攻击与防范](part1/4.2-attack.md)
        *   计算机病毒与网络攻击
        *   入侵检测/防御技术（IDS/IPS）
        *   WAF与漏洞扫描设备
    *   [4.3 安全协议与部署](part1/4.3-security-protocol.md)
        *   安全协议（SSL/TLS、IPsec）
        *   VPN技术
        *   防火墙技术
        *   网络安全设备部署
        *   等级保护制度

*   [第5章：标准化、信息化与知识产权](part1/5-standard.md)
    *   标准化组织与标准
    *   信息化战略与法律法规
    *   知识产权（著作权、商标权、专利权）
    *   网络安全法与信息安全法

*   [第6章：计算机专业英语](part1/6-english.md)
    *   本领域基本英语词汇
    *   技术短文阅读理解

## 科目二：网络系统设计与管理（应用技术）
*   [第7章：网络系统规划与设计](part2/7-network-design.md)
    *   [7.1 需求分析](part2/7.1-requirement.md)
        *   功能、性能、安全、管理需求
    *   [7.2 网络拓扑设计](part2/7.2-topology.md)
        *   三层模型（核心、汇聚、接入）
        *   冗余与高可用性设计
        *   通信规范分析与逻辑/物理设计
    *   [7.3 地址规划与设计](part2/7.3-addressing.md)
        *   IP地址规划（VLSM、CIDR）
        *   IPv6过渡技术
    *   [7.4 设备选型与布线](part2/7.4-device.md)
        *   设备选型与介质选择
        *   结构化布线系统
        *   POE供电与多出口链路负载策略

*   [第8章：网络设备配置与实现](part2/8-config.md)
    *   [8.1 交换机配置](part2/8.1-switch.md)
        *   VLAN划分与Trunk
        *   STP/RSTP配置
        *   链路聚合（Eth-Trunk）
        *   堆叠与级联技术
    *   [8.2 路由器配置](part2/8.2-router.md)
        *   静态路由与默认路由
        *   动态路由协议（RIP、OSPF、BGP）
        *   路由引入与策略路由
        *   VRRP配置
    *   [8.3 广域网与接入配置](part2/8.3-wan.md)
        *   HDLC、PPP与认证
        *   SONET/SDH、PON、xDSL、HFC
        *   数据交换类型
    *   [8.4 网络安全配置](part2/8.4-security-config.md)
        *   ACL访问控制列表
        *   NAT网络地址转换
        *   VPN配置（IPsec、L2TP）
        *   防火墙安全策略
        *   认证方式部署
    *   [8.5 服务器配置](part2/8.5-server.md)
        *   Windows Server基本配置
        *   Linux服务器基本配置
        *   Web、FTP、DNS、DHCP服务配置

*   [第9章：网络系统管理与维护](part2/9-management.md)
    *   网络监视与故障排查
        *   常用命令（ping、tracert、nslookup、netstat）
        *   抓包分析工具使用
    *   性能优化与日志分析
    *   备份与数据恢复策略
    *   [典型案例分析：故障排查流程](part2/9.1-troubleshooting.md)

*   [第10章：新技术与发展趋势](part2/10-new-tech.md)
    *   [SDN与网络虚拟化](part2/10.1-sdn.md)
    *   [云计算网络基础](part2/10.2-cloud.md)
    *   [物联网（IoT）通信协议](part2/10.3-iot.md)
    *   [5G核心网基础概念](part2/10.4-5g.md)

## 附录
*   [历年真题考点分布](appendix/past-exam.md)
*   [配置命令速查表](appendix/command-quickref.md)
*   [子网划分计算器/练习](appendix/subnet-exercise.md)
*   [缩写表](ABBREVIATIONS.md)