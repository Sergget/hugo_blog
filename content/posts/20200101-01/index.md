---
categories:
- 来点码吧
date: 2020-01-01
draft: false
slug: 20200101-01
tags: []
title: Git 配置指南
---

* * *

## 安装

```
sudo apt-get install git git-core
```

## 初始配置

- 用户信息 配置个人的用户名称和电子邮件地址：

```
$ git config –global user.name “runoob”
$ git config –global user.email test@runoob.com
```

- 文本编辑器

```
$ git config –global core.editor vim
```

- 差异分析工具

```
$ git config –global merge.tool vimdiff
```

- 检查已有的配置信息

```
git config –list
```

## 命令

### git diff

执行 git diff 来查看执行 git status 的结果的详细信息。git diff 命令显示已写入缓存与已修改但尚未写入缓存的改动的区别。

- 尚未缓存的改动：git diff

- 查看已缓存的改动： git diff –cached

- 查看已缓存的与未缓存的所有改动：git diff HEAD

- 显示摘要而非整个 diff：git diff –stat

### Git log 查看提交历史

在使用 Git 提交了若干更新之后，又或者克隆了某个项目，想回顾下提交历史，我们可以使用 git log 命令查看。  
针对我们前一章节的操作，使用 git log 命令列出历史提交记录如下：

```
$ git log
```

**_参数：_**

- `--oneline`选项来查看历史记录的简洁的版本。

```
$ git log –oneline
```

- `--graph` 选项，查看历史中什么时候出现了分支、合并。以下为相同的命令，开启了拓扑图选项：

```
$ git log –oneline –graph
```

- `--reverse`参数来逆向显示所有日志。

```
$ git log –reverse –oneline
```

查找指定用户的提交日志可以使用命令：`git log --author` , 例如，比方说我们要找 Git 源码中 Linus 提交的部分：

```
$ git log –author=Linus –oneline -5
```

如果你要指定日期，可以执行几个选项：–since 和 –before，但是你也可以用 –until 和 –after。  
例如，如果我要看 Git 项目中三周前且在四月十八日之后的所有提交，我可以执行这个（我还用了 –no-merges 选项以隐藏合并提交）：

```
$ git log –oneline –before={3.weeks.ago} –after={2010-04-18} –no-merges
```

### Git tag 标签

如果你达到一个重要的阶段，并希望永远记住那个特别的提交快照，你可以使用 git tag 给它打上标签。

比如说，我们想为我们的 w3cschoolcc 项目发布一个”1.0″版本：

```
$ git tag -a v1.0
```

选项：

- \-a 选项意为”创建一个带注解的标签”。不用 -a 选项也可以执行的，但它不会记录这标签是什么时候打的，谁打的，也不会让你添加个标签的注解。

#### 追加标签

如果我们忘了给某个提交打标签，又将它发布了，我们可以给它追加标签。例如，假设我们发布了提交 85fc7e7，但是那时候忘了给它打标签。 我们现在也可以：

```
$ git tag -a v0.9 85fc7e7
```

#### 指定标签信息命令：

```
git tag -a -m “w3cschool.cc标签”
```

#### PGP签名标签命令：

```
git tag -s -m “w3cschool.cc标签”
```

### Git 远程仓库(Github)

#### 添加远程库

```
git remote add [shortname] [url]
```

由于本地Git仓库和GitHub仓库之间的传输是通过SSH加密的，所以我们需要配置验证信息：  
使用以下命令生成SSH Key：

```
$ ssh-keygen -t rsa -C “youremail@example.com”
```

成功的话会在~/下生成.ssh文件夹，进去，打开 id\_rsa.pub，复制里面的 key。  
回到 github 上，进入 Account => Settings（账户配置）。

左边选择 SSH and GPG keys，然后点击 New SSH key 按钮,title 设置标题，可以随便填，粘贴在你电脑上生成的 key。

- 查看当前的远程库

```
git remote
```

- 配置上游分支

```
git push –set-upstream [repo] [branch]
```

- 提取远程仓库

1. 从远程仓库下载新分支与数据：

```
git fetch
```

该命令执行完后需要执行git merge 远程分支到你所在的分支。

2.从远端仓库提取数据并尝试合并到当前分支：

```
git pull
```

#### 推送到远程仓库

推送你的新分支与数据到某个远端仓库命令:

```
git push [alias] [branch]
```

#### 删除远程仓库

删除远程仓库你可以使用命令：

```
git remote rm [别名]
```