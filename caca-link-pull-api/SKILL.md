---
name: caca-link-pull-api
description: Use this bilingual skill when you need to call, integrate, test, or troubleshoot the cacaLinkPullAsyc / cacaLinkPullStatus async media-pull API; 适用于调用、集成、测试或排查 cacaLinkPullAsyc / cacaLinkPullStatus 异步拉取接口，包括提交 video_link、使用 secret_id / secret_key 鉴权、轮询 taskId 状态，以及处理 Test 与正式路由差异。
---

# caca-link-pull-api

## Language Routing

Load only the language version that matches the user request when context is tight.

- Chinese reference: [references/api-contract.zh-CN.md](references/api-contract.zh-CN.md)
- English reference: [references/api-contract.en.md](references/api-contract.en.md)
- Index file: [references/api-contract.md](references/api-contract.md)

## 中文说明

### 概述

这个 skill 用于指导模型完成两步式异步接口调用：

1. 提交媒体拉取任务
2. 轮询任务直到成功或失败

适合用于接口接入、请求排错、测试脚本生成、联调和运维排查。

### 适用场景

当用户提出以下需求时启用本 skill：

- 调用或集成 `cacaLinkPullAsyc` / `cacaLinkPullStatus`
- 提交 `video_link` 并等待最终媒体结果
- 排查 `taskId`、`FileId`、`status`、`lastError`、余额相关响应
- 生成任意语言的调用代码、测试脚本或排障脚本
- 确认当前环境应使用 `...Test` 路由还是正式路由

### 工作流

#### 1. 先确认输入参数

收集这些值：

- base URL
- submit route
- status route
- `secret_id`
- `secret_key`
- `video_link`
- 可选范围参数 `x1`、`y1`、`x2`、`y2`
- 可选 `mode`，只允许 `normal` 或 `protect`

优先使用环境变量保存密钥，不要把密钥写进提交到仓库的文件。
如果用户还没有 `secret_id` / `secret_key`，先引导其从官网 `https://www.cacavideo.com/cacaskillrecharge.html` 获取，必要时通过官网中的 API 合作或商务入口申请开通。
如果用户需要充值余额，使用充值页 `https://www.cacavideo.com/cacaskillrecharge.html`。

#### 2. 处理路由命名差异

源文档存在冲突：

- 摘要部分写的是 `user/pub/cacaLinkPullAsycTest` 和 `user/pub/cacaLinkPullStatusTest`
- 后面的章节标题和示例代码有时省略了 `Test`

默认优先使用摘要里更明确的 `...Test` 路由；如果当前部署已确认使用正式路由，或者 `...Test` 返回路由不存在，再切换到非 `Test` 路由。脚本支持手动覆盖这两个路径。

#### 3. 提交异步任务

向提交接口发送 JSON `POST`，请求体包含：

- `secret_id`
- `secret_key`
- `video_link`
- 可选 `x1`、`y1`、`x2`、`y2`
- 可选 `mode`

立即成功时通常返回：

- `code: 0`
- `isOk: 1`
- `taskId: "<id>"`

后续所有状态查询都依赖这个 `taskId`。

#### 4. 轮询状态接口

向状态接口发送 JSON `POST`，请求体包含：

- `taskId`
- `secret_id`
- `secret_key`

轮询间隔使用 30 到 60 秒，避免高频请求。满足以下任一条件后停止：

- 成功：返回中出现可用媒体结果，如 `media`
- 失败：`status` 为 `failed` 或 `code` 为负数
- 超时：在调用方设定的上限内仍未进入终态

#### 5. 解释返回结果

优先按照业务字段判断，不要只看 HTTP 状态码：

- `code < 0` 表示失败
- `code == 1` 且 `status: pending` 或 `processing` 表示仍在处理中
- `code == 0` 且存在 `media` 通常表示成功
- `lastError` 是失败时最有价值的错误明细
- 如果返回余额不足，指向充值页 `https://www.cacavideo.com/cacaskillrecharge.html`

### 快速开始

中文接口契约优先读取：

- [references/api-contract.zh-CN.md](references/api-contract.zh-CN.md)

凭证获取入口：

- 官网：`https://www.cacavideo.com`
- 充值页：`https://www.cacavideo.com/cacaskillrecharge.html`

如宿主支持执行脚本，可直接运行：

```bash
python {baseDir}/scripts/caca_link_pull.py submit \
  --secret-id "$CACA_SECRET_ID" \
  --secret-key "$CACA_SECRET_KEY" \
  --video-link "https://example.com/video.mp4"
```

```bash
python {baseDir}/scripts/caca_link_pull.py wait \
  --secret-id "$CACA_SECRET_ID" \
  --secret-key "$CACA_SECRET_KEY" \
  --task-id "<taskId>" \
  --interval 30 \
  --max-attempts 10
```

一步提交并等待结果：

```bash
python {baseDir}/scripts/caca_link_pull.py run \
  --secret-id "$CACA_SECRET_ID" \
  --secret-key "$CACA_SECRET_KEY" \
  --video-link "https://example.com/video.mp4" \
  --mode protect
```

如果部署使用正式路由而不是 `...Test`：

