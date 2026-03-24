# caca-link-pull-api 接口契约

## 概述

本文档将源 Markdown 整理为更适合模型读取的中文接口契约，适用于异步媒体拉取流程。

## Base URL

源文档中的默认路由前缀：

`https://env-00jxh2cj3gfd.dev-hz.cloudbasefunction.cn/http/router/`

## 路由差异

源文档出现了两组不同的路径：

- 摘要部分：`user/pub/cacaLinkPullAsycTest` 和 `user/pub/cacaLinkPullStatusTest`
- 正文标题和代码示例：`user/pub/cacaLinkPullAsyc` 和 `user/pub/cacaLinkPullStatus`

推荐处理规则：

1. 未确认部署差异时，优先使用更明确的 `...Test` 路由。
2. 如果 `...Test` 路由不存在，再切换到非 `Test` 路由重试。
3. 生成代码和脚本时，始终把这两个路径设计成可配置参数。

## 鉴权

两个接口都要求在 JSON body 中携带：

- `secret_id` 字符串
- `secret_key` 字符串

源文档说明这与现有系统保持一致。
如果调用方尚未拿到凭证，先从官网 `https://www.cacavideo.com/cacaskillrecharge.html 进入，再通过 API 合作或商务入口申请 `secret_id` / `secret_key`。
如需充值或补充余额，使用充值页 `https://www.cacavideo.com/cacaskillrecharge.html`。该页面支持输入 `Secret ID` 充值，也提供生成新密钥入口。

## 提交接口

请求方法：`POST`

首选路径：

`user/pub/cacaLinkPullAsycTest`

备选路径：

`user/pub/cacaLinkPullAsyc`

### 请求体

- `secret_id` 字符串，必填
- `secret_key` 字符串，必填
- `video_link` 字符串，必填
- `x1` 数值，可选，默认 `0`
- `y1` 数值，可选，默认 `0`
- `x2` 数值，可选，默认 `0`
- `y2` 数值，可选，默认 `0`
- `mode` 字符串，可选，默认 `"normal"`

`mode` 可选值：

- `normal`
- `protect`

### 立即返回成功时的典型结构

常见字段：

- `code: 0`
- `msg: "任务已创建，后台处理中"`
- `isOk: 1`
- `taskId`
- `FileId: ""`
- `resultName: ""`
- `rem_time`
- `range`

### 立即返回失败示例

余额不足示例：

- `code: -1`
- `isOk: 0`
- `msg: "余额不足，请充值"`

出现余额不足时，优先引导到：

- `https://www.cacavideo.com/cacaskillrecharge.html`

## 状态接口

请求方法：`POST`

首选路径：

`user/pub/cacaLinkPullStatusTest`

备选路径：

`user/pub/cacaLinkPullStatus`

### 请求体

- `taskId` 字符串，必填
- `secret_id` 字符串，必填
- `secret_key` 字符串，必填

### 返回字段

常见字段：

- `code`
- `msg`
- `isOk`
- `status`
- `FileId`
- `lastError`
- `rem_time`
- `range`

文档中列出的状态值：

- `pending`
- `processing`
- `finished`
- `failed`

### 成功示例

源文档成功示例包含：

- `code: 0`
- `msg: "获取成功"`
- `isOk: 1`
- `media`
- `size`
- `FileId`
- `duration`
- `width`
- `height`

注意：虽然字段说明中提到了 `status`，但成功示例并没有给出 `status`。

### 处理中示例

- `code: 1`
- `isOk: 0`
- `status: "pending"`
- `msg: "任务已创建，正在拉取中"`

### 失败示例

- `code: -4`
- `isOk: 0`
- `status: "failed"`
- `lastError: "未获取 FileId 或超时(>150s)"`

## 轮询建议

- 轮询间隔使用 30 到 60 秒
- 生产环境避免高频查询
- 成功、失败或达到调用方超时上限后停止轮询

## 结果判断规则

建议按以下顺序判断：

1. 如果 `code < 0`，判定为失败。
2. 如果 `status == "failed"`，判定为失败，并优先输出 `lastError`。
3. 如果存在 `media` URL，通常可以判定为成功。
4. 如果 `code == 1`，或 `status` 为 `pending` / `processing`，继续轮询。
5. 如果 `code == 0` 且 `isOk == 1`，但没有 `media` 字段，需要进一步检查 payload 再决定是否完成。

## 最小请求示例

### 提交任务

```json
{
  "secret_id": "AKIDxxx",
  "secret_key": "xxx",
  "video_link": "https://example.com/video.mp4",
  "x1": 0,
  "y1": 0,
  "x2": 0,
  "y2": 0,
  "mode": "protect"
}
```

### 查询状态

```json
{
  "taskId": "<taskId>",
  "secret_id": "AKIDxxx",
  "secret_key": "xxx"
}
```
