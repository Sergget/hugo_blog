---
categories:
- 会用电脑
date: 2020-02-05
draft: false
slug: 20200205-01
tags: []
title: 抛弃迅雷，投入BT的怀抱吧
---

* * *

由于最近的特殊情况，不得不宅在家中（其实没这档子事儿我也乐意待家里），于是乎就下载了大量的电影，迅雷加速基本和百度网盘一个性质，本人都没有购买会员，通过bt种子或磁力链接进行下载。并且可以跑满带宽上限。下面就分享下：

## 客户端

我是用的客户端是比特彗星[bitcomet](http://www.bitcomet.com/)，所谓的登录和上传升级加速之类的都是扯淡，实际当中考虑到这些bt客户端往往都有防吸血的功能，因此，上传的限速不要太过分就可以了。

也可以考虑使用uTorrent客户端或者uTorrent web。

## 添加Tracker

### Tracker是什么？

我们知道BT下载或者磁力下载是一种去中心化的网络内容分发的机制，每个人既是下载的，也是上传的，没人做种，也就没法下载。做种的人越多，你下载的速度就能越快，但是这并不是完全意义上的去中心化，因为你不知道有谁在做种。

因此我们需要中心化的服务器，来将大家上传和下载的请求信息进行交换，然后各个客户端各自进行连接交换数据。

### 为什么添加Tracker?

简单地说， **优质的 Tracker，可以有效提高资源解析速度及下载速度。** **同时，用这些 Tracker 的人越多，大家的下载速度就越快**。

### 向比特彗星添加Tracker

点击[链接](http://www.bitcomet.com/en/downloads)下载比特彗星，安装完成后，可能是默认为英语，选择工具栏的Tools => Language => Chinese

更改语言后，添加Tracker服务器的订阅链接。Github的XIU2汇总了一些优质的Tracker列表:

- 项目地址： [https://github.com/XIU2/TrackersListCollection](https://github.com/XIU2/TrackersListCollection)

- 项目网站： [https://trackerslist.com/#/zh](https://trackerslist.com/#/zh)

项目提供了两个订阅列表：

- 精选版： [https://trackerslist.com/best.txt](https://trackerslist.com/best.txt)

- 完整版： [https://trackerslist.com/all.txt](https://trackerslist.com/all.txt)

请选择上面任意一个链接，复制。打开比特彗星 => 工具 => 人物设置 => Tracker => 勾选”每天自动更新Tracker服务器列表”，然后在下面的输入框内粘贴刚才复制的订阅列表，点击立即更新，确定即可。