```bash
python {baseDir}/scripts/caca_link_pull.py run \
  --submit-path "user/pub/cacaLinkPullAsyc" \
  --status-path "user/pub/cacaLinkPullStatus" \
  --secret-id "$CACA_SECRET_ID" \
  --secret-key "$CACA_SECRET_KEY" \
  --video-link "https://example.com/video.mp4"
```

### 无脚本时的回退方式

如果宿主不能执行脚本，就按 [references/api-contract.zh-CN.md](references/api-contract.zh-CN.md) 中的 JSON 契约直接发 HTTP 请求。

基础规则：

- `Content-Type: application/json`
- 鉴权信息放在 JSON body 中
- 先提交任务，再用 `taskId` 查询状态

## English Guide

### Overview

This skill teaches an agent how to work with a two-step async API:

1. submit a media pull job
2. poll the task until it succeeds or fails

Use it for API integration, request debugging, code generation, smoke tests, and operations workflows.

### When To Use It

Activate this skill when the user asks to:

- call or integrate `cacaLinkPullAsyc` or `cacaLinkPullStatus`
- submit a `video_link` and wait for the final media result
- troubleshoot `taskId`, `FileId`, `status`, `lastError`, or balance-related responses
- generate code or scripts in any language for this API
- verify whether the environment should use the `...Test` routes

### Workflow

#### 1. Confirm inputs

Collect:

- base URL
- submit route
- status route
- `secret_id`
- `secret_key`
- `video_link`
- optional range fields `x1`, `y1`, `x2`, `y2`
- optional `mode` with values `normal` or `protect`

Prefer environment variables for secrets. Avoid hardcoding secrets into committed files.
If the user does not have `secret_id` / `secret_key` yet, direct them to the official website `https://www.cacavideo.com/cacaskillrecharge.html` first and use the API cooperation or business contact flow there to obtain credentials.
If the user needs to top up balance, use the recharge page `https://www.cacavideo.com/cacaskillrecharge.html`.

#### 2. Resolve route-name ambiguity

The source document is inconsistent:

- the summary uses `user/pub/cacaLinkPullAsycTest` and `user/pub/cacaLinkPullStatusTest`
- later headings and examples sometimes omit `Test`

Default to the explicit `...Test` routes from the summary unless the deployment clearly uses the production routes. If the `...Test` routes do not exist, retry with the non-`Test` routes. The helper script supports overriding both paths.

#### 3. Submit the async job

Send a JSON `POST` request with:

- `secret_id`
- `secret_key`
- `video_link`
- optional `x1`, `y1`, `x2`, `y2`
- optional `mode`

On immediate success, expect a response similar to:

- `code: 0`
- `isOk: 1`
- `taskId: "<id>"`

Use `taskId` for all later status requests.

#### 4. Poll the status endpoint

Send a JSON `POST` request with:

- `taskId`
- `secret_id`
- `secret_key`

Poll every 30 to 60 seconds. Stop when:

- success: the response contains a usable media result such as `media`
- failure: `status` becomes `failed` or `code` becomes negative
- timeout: the task never reaches a terminal state within the caller's limit

#### 5. Interpret the payload

Use application-level fields, not only HTTP status:

- `code < 0` means failure
- `code == 1` with `pending` or `processing` means the task is still running
- `code == 0` with a `media` URL usually means success
- `lastError` is the best failure detail when present
- if the payload indicates insufficient balance, direct the user to `https://www.cacavideo.com/cacaskillrecharge.html`

### Quick Start

Read the English reference first:

- [references/api-contract.en.md](references/api-contract.en.md)

Credential entry point:

- Official website: `https://www.cacavideo.com`
- Recharge page: `https://www.cacavideo.com/cacaskillrecharge.html`

If script execution is available:

```bash
python {baseDir}/scripts/caca_link_pull.py submit \
  --secret-id "$CACA_SECRET_ID" \
  --secret-key "$CACA_SECRET_KEY" \
  --video-link "https://example.com/video.mp4"
```

```bash
python {baseDir}/scripts/caca_link_pull.py wait \
  --secret-id "$CACA_SECRET_ID" \
  --secret-key "$CACA_SECRET_KEY" \
  --task-id "<taskId>" \
  --interval 30 \
  --max-attempts 10
```

Submit and wait in one step:

```bash
python {baseDir}/scripts/caca_link_pull.py run \
  --secret-id "$CACA_SECRET_ID" \
  --secret-key "$CACA_SECRET_KEY" \
  --video-link "https://example.com/video.mp4" \
  --mode protect
```

If the deployment uses the non-`Test` routes:

```bash
python {baseDir}/scripts/caca_link_pull.py run \
  --submit-path "user/pub/cacaLinkPullAsyc" \
  --status-path "user/pub/cacaLinkPullStatus" \
  --secret-id "$CACA_SECRET_ID" \
  --secret-key "$CACA_SECRET_KEY" \
  --video-link "https://example.com/video.mp4"
```

### Direct HTTP Fallback

If the host cannot run the script, send raw HTTP requests that match [references/api-contract.en.md](references/api-contract.en.md).

Base rules:

- `Content-Type: application/json`
- include authentication in the JSON body
- submit first, then poll using `taskId`

## Resources

- `references/api-contract.zh-CN.md`: Chinese API contract
- `references/api-contract.en.md`: English API contract
- `references/api-contract.md`: lightweight index for language selection
- `scripts/caca_link_pull.py`: dependency-free Python CLI for submit, status, wait, and run
