# caca-link-pull-api API contract

## Overview

This reference normalizes the source Markdown into an agent-friendly English contract for the async media-pull workflow.

## Base URL

Default router base from the source document:

`https://env-00jxh2cj3gfd.dev-hz.cloudbasefunction.cn/http/router/`

## Route ambiguity

The source document contains two route variants:

- summary section: `user/pub/cacaLinkPullAsycTest` and `user/pub/cacaLinkPullStatusTest`
- section headings and code snippets: `user/pub/cacaLinkPullAsyc` and `user/pub/cacaLinkPullStatus`

Safe rule:

1. Prefer the explicit `...Test` routes when no deployment-specific override exists.
2. If requests fail because the route is unknown, retry with the non-`Test` routes.
3. Keep both route values configurable in generated code and scripts.

## Authentication

Both endpoints require these JSON body fields:

- `secret_id` string
- `secret_key` string

The source document says this matches the existing system's auth behavior.
If the caller has not been provisioned yet, start from the official website `https://www.cacavideo.com` and use the API cooperation or business onboarding path there to obtain `secret_id` / `secret_key`.
If the caller needs to recharge balance, use `https://www.cacavideo.com/cacaskillrecharge.html`. The page supports entering a `Secret ID` for recharge and also exposes a flow for generating new API credentials.

## Submit endpoint

Method: `POST`

Preferred path:

`user/pub/cacaLinkPullAsycTest`

Alternative path:

`user/pub/cacaLinkPullAsyc`

### Request body

- `secret_id` string required
- `secret_key` string required
- `video_link` string required
- `x1` number optional, default `0`
- `y1` number optional, default `0`
- `x2` number optional, default `0`
- `y2` number optional, default `0`
- `mode` string optional, default `"normal"`

Allowed `mode` values from the source:

- `normal`
- `protect`

### Immediate success shape

Typical fields:

- `code: 0`
- `msg: "任务已创建，后台处理中"`
- `isOk: 1`
- `taskId`
- `FileId: ""`
- `resultName: ""`
- `rem_time`
- `range`

### Immediate failure example

Insufficient balance example:

- `code: -1`
- `isOk: 0`
- `msg: "余额不足，请充值"`

When the API indicates insufficient balance, direct the user to:

- `https://www.cacavideo.com/cacaskillrecharge.html`

## Status endpoint

Method: `POST`

Preferred path:

`user/pub/cacaLinkPullStatusTest`

Alternative path:

`user/pub/cacaLinkPullStatus`

### Request body

- `taskId` string required
- `secret_id` string required
- `secret_key` string required

### Response fields

Common fields:

- `code`
- `msg`
- `isOk`
- `status`
- `FileId`
- `lastError`
- `rem_time`
- `range`

Documented status values:

- `pending`
- `processing`
- `finished`
- `failed`

### Success example

The source success example includes:

- `code: 0`
- `msg: "获取成功"`
- `isOk: 1`
- `media`
- `size`
- `FileId`
- `duration`
- `width`
- `height`

Note: the success example does not include a `status` field, even though the field is documented elsewhere.

### In-progress example

- `code: 1`
- `isOk: 0`
- `status: "pending"`
- `msg: "任务已创建，正在拉取中"`

### Failure example

- `code: -4`
- `isOk: 0`
- `status: "failed"`
- `lastError: "未获取 FileId 或超时(>150s)"`

## Polling guidance

- use a 30 to 60 second interval
- avoid high-frequency polling in production
- stop on success, `failed`, or a caller-defined timeout

## Interpretation rules

Use these rules in this order:

1. If `code < 0`, treat the call as failed.
2. If `status == "failed"`, treat the task as failed and surface `lastError`.
3. If a `media` URL is present, treat the task as successful.
4. If `code == 1` or `status` is `pending` or `processing`, keep polling.
5. If `code == 0` and `isOk == 1` but no `media` field exists, inspect the payload before deciding whether the task is complete.

## Minimal request examples

### Submit

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

### Status

```json
{
  "taskId": "<taskId>",
  "secret_id": "AKIDxxx",
  "secret_key": "xxx"
}
```
