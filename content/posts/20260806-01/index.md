---
title: OpenCode 无法使用 Gemini 工具调用：从 one-api 迁移到 new-api 的完整排查与解决方案
date: '2026-08-06'
lastmod: '2026-08-06T02:42:10Z'
slug: 20260806-01
categories:
- 来点码吧
tags:
- opencode
- cline
- gemini
- one-api
- new-api
- docker
- 故障排查
draft: true
---

## 背景

在 opencode 中使用 oneAPI（JustSong 版 one-api v0.6.11-preview.7）提供的 `gemini-3.6-flash` 时出现诡异现象：

- 聊天窗口「没有内容或内容很少」，看起来像无法使用；
- 日志中频繁出现空消息错误：`AI_APICallError:  (request id: ...)`；
- 但纯问答（不涉及工具）能正常返回文本；
- 同一令牌在 Cline 中却工作正常。

排查的目标：**为什么 opencode/Cline 都可以，但只有 opencode 依赖的请求路径会失败？**

## 逐步排查

### 1. 先排除网络与令牌问题

直接对 oneAPI 的 OpenAI 兼容接口做压力测试（同 key、同端点）：

- 顺序、并发、大 payload（67KB）、`stream_options: { include_usage: true }` 全部成功；
- 结论：**oneAPI 侧暂时健康，问题不在网络/令牌/上游连通性**。

### 2. 用 opencode 的真实请求链路复现

opencode 走 Vercel AI SDK（`@ai-sdk/openai-compatible` + `ai`）。用同样的 SDK、相同 baseURL、相同 key 复现：

- **纯问答**：正常流出文本，解析无误；
- **带工具（agent 模式）**：模型只返回「工具调用」，`text len = 0`，**没有任何可见文字**——这是 Gemini 思考模型的行为：思考放到 `extra_content.google.thought_signature`，而 opencode 不渲染这段，于是看起来「一片空白」。

### 3. 抓到真正的凶手：工具续轮 400

用手动构造的多轮请求测试「把工具结果回传」的操作（`assistant.tool_calls` + `role: "tool"`）：

- 第一轮（触发工具调用）：HTTP 200；
- **第二轮（回传工具结果）：HTTP 400 → `bad_response_status_code`**，且错误体只有「空格 + request id」，message 为空。

这正对应 opencode 里那个**空消息的 `AI_APICallError`**。我又试了 7 种请求变体（`content:null`/`""`/数组、去掉 `tools`、去掉 `type` 等）**全部 400**——只要消息里带 `role: "tool"` 就必挂。

### 4. 根因定位

- 该 relay 的 Gemini 渠道 base_url 指向 Google 的 **OpenAI 兼容层** `https://generativelanguage.googleapis.com/v1beta/openai`；
- 而 **Google 官方 OpenAI 兼容层对 `tool` 角色的多轮续轮本身就有缺陷**（社区已知问题：tool_calls 缺 `index`、`thought_signature` 破坏工具流），返回 400；
- 同时 **JustSong 版 one-api 的原生 Gemini 工具调用也是损坏的**（官方 issue #915，长期无人修复）。

结论：**root cause 在 relay（oneAPI / one-api）对 Gemini 工具续轮的支持，而不是 opencode 或某个 agent。** 任何走 OpenAI 兼容格式、且会把工具结果以 `role:"tool"` 回传的客户端（opencode、zcode、基于 AI SDK/OpenAI SDK 的工具）只要打到同一 relay 的 Gemini 通道，都会撞 400。

## 解决方案：迁移到 new-api fork

`new-api`（QuantumNous/new-api，即 Calcium-Ion 的维护分支）修复了 Gemini function calling / `tool` 角色续轮 / `thought_signature` 等问题。迁移全程保持 one-api 目录不动，并行部署验证后切换。

### 环境

- 服务器上 docker-compose 部署，one-api 在 `~/docker/one-api`；
- 因网络问题用 sing-box 容器走代理出海；
- SQLite 单库 `data/one-api.db`。

### 步骤

1. **创建新目录并复制配置**：`~/docker/new-api/`，拷贝 `proxy_config.json`。
2. **安全备份数据库**：用 sqlite 在线备份 API（而不是直接 `cp`，避免文件锁/损坏）：
   ```python
   import sqlite3
   src = sqlite3.connect('<old>/data/one-api.db')
   dst = sqlite3.connect('<new>/data/one-api.db')
   src.backup(dst)   # integrity_check: ok，11 个渠道完整
   ```
3. **写 new-api compose**（独立 redis/proxy，测试端口先给 `4001`，正式切前端 `4000`），并加备份脚本 `backup.sh`。
4. **启动并修复两处配置**：
   - **自用模式**：new-api 强制要求模型定价，否则报 `模型价格未配置`。个人/内部使用直接开启自用模式（写入 `options` 表 `SelfUseModeEnabled=true`）；
   - **渠道类型错位**：one-api 与 new-api 的渠道 `type` 码不同，迁移后会错位（我遇到 type 51 被路由器当成「即梦/Jimeng」，key 被要求 `ak|sk` 格式导致 `invalid api key format for jimeng`）。修正：
     - Gemini 渠道 `type 51 → 24`，`base_url → https://generativelanguage.googleapis.com`（new-api 原生 Gemini 适配器用 `{base_url}/v1beta/models/{model}:generateContent` + `x-goog-api-key` 头）；
     - Ollama 渠道 `type 30 → 4`。
5. **验证工具续轮**（手动 `assistant.tool_calls` + `tool` 角色）：第一轮、第二轮均 **HTTP 200**，流式/非流式都通过，第二轮能正常返回最终文本。**400 已修复。**
6. **正式切换**：停 one-api 容器，new-api 接管 `4000` 端口（nginx `proxy_pass 127.0.0.1:4000` 无需改动）；公网 `https://api.sergget.qzz.io/v1/models` 返回 200，模型列表正常。
7. opencode 端把 provider 名从 `oneapi` 改为 `newapi`（同时把 `auth.json` 里对应 key 条目改名为 `newapi`，避免令牌失效）。

## 结论

- **一句话根因**：直连 Google OpenAI 兼容层做 Gemini，其 `tool` 角色多轮续接返回 400；而 JustSong one-api 原生 Gemini 工具调用同样残缺。换用 new-api 的**原生 Gemini 适配器 + 自用模式 + 修正渠道 type** 三者结合后彻底修复。
- **通用教训**：
  - 客户端“空白/报错”不一定在客户端；先按**同一个链路（同 SDK、同 key、同 baseURL）**复现，再用原始 HTTP 逐步拆解；
  - 换 gateway 时**渠道 type 码不一定兼容**，务必逐渠道核对；
  - 用 SQLite 迁移务必使用在线备份 API，避免直接复制损坏。

## 复现脚本（留档）

手动工具续轮测试脚本（可作日后回归）示例要素：

```python
# 第一轮：带 tools，模型返回 tool_call
# 第二轮：消息数组追加
#   {"role":"assistant","content":None,"tool_calls":[{...}]}
#   {"role":"tool","tool_call_id":id,"content":"<result>"}
# 第二轮不再 400，且能返回最终文字 => 修复生效
```