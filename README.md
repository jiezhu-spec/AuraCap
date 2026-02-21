# AuraCap

Slogan: Capture the spark, let AI do the rest.

Repo description: Turn your iOS screenshots into AI structured wisdom.

## 项目定位
AuraCap 是一个“快捷指令优先”的 AI 记录系统。

核心特点：
- iOS 交互只通过快捷指令（截图、录音）
- 不做前端 UI
- 同时支持两类部署：
  - 路径 A：自部署/云部署（有后端 API）
  - 路径 B：GitHub-only（无常驻后端，使用 GitHub Release Inbox）
- 处理结果统一落地到 `storage/`

## 先选路径

### 路径 A：自部署/云部署
- iOS 直接调用你的 AuraCap API
- 配置来源：`.env`
- 适合：你可运行 Python 服务或 Docker

### 路径 B：GitHub-only（推荐给不想维护服务的小白）
- 不需要你维护常驻 API
- iOS 先上传文件到 GitHub Release Asset
- iOS 再触发工作流（两种方式）：
  - 方式 1：手写 `repository_dispatch`（兼容性最高）
  - 方式 2：GitHub App `调度工作流程`（配置步骤更少）
- GitHub Action 处理后写回 `storage/`
- 不依赖外部中转存储服务
- 配置来源：GitHub `Actions Secrets and Variables`

## 快速开始

### 路径 A：本地运行
```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python backend/main.py
```

检查：
```bash
curl http://127.0.0.1:8000/health
```

### 路径 A：Docker Compose
```bash
cp .env.example .env
docker compose up -d --build
docker compose ps
```

### 路径 B：GitHub-only
1. 配置 `Actions Secrets and Variables`
2. 运行 `AuraCap Setup Release Inbox` workflow 初始化 release inbox
3. 在 iOS 快捷指令里执行：上传 Release Asset -> 触发工作流（`repository_dispatch` 或 GitHub App 调度）

详细步骤请看：
- `/Users/massif/AuraCap/USERGUIDE.md`
- `/Users/massif/AuraCap/docs/GITHUB_RELEASE_INBOX.md`

## GitHub-only 最小配置清单
进入：`Settings -> Secrets and variables -> Actions`

| 场景 | 必填 Variables | 必填 Secrets |
| --- | --- | --- |
| 联调（mock） | `TEXT_PROVIDER=mock`<br>`MM_PROVIDER=mock`<br>`ASR_PROVIDER=mock`<br>`OUTPUT_LOCALE=zh-CN`<br>`DEFAULT_TIMEZONE=local`<br>`GITHUB_RELEASE_INBOX_TAG=auracap-inbox`<br>`GITHUB_RELEASE_DELETE_AFTER_PROCESS=true` | 无 |
| OpenAI | 上述 + `TEXT_PROVIDER=openai`<br>`MM_PROVIDER=openai`<br>`ASR_PROVIDER=openai` | `OPENAI_API_KEY` |
| Gemini | 上述 + `TEXT_PROVIDER=google`<br>`MM_PROVIDER=google`<br>`ASR_PROVIDER=google` | `GOOGLE_API_KEY` |

私有仓库触发 `repository_dispatch` 的 token 权限最小值：
- `Contents: Read and write`
- 创建 token 的逐步图文式说明见：`/Users/massif/AuraCap/USERGUIDE.md` 第 2.2 节

### Actions Variables/Secrets 怎么填（小白步骤）
1. 打开你的 fork 仓库，进入 `Settings -> Secrets and variables -> Actions`。
2. 点 `Variables` 页签，使用 `New repository variable` 新建变量（Name/Value）。
3. 点 `Secrets` 页签，使用 `New repository secret` 新建密钥（Name/Secret）。
4. 变量名必须和文档完全一致（区分大小写），不要多空格。
5. `TEXT_PROVIDER`、`MM_PROVIDER`、`ASR_PROVIDER` 建议先统一同一供应商。

