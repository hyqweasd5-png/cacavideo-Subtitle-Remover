# cacavideo-Subtitle-Remover

当前仓库提供的是一个可复用的 skill 包，用于接入 CacaVideo 异步拉取接口 `cacaLinkPullAsyc` / `cacaLinkPullStatus`，适合 OpenClaw、Codex 以及其他支持 `SKILL.md` / AgentSkills 风格目录的宿主。

## 仓库内容

- `caca-link-pull-api/`
  - 双语 `SKILL.md`
  - 中文和英文接口参考文档
  - `agents/openai.yaml` 元数据
  - Python CLI 工具，可用于提交任务、轮询状态和真实联调
- `接口文档Test.md`
  - 用于生成 skill 的原始接口文档

## 支持的宿主

这个 skill 按可移植的 AgentSkills 风格组织，可用于：

- OpenClaw
- Codex / OpenAI skill 兼容宿主
- 其他会从 skill 目录读取 `SKILL.md` 的 agent 运行时

## 目录结构

```text
caca-link-pull-api/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── api-contract.md
│   ├── api-contract.zh-CN.md
│   └── api-contract.en.md
└── scripts/
    └── caca_link_pull.py
```

## 安装方式

把 `caca-link-pull-api/` 复制到宿主程序的 `skills/` 目录中。

例如：

- OpenClaw：放到运行时扫描的 `skills/` 目录
- 本地 skill 宿主：放到会扫描 `SKILL.md` 的目录中

## 这个 Skill 能做什么

这个 skill 会指导模型：

1. 提交异步媒体拉取任务
2. 轮询任务状态
3. 解释成功、处理中、失败三类响应
4. 处理 `Test` 与非 `Test` 路由差异

仓库内附带的 CLI 也可以直接用于手工联调。

## 接口输入参数

必填：

- `secret_id`
- `secret_key`
- `video_link`

可选：

- `x1`
- `y1`
- `x2`
- `y2`
- `mode`，取值为 `normal` 或 `protect`

## 凭证与充值入口

- 官网：`https://www.cacavideo.com`
- 充值页：`https://www.cacavideo.com/cacaskillrecharge.html`

当你需要申请 API 能力或获取凭证时，使用官网入口。

当接口返回余额不足，或者你要通过 `Secret ID` 充值时，使用充值页。

## 快速开始

先设置凭证：

```powershell
$env:CACA_SECRET_ID="your_secret_id"
$env:CACA_SECRET_KEY="your_secret_key"
```

提交任务并等待完成：

```powershell
python ".\caca-link-pull-api\scripts\caca_link_pull.py" run `
  --video-link "https://example.com/video.mp4" `
  --pretty
```

查询已有任务：

```powershell
python ".\caca-link-pull-api\scripts\caca_link_pull.py" wait `
  --task-id "<taskId>" `
  --interval 30 `
  --max-attempts 10 `
  --pretty
```

如果当前部署使用的是非 `Test` 路由：

```powershell
python ".\caca-link-pull-api\scripts\caca_link_pull.py" run `
  --submit-path "user/pub/cacaLinkPullAsyc" `
  --status-path "user/pub/cacaLinkPullStatus" `
  --video-link "https://example.com/video.mp4" `
  --pretty
```

## 当前限制

当前版本只支持链接上传。

也就是说：

- 支持：通过 `video_link` 提交公网 `http` / `https` 视频地址
- 不直接支持：本地文件路径，例如 `C:\video.mp4`

如果要使用本地文件，需要先把文件上传到一个服务端可访问的位置，再把公网 URL 传给 `video_link`。

## 校验

本地可使用以下命令校验 skill 包结构：

```powershell
python -X utf8 "C:\Users\Administrator.BF-202507112132\.codex\skills\.system\skill-creator\scripts\quick_validate.py" ".\caca-link-pull-api"
```

这个 CLI 也已经使用真实线上接口和公开视频链接做过联调测试。

## 说明

- Windows 下校验双语文档时，建议使用 `python -X utf8`，避免编码问题
- 不要把真实 `secret_id` / `secret_key` 提交到仓库
- 打包产物 `.zip` 已在 `.gitignore` 中排除

## 参考文件

- [caca-link-pull-api/SKILL.md](caca-link-pull-api/SKILL.md)
- [caca-link-pull-api/references/api-contract.zh-CN.md](caca-link-pull-api/references/api-contract.zh-CN.md)
- [caca-link-pull-api/references/api-contract.en.md](caca-link-pull-api/references/api-contract.en.md)
- [caca-link-pull-api/scripts/caca_link_pull.py](caca-link-pull-api/scripts/caca_link_pull.py)
