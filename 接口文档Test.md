# 接口文档：cacaLinkPullAsyc / cacaLinkPullStatus

- BaseUrl: https://env-00jxh2cj3gfd.dev-hz.cloudbasefunction.cn/http/router/

本文档描述两个云函数接口：

- 提交异步拉取：`user/pub/cacaLinkPullAsycTest`（POST）
- 查询任务状态：`user/pub/cacaLinkPullStatusTest`（POST）

两个接口均使用 JSON 请求/响应，并要求在 body 中携带 `secret_id` / `secret_key` 进行鉴权（与现有系统一致）。

---

## 一、通用信息

- Content-Type: `application/json`
- 所有返回均为 JSON：`{ code, msg, isOk, ... }`
- 建议客户端：提交后使用 `taskId` 调用 `cacaLinkPullStatus` 轮询获取最终结果，轮询频率建议 30-60 秒，生产环境请避免短时间高频请求。

---

## 二、提交异步拉取 —— POST /user/pub/cacaLinkPullAsyc

### 请求参数（JSON）
- secret_id (string) 必需
- secret_key (string) 必需
- video_link (string) 必需
- x1, y1, x2, y2 (number) 可选（范围参数，默认为 0）
- mode (string) 可选，默认 `"normal"`。可取值：
  - `"normal"`：默认行为。
  - `"protect"`：保护模式。

示例请求 body：
```json
{
  "secret_id": "AKIDxxx",
  "secret_key": "xxx",
  "video_link": "https://example.com/video.mp4",
  "x1": 0, "y1": 0, "x2": 0, "y2": 0,
  "mode": "protect"
}
```

### 成功返回（立即返回，不等待拉取完成）
```json
{
  "code": 0,
  "msg": "任务已创建，后台处理中",
  "isOk": 1,
  "taskId": "<本地任务id>",
  "FileId": "",           // 提交时尚不可用，返回空字符串以兼容同步接口
  "resultName": "",
  "rem_time": 123,         // 调用者余额
  "range": {"x1":0,"y1":0,"x2":0,"y2":0}
}
```

错误示例（余额不足）：
```json
{ "code": -1, "msg": "余额不足，请充值", "isOk": 0 }
```

---

## 三、查询任务状态 —— POST /user/pub/cacaLinkPullStatus

### 请求参数（JSON）
- taskId (string) 必需 —— 提交接口返回的本地任务 `_id`
- secret_id (string) 必需
- secret_key (string) 必需

示例请求 body：
```json
{ "taskId": "<taskId>", "secret_id": "AKIDxxx", "secret_key": "xxx" }
```

### 返回字段说明
- code, msg, isOk
- status: pending / processing / finished / failed
- FileId: 任务记录中的 `originalFileId`（可能为空）
- lastError: 失败原因（如有）
- rem_time: 调用者余额
- range: { x1,y1,x2,y2 }


### 成功示例（媒体可用）
```json
{
  "code": 0,
  "msg": "获取成功",
  "isOk": 1,
  "media": "https://cdn.example.com/xxx.mp4",
  "size": 123456,
  "FileId": "xxxxxx",
  "duration": 12.3,
  "width": 1080,
  "height": 1920
}
```

处理中示例：
```json
{ "code": 1, "msg": "任务已创建，正在拉取中", "isOk": 0, "status":"pending" }
```

失败示例：
```json
{ "code": -4, "msg": "未获取 FileId 或超时(>150s)", "isOk": 0, "status":"failed", "lastError":"未获取 FileId 或超时(>150s)" }
```

---

## 四、示例调用代码

下面给出 JavaScript (fetch)、Python (requests)、PHP (curl) 和 C# (HttpClient) 的最小示例，便于开发快速接入。

### 1) JavaScript (fetch)
提交异步拉取：
```javascript
await fetch('https://yourdomain.com/user/pub/cacaLinkPullAsyc', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({ secret_id:'AKIDxxx', secret_key:'xxx', video_link:'https://example.com/video.mp4', mode: 'protect' })
}).then(r=>r.json()).then(console.log);
```

查询状态：
```javascript
await fetch('https://yourdomain.com/user/pub/cacaLinkPullStatus', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({ taskId:'<taskId>', secret_id:'AKIDxxx', secret_key:'xxx' })
}).then(r=>r.json()).then(console.log);
```

### 2) Python (requests)
提交：
```python
import requests
r = requests.post('https://yourdomain.com/user/pub/cacaLinkPullAsyc', json={
  'secret_id':'AKIDxxx','secret_key':'xxx','video_link':'https://example.com/video.mp4', 'mode':'protect'
})
print(r.json())
```
查询：
```python
r = requests.post('https://yourdomain.com/user/pub/cacaLinkPullStatus', json={ 'taskId':'<taskId>','secret_id':'AKIDxxx','secret_key':'xxx' })
print(r.json())
```

### 3) PHP (curl)
提交：
```php
$ch = curl_init('https://yourdomain.com/user/pub/cacaLinkPullAsyc');
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode(['secret_id'=>'AKIDxxx','secret_key'=>'xxx','video_link'=>'https://example.com/video.mp4','mode'=>'protect']));
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type:application/json']);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
echo curl_exec($ch);
```
查询：
```php
$ch = curl_init('https://yourdomain.com/user/pub/cacaLinkPullStatus');
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode(['taskId'=>'<taskId>','secret_id'=>'AKIDxxx','secret_key'=>'xxx']));
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type:application/json']);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
echo curl_exec($ch);
```

### 4) C# (.NET HttpClient)
提交：
```csharp
using var client = new HttpClient();
var resp = await client.PostAsJsonAsync("https://yourdomain.com/user/pub/cacaLinkPullAsyc", new { secret_id="AKIDxxx", secret_key="xxx", video_link="https://example.com/video.mp4", mode = "protect" });
var json = await resp.Content.ReadFromJsonAsync<object>();
Console.WriteLine(json);
```
查询：
```csharp
var resp = await client.PostAsJsonAsync("https://yourdomain.com/user/pub/cacaLinkPullStatus", new { taskId="<taskId>", secret_id="AKIDxxx", secret_key="xxx" });
var json = await resp.Content.ReadFromJsonAsync<object>();
Console.WriteLine(json);
```

---