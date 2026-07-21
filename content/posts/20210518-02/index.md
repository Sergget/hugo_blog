---
categories:
- 会用电脑
date: 2021-05-18
draft: false
slug: 20210518-02
tags: []
title: 硬盘自检工具-smartctl的使用
---

## 1\. 简介

smartctl是Linux系统中常用的磁盘健康检查工具，基于SMART（Self-Monitoring, Analysis and Reporting Technology）技术。SMART是一种现代硬盘普遍支持的自我监测、分析和报告技术，能够提前预警磁盘可能发生的故障。

smartmontools软件包包含两个主要工具：

- smartctl：命令行工具，用于控制和监控存储设备

- smartd：守护进程，用于自动监控和报告磁盘状态

## 2\. 安装

Ubuntu/Debian系统

```
$ sudo apt-get install smartmontools
```

CentOS/RHEL系统

```
$ yum install smartmontools
# 或对于较新版本
$ dnf install smartmontools
```

启动服务

```
# Ubuntu/Debian
$ sudo systemctl start smartmontools
$ sudo systemctl enable smartmontools

# CentOS/RHEL
$ sudo systemctl start smartd
$ sudo systemctl enable smartd
```

## 3\. 基本使用

### 3.1 检查磁盘是否支持SMART

```
$ sudo smartctl -i /dev/sda
```

关键查看最后两行输出：

```
SMART support is: Available - device has SMART capability.
SMART support is: Enabled
```

### 3.2 启用SMART支持（如未开启）

```
$ sudo smartctl --smart=on --offlineauto=on --saveauto=on /dev/sda
```

参数说明：

- \--smart=on：启用SMART功能

- \--offlineauto=on：启用自动离线测试

- \--saveauto=on：启用属性自动保存

### 3.3 检查磁盘健康状况

```
$ sudo smartctl -H /dev/sda
```

健康状态显示为"PASSED"表示正常，"FAILED"表示磁盘可能出现问题。

### 3.4 查看详细SMART信息

```
$ sudo smartctl -a /dev/sda
# 或仅显示属性表
$ sudo smartctl -A /dev/sda
```

## 4\. SMART属性详解

SMART属性表包含以下重要列：

| 列名 | 说明 |
| --- | --- |
| ID | 属性ID，1-255之间的数字 |
| ATTRIBUTE\_NAME | 制造商定义的属性名称 |
| VALUE | 标准化值（1-253），值越高越好 |
| WORST | 历史最低值 |
| THRESH | 故障阈值 |
| TYPE | 属性类型（Pre-fail关键属性/Old\_age非关键属性） |
| WHEN\_FAILED | 故障状态指示 |
| RAW\_VALUE | 原始数值 |

重点关注属性：

- 5 Reallocated\_Sector\_Ct：重映射扇区计数

- 197 Current\_Pending\_Sector：当前待处理扇区数

- 198 Offline\_Uncorrectable：离线无法校正扇区数

## 5\. 磁盘测试

### 5.1 短期测试（约2分钟）

```
$ sudo smartctl -t short /dev/sda
```

### 5.2 长期测试（全面扫描，时间较长）

```
$ sudo smartctl -t long /dev/sda
```

### 5.3 查看测试进度和结果

```
$ sudo smartctl -l selftest /dev/sda
```

### 5.4 中止测试

```
$ sudo smartctl -X /dev/sda
```

## 6\. 高级功能

### 6.1 查看错误日志

```
$ sudo smartctl -l error /dev/sda
```

### 6.2 查看测试时间估算

```
$ sudo smartctl -c /dev/sda
```

### 6.3 自动监控配置

编辑/etc/smartd.conf配置文件：

```
DEVICESCAN -a -o on -S on -s (S/../.././02|L/../../6/03) -m admin@example.com
```

参数说明：

- \-a：监控所有属性

- \-o on：开启自动离线测试

- \-S on：开启属性自动保存

- \-s：定期测试计划

- \-m：发送邮件通知

## 7\. 实际应用建议

### 7.1 定期检查计划

建议将以下命令加入crontab定期执行：

```
# 每周执行一次短期测试
0 2 * * 0 /usr/sbin/smartctl -t short` /dev/sda

# 每月执行一次长期测试
0 3 1 * * /usr/sbin/smartctl -t long /dev/sda
```

### 7.2 故障预警指标

当出现以下情况时应立即备份数据：

- 健康检查结果为"FAILED"

- 任何Pre-fail属性显示"FAILING\_NOW"

- Reallocated\_Sector\_Ct值持续增加

- 出现大量待处理扇区

### 7.3 注意事项

- RAID阵列中的磁盘可能需要特殊参数（如-d megaraid,N）

- USB外接磁盘的SMART支持可能有限

- 虚拟机中的磁盘可能无法使用SMART功能

## 8\. 总结

smartctl是Linux系统管理员必备的磁盘健康监测工具，通过定期监控可以提前发现磁盘潜在问题，避免数据丢失。结合smartd守护进程，可以实现自动化监控和报警，为系统稳定性提供重要保障。