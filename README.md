![AuraCap Banner](docs/banner.png)

[![License](https://img.shields.io/github/license/massif-01/AuraCap)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-iOS%20%7C%20GitHub%20Actions-lightgrey)](.)

Turn your iOS screenshots into AI-structured wisdom—one-click setup with GitHub Actions, or self-host anywhere.

---

**Language / 语言**：[中文](#中文) | [English](#english)

---

<a name="中文"></a>
## 中文

### 项目定位
AuraCap 是一个「快捷指令优先」的 AI 记录系统。

核心特点：
- iOS 交互只通过快捷指令（截图、录音）
- 不做前端 UI
- 同时支持两类部署：
  - 路径 A：自部署/云部署（有后端 API）
  - 路径 B：GitHub-only（无常驻后端，使用 GitHub Release Inbox）
- 处理结果统一落地到 `storage/`

### 先选路径

**路径 A：自部署/云部署**
- iOS 直接调用你的 AuraCap API
- 配置来源：`.env`
- 适合：你可运行 Python 服务或 Docker

**路径 B：GitHub-only（推荐给不想维护服务的小白）**
- 不需要你维护常驻 API
- iOS 先上传文件到 GitHub Release Asset
- iOS 再触发工作流（两种方式）：
  - 方式 1：手写 `repository_dispatch`（兼容性最高）
  - 方式 2：GitHub App「调度工作流程」（配置步骤更少）
- GitHub Action 处理后写回 `storage/`
- 不依赖外部中转存储服务
- 配置来源：GitHub `Actions Secrets and Variables`

### 快速开始

**路径 A：本地运行**
```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python backend/main.py
```
验证：`curl http://127.0.0.1:8000/health`

**路径 A：Docker Compose**
```bash
cp .env.example .env
docker compose up -d --build
docker compose ps
```

**路径 B：GitHub-only**
1. 配置 `Actions Secrets and Variables`
2. 运行 `AuraCap Setup Release Inbox` workflow 初始化 release inbox
3. 在 iOS 快捷指令里执行：上传 Release Asset -> 触发工作流

详细步骤：`docs/USERGUIDE.md`、`docs/GITHUB_RELEASE_INBOX.md`

### GitHub-only 最小配置
进入 `Settings -> Secrets and variables -> Actions`。必填 Variables（联调用 mock）：`TEXT_PROVIDER`、`MM_PROVIDER`、`ASR_PROVIDER`、`OUTPUT_LOCALE`、`DEFAULT_TIMEZONE`、`AURACAP_RELEASE_INBOX_TAG`、`AURACAP_RELEASE_DELETE_AFTER_PROCESS`。注意：GitHub 不允许 Variable 名以 `GITHUB_` 开头。用 OpenAI 时加 `OPENAI_API_KEY`（Secrets）。私有仓库 token 需 `Contents: Read and write`。详见 `docs/USERGUIDE.md` 第 2.2 节。

### iOS 快捷指令
- 路径 A：运行 `python scripts/build_shortcuts.py` 生成模板，导入 `shortcuts/templates/` 下的 `.shortcut` 文件。
- 路径 B：按 `docs/USERGUIDE.md` 第 2.4、2.5 节手动搭建；若用 GitHub App，见第 2.4.3、2.5.1。

### API 一览
- `POST /v1/capture/json` | `POST /v1/capture/upload` | `POST /v1/capture/raw`
- `POST /v1/webhook/dispatch` | `POST /v1/tasks/run-scheduled` | `GET /health`

### 存储输出
`storage/timeline.md`、`storage/insights/`、`storage/summary/`、`storage/customized/`

### 文档索引
- `docs/USERGUIDE.md`
- `docs/GITHUB_RELEASE_INBOX.md`
- `docs/TESTING_GITHUB_APP.md`（路径 B GitHub App 版测试流程）
- `shortcuts/README.md`

### 规则
全项目禁止 emoji；icon 仅允许 remixicon。

### 协议
[MIT License](LICENSE)

---

<a name="english"></a>
## English

### Overview
AuraCap is a shortcut-first AI capture system for screenshots and voice recordings.

Features:
- iOS interaction via Shortcuts only (screenshot, voice)
- No UI; backend-only
- Two deployment paths:
  - Path A: Self-host or cloud (Python backend API)
  - Path B: GitHub-only (no persistent backend; uses GitHub Release Inbox)
- Output written to `storage/`

### Choose a Path

**Path A: Self-host / Cloud**
- iOS posts directly to your AuraCap API
- Config via `.env`
- For users who can run Python or Docker

**Path B: GitHub-only (recommended for beginners)**
- No backend to maintain
- iOS uploads to GitHub Release Asset, then triggers workflow via `repository_dispatch` or GitHub App
- GitHub Actions process and commit to `storage/`
- Config via GitHub `Actions Secrets and Variables`

### Quick Start

**Path A: Local**
```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python backend/main.py
```
Verify: `curl http://127.0.0.1:8000/health`

**Path A: Docker**
```bash
cp .env.example .env
docker compose up -d --build
docker compose ps
```

**Path B: GitHub-only**
1. Configure `Actions Secrets and Variables`
2. Run `AuraCap Setup Release Inbox` workflow
3. In iOS Shortcuts: upload Release Asset -> trigger workflow

Full guide: `docs/USERGUIDE.md` (section 7), `docs/GITHUB_RELEASE_INBOX.md`

### GitHub-only Min Config
In `Settings -> Secrets and variables -> Actions`, add Variables: `TEXT_PROVIDER`, `MM_PROVIDER`, `ASR_PROVIDER` (use `mock` for testing), `OUTPUT_LOCALE`, `DEFAULT_TIMEZONE`, `AURACAP_RELEASE_INBOX_TAG`, `AURACAP_RELEASE_DELETE_AFTER_PROCESS`. Note: GitHub disallows variable names starting with `GITHUB_`. Add `OPENAI_API_KEY` (Secret) for OpenAI. Token needs `Contents: Read and write` for private repos.

### iOS Shortcuts
- Path A: Run `python scripts/build_shortcuts.py` and import templates from `shortcuts/templates/`
- Path B: Follow `docs/USERGUIDE.md` sections 2.4 and 2.5; or use GitHub App flow in 2.4.3 and 2.5.1

### API Summary
- `POST /v1/capture/json` | `POST /v1/capture/upload` | `POST /v1/capture/raw`
- `POST /v1/webhook/dispatch` | `POST /v1/tasks/run-scheduled` | `GET /health`

### Storage Output
`storage/timeline.md`, `storage/insights/`, `storage/summary/`, `storage/customized/`

### Docs
- `docs/USERGUIDE.md`
- `docs/GITHUB_RELEASE_INBOX.md`
- `docs/TESTING_GITHUB_APP.md` (Path B GitHub App testing flow)
- `shortcuts/README.md`

### Rules
No emoji anywhere; icons must use remixicon.

### License
[MIT License](LICENSE)