### OpenAI 实填示例（可直接照填）
Variables：
- `TEXT_PROVIDER=openai`
- `MM_PROVIDER=openai`
- `ASR_PROVIDER=openai`
- `OPENAI_TEXT_MODEL=gpt-4.1-mini`
- `OPENAI_MM_MODEL=gpt-4.1-mini`
- `OPENAI_ASR_MODEL=gpt-4o-mini-transcribe`

Secrets：
- `OPENAI_API_KEY=<你的OpenAI API Key>`
- 在 GitHub 中：`Secrets` -> `New repository secret`
  - Name: `OPENAI_API_KEY`
  - Secret: 粘贴你的 OpenAI key（通常以 `sk-` 开头）

### Gemini 实填示例（可直接照填）
Variables：
- `TEXT_PROVIDER=google`
- `MM_PROVIDER=google`
- `ASR_PROVIDER=google`
- `GOOGLE_TEXT_MODEL=gemini-2.0-flash`
- `GOOGLE_MM_MODEL=gemini-2.0-flash`
- `GOOGLE_ASR_MODEL=gemini-2.0-flash`

Secrets：
- `GOOGLE_API_KEY=<你的Gemini API Key>`
- 在 GitHub 中：`Secrets` -> `New repository secret`
  - Name: `GOOGLE_API_KEY`
  - Secret: 粘贴你的 Gemini key

### 路径 A（本地/云）.env 对照示例
OpenAI：
```env
TEXT_PROVIDER=openai
MM_PROVIDER=openai
ASR_PROVIDER=openai
OPENAI_API_KEY=<你的OpenAI API Key>
OPENAI_TEXT_MODEL=gpt-4.1-mini
OPENAI_MM_MODEL=gpt-4.1-mini
OPENAI_ASR_MODEL=gpt-4o-mini-transcribe
```

Gemini：
```env
TEXT_PROVIDER=google
MM_PROVIDER=google
ASR_PROVIDER=google
GOOGLE_API_KEY=<你的Gemini API Key>
GOOGLE_TEXT_MODEL=gemini-2.0-flash
GOOGLE_MM_MODEL=gemini-2.0-flash
GOOGLE_ASR_MODEL=gemini-2.0-flash
```

## iOS 快捷指令文件
生成模板：
```bash
python scripts/build_shortcuts.py
```

模板文件：
- `shortcuts/templates/AuraCap_Capture.shortcut`
- `shortcuts/templates/AuraCap_Voice.shortcut`
- `shortcuts/templates/AuraCap_Capture.plist`
- `shortcuts/templates/AuraCap_Voice.plist`

注意：
- 上述模板只用于路径 A（直传后端 API）
- 路径 B（GitHub-only）请按 `USERGUIDE` 第 2.4 与第 2.5 节搭建快捷指令
- 如果已安装 GitHub App，优先看 `USERGUIDE` 第 2.4.3 与第 2.5.1（调度工作流程版，步骤更少）

## API 一览
- `POST /v1/capture/json`
- `POST /v1/capture/upload`
- `POST /v1/capture/raw`
- `POST /v1/webhook/dispatch`
- `POST /v1/tasks/run-scheduled`
- `GET /health`

## 存储输出
- `storage/timeline.md`
- `storage/insights/*.md`
- `storage/summary/*.md`
- `storage/customized/*.md`

## 时间戳机制
时间戳由服务端写入，不依赖 prompt 输出：
- 实现文件：`backend/app/services/timeline.py`
- 时区：`DEFAULT_TIMEZONE` 或请求 `timezone`
- 格式：`TIMESTAMP_FORMAT`

## 文档索引
- 主操作手册：`/Users/massif/AuraCap/USERGUIDE.md`
- GitHub-only Inbox 指南：`/Users/massif/AuraCap/docs/GITHUB_RELEASE_INBOX.md`
- 快捷指令模板说明：`/Users/massif/AuraCap/shortcuts/README.md`

## 规则
- 全项目禁止 emoji（包括文档、注释、代码）
- 如需 icon，仅允许 remixicon

## English Snapshot
AuraCap is a shortcut-first pipeline for screenshot/audio capture.
- Route A: self-host/cloud backend API
- Route B: GitHub-only with Release Inbox + `repository_dispatch`
- Full guide: `/Users/massif/AuraCap/USERGUIDE.md`
