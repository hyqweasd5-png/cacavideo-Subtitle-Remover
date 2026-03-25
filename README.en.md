# cacavideo-Subtitle-Remover

[中文](README.md) | [English](README.en.md)

This repository contains a reusable skill package for integrating the CacaVideo async media-pull API: `cacaLinkPullAsyc` / `cacaLinkPullStatus`. It is suitable for OpenClaw, Codex, and other hosts that support `SKILL.md` or AgentSkills-style skill folders.

## What Is Included

- `caca-link-pull-api/`
  - bilingual `SKILL.md`
  - Chinese and English API references
  - `agents/openai.yaml` metadata
  - a Python CLI helper for task submission, status polling, and live API testing
- `接口文档Test.md`
  - the original source document used to build the skill

## Supported Hosts

This skill is organized in a portable AgentSkills-style layout and can be used by:

- OpenClaw
- Codex / OpenAI skill-compatible hosts
- other agent runtimes that read `SKILL.md` from a skill folder

## Skill Structure

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

## Installation

Copy `caca-link-pull-api/` into your host application's `skills/` directory.

Examples:

- OpenClaw: place the folder under the runtime's `skills/` directory
- local skill hosts: place it in a directory where the host scans for `SKILL.md`

## What The Skill Does

The skill teaches an agent to:

1. submit an async media-pull task
2. poll task status
3. interpret success, processing, and failure payloads
4. handle `Test` vs non-`Test` route differences

The included CLI can also be used directly for manual testing.

## API Inputs

Required:

- `secret_id`
- `secret_key`
- `video_link`

Optional:

- `x1`
- `y1`
- `x2`
- `y2`
- `mode` with values `normal` or `protect`

## Credential And Recharge Entry Points

- official website: `https://www.cacavideo.com`
- recharge page: `https://www.cacavideo.com/cacaskillrecharge.html`

Use the official website when you need API access or credentials.

Use the recharge page when the API reports insufficient balance, or when you need to recharge by `Secret ID`.

## Quick Start

Set credentials:

```powershell
$env:CACA_SECRET_ID="your_secret_id"
$env:CACA_SECRET_KEY="your_secret_key"
```

Submit and wait for completion:

```powershell
python ".\caca-link-pull-api\scripts\caca_link_pull.py" run `
  --video-link "https://example.com/video.mp4" `
  --pretty
```

Query an existing task:

```powershell
python ".\caca-link-pull-api\scripts\caca_link_pull.py" wait `
  --task-id "<taskId>" `
  --interval 30 `
  --max-attempts 10 `
  --pretty
```

If the deployment uses non-`Test` routes:

```powershell
python ".\caca-link-pull-api\scripts\caca_link_pull.py" run `
  --submit-path "user/pub/cacaLinkPullAsyc" `
  --status-path "user/pub/cacaLinkPullStatus" `
  --video-link "https://example.com/video.mp4" `
  --pretty
```

## Current Limitation

This repository currently supports link-based upload only.

That means:

- supported: public `http` / `https` media URLs via `video_link`
- not supported directly: local file paths such as `C:\video.mp4`

If you need to use a local file, upload it somewhere accessible first, then pass the public URL to `video_link`.

## Validation

The skill package can be validated locally with:

```powershell
python -X utf8 "C:\Users\Administrator.BF-202507112132\.codex\skills\.system\skill-creator\scripts\quick_validate.py" ".\caca-link-pull-api"
```

The CLI has also been tested against the live API using a public video URL.

## Notes

- On Windows, prefer `python -X utf8` when validating bilingual docs to avoid encoding issues
- Do not commit real `secret_id` / `secret_key` values into the repository
- The packaged `.zip` file is excluded from Git by `.gitignore`

## Reference Files

- [caca-link-pull-api/SKILL.md](caca-link-pull-api/SKILL.md)
- [caca-link-pull-api/references/api-contract.zh-CN.md](caca-link-pull-api/references/api-contract.zh-CN.md)
- [caca-link-pull-api/references/api-contract.en.md](caca-link-pull-api/references/api-contract.en.md)
- [caca-link-pull-api/scripts/caca_link_pull.py](caca-link-pull-api/scripts/caca_link_pull.py)
