# AuraCap 用户手册

**Language / 语言**：[中文](#中文) | [English](#english)

---

<a name="中文"></a>
## 中文

### 0. 选择使用方式

| 方式 | 条件 | 特点 |
|------|------|------|
| **GitHub-only** | 不希望维护服务器，希望尽量简化运维 | 上传截图至 Release 后触发 Workflow 自动处理 |
| **自部署** | 有服务器，或本机可运行 Python / Docker | iOS 直接连接你的 API，响应快、可控性高 |

两种方式都可独立使用：前者强调低维护成本与开箱即用，后者强调实时性与控制力。

### 1. GitHub-only

GitHub-only 模式下，你不需要常驻后端。iOS 将截图/录音上传到 GitHub Release Asset，再触发 Workflow；GitHub Actions 自动处理并写回 `storage/`。

**四步快速开始**：
1. Fork 本仓库
2. 在 `Settings -> Secrets and variables -> Actions` 中配置必要变量（可先用 `mock` 跑通）
3. 运行一次 `AuraCap Setup Release Inbox` 工作流
4. 按详细指南在 iPhone 上搭好快捷指令

建议首次用 `mock` 模式完成端到端验证，再切换真实模型。**完整步骤与步骤截图见 [GITHUB_RELEASE_INBOX.md](GITHUB_RELEASE_INBOX.md)。**

### 2. 自部署

### 2.1 本地部署
```bash
git clone <your-fork-or-repo-url>
cd AuraCap
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python backend/main.py
```

验证：
```bash
curl http://127.0.0.1:8000/health
```

### 2.2 云服务器部署（Docker）
```bash
git clone <your-fork-or-repo-url>
cd AuraCap
cp .env.example .env
docker compose up -d --build
docker compose ps
```

Docker Compose 启动两个容器：
- **backend**：HTTP API 服务，处理截图/录音上传，监听 8000 端口
- **scheduler**：定时任务容器，默认每小时执行一次 `run_scheduler_tick.py`，运行 insights/summary 等定时逻辑

建议：
- 用 Nginx/Caddy 反代到 `127.0.0.1:8000`
- 开 HTTPS
- 只开放 80/443

### 2.3 自部署的 iOS 快捷指令

#### 方案 1：导入模板（推荐）
1. 在仓库执行：
```bash
python scripts/build_shortcuts.py
```
2. 导入到 iPhone：
- `shortcuts/templates/AuraCap_Capture.shortcut`
- `shortcuts/templates/AuraCap_Voice.shortcut`
3. 首次运行输入 `AuraCap Backend Base URL`：
- 本地局域网示例：`http://192.168.1.23:8000`
- 云端示例：`https://cap.yourdomain.com`

#### 方案 2：手动搭建（不用模板）
将下面 URL 中的 `cap.yourdomain.com` 替换为你的实际后端地址（本地示例 `192.168.1.23:8000`，需加 `http://` 前缀）。

截图：
1. 新建快捷指令
2. 动作 `文本`：
`https://cap.yourdomain.com/v1/capture/raw?media_type=screenshot&source=ios_shortcut&locale=zh-CN&timezone=local&mime_type=image/png`
3. 动作 `URL`
4. 动作 `截取屏幕`
5. 动作 `获取 URL 内容`：
- 方法 `POST`
- 请求正文 `文件`
- 文件选"截取屏幕"输出
6. 动作 `显示结果`

录音：
1. 新建快捷指令
2. 动作 `文本`：
`https://cap.yourdomain.com/v1/capture/raw?media_type=audio&source=ios_shortcut&locale=zh-CN&timezone=local&mime_type=audio/m4a`
3. 动作 `URL`
4. 动作 `录制音频`
5. 动作 `获取 URL 内容`（POST + 文件）
6. 动作 `显示结果`

### 2.4 自部署成功判定
1. 快捷指令返回 JSON，含 `status: success`
2. 本地或服务器的 `storage/timeline.md` 增加新记录

### 2.5 捕获 API 的三种方式
自部署后端提供三种上传接口，快捷指令模板使用 `/raw`（POST 请求体直接为文件）：

| 端点 | 适用场景 |
|------|----------|
| `/v1/capture/raw` | 快捷指令直接 POST 文件，URL 传参；简单、适合大文件 |
| `/v1/capture/upload` | multipart 表单上传，可带 metadata |
| `/v1/capture/json` | Base64 编码后放入 JSON，体积有 `MAX_BASE64_CHARS` 限制，易触发 `PAYLOAD_TOO_LARGE` |

遇到 `PAYLOAD_TOO_LARGE` 时优先改用 `/raw` 或 `/upload`。

### 3. 配置说明（两条路径通用）

### 3.1 模型配置

**自部署**：在仓库根目录 `.env` 中配置。**GitHub-only**：在 `Settings -> Secrets and variables -> Actions` 的 Variables 和 Secrets 中配置。

推荐先统一 `TEXT_PROVIDER`、`MM_PROVIDER`、`ASR_PROVIDER` 为同一供应商，跑通后再混搭。

#### OpenAI（自部署 .env 示例）
```env
TEXT_PROVIDER=openai
MM_PROVIDER=openai
ASR_PROVIDER=openai
OPENAI_API_KEY=<你的OpenAI API Key>
OPENAI_TEXT_MODEL=gpt-4.1-mini
OPENAI_MM_MODEL=gpt-4.1-mini
OPENAI_ASR_MODEL=gpt-4o-mini-transcribe
```

#### OpenAI（GitHub-only Variables + Secrets）
Variables：`TEXT_PROVIDER=openai`、`MM_PROVIDER=openai`、`ASR_PROVIDER=openai`、`OPENAI_TEXT_MODEL`、`OPENAI_MM_MODEL`、`OPENAI_ASR_MODEL`、`OUTPUT_LOCALE`、`DEFAULT_TIMEZONE`。Secrets：`OPENAI_API_KEY`。

#### Gemini（自部署 .env 示例）
```env
TEXT_PROVIDER=google
MM_PROVIDER=google
ASR_PROVIDER=google
GOOGLE_API_KEY=<你的Gemini API Key>
GOOGLE_TEXT_MODEL=gemini-2.0-flash
GOOGLE_MM_MODEL=gemini-2.0-flash
GOOGLE_ASR_MODEL=gemini-2.0-flash
```

#### Gemini（GitHub-only Variables + Secrets）
Variables：`TEXT_PROVIDER=google`、`MM_PROVIDER=google`、`ASR_PROVIDER=google`、`GOOGLE_TEXT_MODEL`、`GOOGLE_MM_MODEL`、`GOOGLE_ASR_MODEL`、`OUTPUT_LOCALE`、`DEFAULT_TIMEZONE`。Secrets：`GOOGLE_API_KEY`。

#### OpenAI 兼容服务（SiliconFlow、OpenRouter、DeepSeek、通义等）
只需改 `OPENAI_BASE_URL` 和 `OPENAI_API_KEY`。以 SiliconFlow 为例：`OPENAI_BASE_URL=https://api.siliconflow.cn/v1`（中国区），模型名在 [SiliconFlow 文档](https://docs.siliconflow.cn/) 中确认。

#### 其他 Provider（Anthropic、Groq、Mistral）
config 支持 Anthropic、Groq、Mistral，变量命名见 `.env.example`（如 `ANTHROPIC_API_KEY`、`GROQ_API_KEY`、`MISTRAL_API_KEY` 及对应 `*_MODEL`、`*_BASE_URL`）。

改完后：自部署重启 `python backend/main.py` 或 `docker compose up -d --build`；GitHub-only 无需重启。

#### 如何判断模型配置成功
- **自部署**：跑一次快捷指令；检查后端日志无 `AUTH_FAILED`；`storage/timeline.md` 出现非空提取内容
- **GitHub-only**：跑一次快捷指令或手动触发 `AuraCap Ingest Dispatch`；Actions 日志中不再出现 `AUTH_FAILED`；`storage/timeline.md` 出现非空提取内容

### 3.2 时间戳与输出
- **DEFAULT_TIMEZONE**：timeline 条目与 insights/summary 日期分组的时区。`local` 表示服务器本地时区；GitHub Actions 环境无本地时区，会退化为 UTC。
- **TIMESTAMP_FORMAT**：使用 Python strftime 格式，如 `%Y-%m-%d %H:%M:%S %Z`
- **OUTPUT_LOCALE**：控制 timeline 标题、sync 推送标题等的语言，支持 `zh-CN`、`en-US`
- 时间戳由服务端写入，不依赖 prompt 文本生成

### 3.3 音频模式
录音处理有两种模式，通过 `AUDIO_MODE` 切换：

| 模式 | 流程 | 依赖 |
|------|------|------|
| `TRANSCRIBE_THEN_ANALYZE` | 先用 ASR 转写为文本，再用文本模型分析 | `ASR_PROVIDER` + `TEXT_PROVIDER` |
| `DIRECT_MULTIMODAL` | 直接把音频送给 VL 模型 | `MM_PROVIDER`（需支持音频输入） |

推荐默认 `TRANSCRIBE_THEN_ANALYZE`，兼容性更好；`DIRECT_MULTIMODAL` 需确认模型支持音频 multimodal。

### 3.4 功能开关
- **EXTRACT_ONLY**：为 `true` 时仅做 timeline 提取，**跳过** insights 与 summary；此时 `ENABLE_INSIGHTS`/`ENABLE_SUMMARY` 被忽略
- **ENABLE_SCHEDULER**：scheduler 总开关（默认 `true`）；为 `false` 时 GitHub Actions scheduler job 不运行、自部署脚本 early return；**不影响** HTTP 手动触发端点 `/v1/tasks/run-scheduled`
- **ENABLE_INSIGHTS**：是否启用每日洞察（默认 `true`）
- **ENABLE_SUMMARY**：是否启用定期摘要（默认 `true`）
- **ENABLE_CUSTOM_OPERATION**：是否启用自定义操作（默认 `false`），见下方

**自定义操作**：对 timeline 提取结果做额外 AI 处理，输出到 `storage/customized/`。需配置 `prompts/customized_prompts.md`（或 `CUSTOMIZED_PROMPT_FILE`）。`CUSTOM_OPERATION_MODE`：
- `ON_EACH_TRIGGER`：每次捕捉后立即执行
- `CRON`：按 `CUSTOM_OPERATION_CRON` 定时执行（默认每 6 小时）

**手动触发 Scheduler**：`POST /v1/tasks/run-scheduled` 可手动执行一次 insights/summary 等定时逻辑；不受 `ENABLE_SCHEDULER=false` 影响。自部署用户可用 cron 定期调用该端点替代内置 scheduler 容器。

### 3.5 自动化调度

| 变量 | 默认值 | 含义 |
| ---- | ------ | ---- |
| `INSIGHTS_CRON` | `0 1 * * *` | 洞察执行时间（每日 UTC 01:00） |
| `SUMMARY_CRON` | `0 2 * * 0` | 摘要执行时间（每周日 UTC 02:00） |
| `SUMMARY_WINDOW_DAYS` | `7` | 摘要覆盖天数 |
| `ENABLE_SCHEDULER` | `true` | 是否启用自动调度 |

- **时区**：GitHub Actions 中 cron 以 **UTC** 执行；自部署时由系统时区决定
- **weekday 约定**：使用标准 cron（0=周日，6=周六，7 为周日的别名）
- **Docker 场景**：`ENABLE_SCHEDULER=false` 时容器仍运行，但脚本立即退出；需完全停止可 `docker compose stop scheduler`
- **示例**：每周一洞察 `0 8 * * 1`；每两周摘要 `0 2 * * 0` 并设 `SUMMARY_WINDOW_DAYS=14`

### 3.6 提示词

AuraCap 的三类提示词位于 `prompts/` 目录，分别驱动 timeline 提取、每日洞察和定期摘要。你可以直接编辑这些文件，或通过环境变量指定自己的路径。

| 文件 | 作用 | 触发时机 | 模型 |
|------|------|----------|------|
| `timeline_prompts.md` | 从截图或录音中提取用户想记录的核心信息，写入 `storage/timeline.md` | 每次快捷指令完成截图/录音并上传时 | VL（截图）/ 文本或 VL（录音） |
| `insights_prompts.md` | 通读当日所有 timeline 条目，发现跨条目的模式、隐含意图、未完成信号 | 每日定时（见下方变量） | 文本 |
| `summary_prompts.md` | 纵向分析一段时间内的 timeline + insights，归纳持续关注的主题、进展与停滞、建议方向 | 每周定时（见下方变量） | 文本 |

**触发变量**（自部署写在 `.env`，GitHub-only 写在 `Settings -> Secrets and variables -> Actions` 的 Variables 中）：

| 提示词 | 变量 | 含义 | 默认值 |
|--------|------|------|--------|
| timeline | 无 | 事件驱动，每次捕捉即触发，无定时变量 | — |
| insights | `ENABLE_INSIGHTS` | 是否启用每日洞察 | `true` |
| | `INSIGHTS_CRON` | cron 表达式，定义执行时间（分 时 日 月 周） | `0 1 * * *`（每日 UTC 01:00） |
| | `INSIGHTS_TARGET_DAY_OFFSET` | 分析哪一天：`0`=当天，`1`=前一天 | `1` |
| summary | `ENABLE_SUMMARY` | 是否启用定期摘要 | `true` |
| | `SUMMARY_CRON` | cron 表达式，定义执行时间 | `0 2 * * 0`（每周日 UTC 02:00） |
| | `SUMMARY_WINDOW_DAYS` | 摘要覆盖的天数 | `7` |

上述变量需在 `ENABLE_SCHEDULER=true` 且对应 `ENABLE_*` 为 `true` 时生效。cron 格式与更多示例见 [3.5 自动化调度](#35-自动化调度)。

**自定义路径**：在 `.env` 或 GitHub Actions Variables 中设置 `TIMELINE_PROMPT_FILE`、`INSIGHTS_PROMPT_FILE`、`SUMMARY_PROMPT_FILE`，指向你自己的 Markdown 文件。

**截图 vs 录音**：默认的 timeline 提示词针对 **iOS 截图** 优化，包含过滤状态栏、导航栏等系统噪音的指引。若你主要使用**录音**：

- `TRANSCRIBE_THEN_ANALYZE` 模式下，模型收到的是 ASR 转写后的文本，没有图像；"忽略 iOS 噪音" 等描述不会造成问题，提取逻辑仍适用。
- 若希望提示词更贴合语音场景，可自行修改：移除或弱化截图相关的噪音描述，增加对会议纪要、想法、待办、口述备忘等内容的提取指引。

### 4. 存储输出
- `storage/timeline.md`：按时间顺序的原始记录
- `storage/insights/`：每日洞察
- `storage/summary/`：定期摘要
- `storage/customized/`：自定义操作（Custom Operation）的输出

存储路径可通过 `STORAGE_ROOT`、`TIMELINE_FILE`、`INSIGHTS_DIR`、`SUMMARY_DIR`、`CUSTOMIZED_DIR` 自定义。

### 4.1 输入限制与媒体类型
- **MAX_UPLOAD_MB**：上传大小上限（默认 25MB）
- **MAX_BASE64_CHARS**：`/json` 接口 Base64 字符串长度上限（默认 2M 字符）
- **ALLOWED_IMAGE_MIME**：支持的图片格式，如 `image/png,image/jpeg,image/heic`
- **ALLOWED_AUDIO_MIME**：支持的音频格式，如 `audio/m4a,audio/mp4,audio/mpeg,audio/wav,audio/x-wav`

### 4.2 同步（Sync）
启用 `SYNC_ENABLE=true` 并配置对应渠道（飞书 `FEISHU_*`、Telegram `TELEGRAM_*`、Discord `DISCORD_*`、WhatsApp `WHATSAPP_*`）后，timeline 条目、insights、summary 可推送至外部。`SYNC_DEFAULT_FREQUENCY` 控制即时推送或按 `SYNC_DEFAULT_CRON` 批量推送。详见 `.env.example` 注释。

### 4.3 安全（可选）
默认 `SKIP_SIGNATURE_VERIFICATION=true`，不校验请求签名。若启用签名校验，需设置 `REQUEST_SIGNATURE_SECRET` 并在客户端请求头携带 `X-AuraCap-Signature`（HMAC-SHA256）。

### 5. 排障清单
1. `PAYLOAD_TOO_LARGE`：改用 `/v1/capture/raw` 或 `/v1/capture/upload`
2. `AUTH_FAILED`：检查 provider 与对应 key
3. 自部署没写入：检查后端进程和 `storage/` 权限
4. GitHub-only 没写入：检查 Actions 权限、dispatch 是否 `204`、`asset_id` 是否正确

### 6. 相关文档
- [GITHUB_RELEASE_INBOX.md](GITHUB_RELEASE_INBOX.md)：GitHub-only 完整指南（含步骤截图）
- [TESTING_GITHUB_APP.md](TESTING_GITHUB_APP.md)：GitHub App 版测试清单
- [shortcuts/README.md](../shortcuts/README.md)：模板快捷指令说明

---

<a name="english"></a>
## English

### 0. Choose Your Mode

| Mode | Requirement | Characteristics |
|------|-------------|-----------------|
| **GitHub-only** | No server maintenance; minimal ops | Upload to Release, trigger Workflow; processing is automatic |
| **Self-host** | Server or local Python/Docker | iOS connects directly to your API; fast response, full control |

Both can be used independently: the former emphasizes low maintenance and out-of-the-box use, the latter emphasizes real-time control.

### 1. GitHub-only

No persistent backend. iOS uploads screenshots/recordings to GitHub Release Asset, triggers Workflow; GitHub Actions processes and writes to `storage/`.

**Four-step quick start**:
1. Fork this repository
2. Configure variables under `Settings -> Secrets and variables -> Actions` (use `mock` first to verify)
3. Run `AuraCap Setup Release Inbox` workflow once
4. Follow the detailed guide to set up shortcuts on iPhone

Start with `mock` mode for end-to-end verification, then switch to real models. **Full steps and screenshot placeholders: [GITHUB_RELEASE_INBOX.md](GITHUB_RELEASE_INBOX.md).**

### 2. Self-host

#### 2.1 Local Deployment
```bash
git clone <your-fork-or-repo-url>
cd AuraCap
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python backend/main.py
```

Verify:
```bash
curl http://127.0.0.1:8000/health
```

#### 2.2 Cloud / Docker Deployment
```bash
git clone <your-fork-or-repo-url>
cd AuraCap
cp .env.example .env
docker compose up -d --build
docker compose ps
```

Docker Compose starts two containers:
- **backend**: HTTP API for screenshot/audio upload, port 8000
- **scheduler**: Runs `run_scheduler_tick.py` hourly for insights/summary

Recommendations:
- Use Nginx/Caddy to reverse-proxy to `127.0.0.1:8000`
- Enable HTTPS
- Expose only ports 80/443

#### 2.3 iOS Shortcuts for Self-host

**Option 1: Import templates (recommended)**
1. In the repo, run:
```bash
python scripts/build_shortcuts.py
```
2. Import to iPhone: `shortcuts/templates/AuraCap_Capture.shortcut`, `shortcuts/templates/AuraCap_Voice.shortcut`
3. On first run, enter `AuraCap Backend Base URL` (e.g. `http://192.168.1.23:8000` for LAN, `https://cap.yourdomain.com` for cloud)

**Option 2: Manual setup**
Replace `cap.yourdomain.com` in the URL with your actual backend (e.g. `192.168.1.23:8000` with `http://` prefix for LAN).
Screenshot: Create shortcut with `Text` (URL), `URL`, `Take Screenshot`, `Get Contents of URL` (POST, body: File, file: screenshot output), `Show Result`.
Audio: Same flow with `Record Audio`, `audio/m4a` in URL params.

#### 2.4 Success Criteria
1. Shortcut returns JSON with `status: success`
2. `storage/timeline.md` on server gains new entries

#### 2.5 Capture API Options
Three upload endpoints; shortcut templates use `/raw` (POST body = file):

| Endpoint | Use case |
|----------|----------|
| `/v1/capture/raw` | Direct file POST from Shortcuts; simple, suited for large files |
| `/v1/capture/upload` | Multipart form upload with metadata |
| `/v1/capture/json` | Base64 in JSON; subject to `MAX_BASE64_CHARS` limit, prone to `PAYLOAD_TOO_LARGE` |

Use `/raw` or `/upload` when hitting `PAYLOAD_TOO_LARGE`.

### 3. Configuration (Both Modes)

#### 3.1 Model Configuration

**Self-host**: Configure in root `.env`. **GitHub-only**: Configure in `Settings -> Secrets and variables -> Actions` (Variables and Secrets).

Use the same provider for `TEXT_PROVIDER`, `MM_PROVIDER`, `ASR_PROVIDER` initially; mix after it works.

#### OpenAI (Self-host .env example)
```env
TEXT_PROVIDER=openai
MM_PROVIDER=openai
ASR_PROVIDER=openai
OPENAI_API_KEY=<your-key>
OPENAI_TEXT_MODEL=gpt-4.1-mini
OPENAI_MM_MODEL=gpt-4.1-mini
OPENAI_ASR_MODEL=gpt-4o-mini-transcribe
```

#### OpenAI (GitHub-only Variables + Secrets)
Variables: `TEXT_PROVIDER`, `MM_PROVIDER`, `ASR_PROVIDER`, `OPENAI_TEXT_MODEL`, `OPENAI_MM_MODEL`, `OPENAI_ASR_MODEL`, `OUTPUT_LOCALE`, `DEFAULT_TIMEZONE`. Secrets: `OPENAI_API_KEY`.

#### Gemini (Self-host .env example)
```env
TEXT_PROVIDER=google
MM_PROVIDER=google
ASR_PROVIDER=google
GOOGLE_API_KEY=<your-key>
GOOGLE_TEXT_MODEL=gemini-2.0-flash
GOOGLE_MM_MODEL=gemini-2.0-flash
GOOGLE_ASR_MODEL=gemini-2.0-flash
```

#### Gemini (GitHub-only Variables + Secrets)
Variables: `TEXT_PROVIDER`, `MM_PROVIDER`, `ASR_PROVIDER`, `GOOGLE_*_MODEL`, `OUTPUT_LOCALE`, `DEFAULT_TIMEZONE`. Secrets: `GOOGLE_API_KEY`.

#### OpenAI-compatible services (SiliconFlow, OpenRouter, DeepSeek, etc.)
Change `OPENAI_BASE_URL` and `OPENAI_API_KEY`. For SiliconFlow: `OPENAI_BASE_URL=https://api.siliconflow.cn/v1` (China). See [SiliconFlow docs](https://docs.siliconflow.cn/) for model names.

#### Other providers (Anthropic, Groq, Mistral)
Config supports Anthropic, Groq, Mistral; variable names in `.env.example` (e.g. `ANTHROPIC_API_KEY`, `GROQ_API_KEY`, `MISTRAL_API_KEY` and corresponding `*_MODEL`, `*_BASE_URL`).

After changes: Self-host restart `python backend/main.py` or `docker compose up -d --build`; GitHub-only needs no restart.

#### Verifying model config
- **Self-host**: Run shortcut; check backend logs for no `AUTH_FAILED`; non-empty content in `storage/timeline.md`
- **GitHub-only**: Run shortcut or manually trigger `AuraCap Ingest Dispatch`; no `AUTH_FAILED` in Actions logs; non-empty content in `storage/timeline.md`

### 3.2 Timestamp and Output
- **DEFAULT_TIMEZONE**: Timezone for timeline entries and insights/summary day grouping. `local` uses server timezone; GitHub Actions falls back to UTC.
- **TIMESTAMP_FORMAT**: Python strftime format (e.g. `%Y-%m-%d %H:%M:%S %Z`)
- **OUTPUT_LOCALE**: Controls language for timeline/sync titles; `zh-CN`, `en-US`
- Timestamp written server-side

### 3.3 Audio Mode
Two modes via `AUDIO_MODE`:

| Mode | Flow | Depends on |
|------|------|------------|
| `TRANSCRIBE_THEN_ANALYZE` | ASR transcribe → text model analyze | `ASR_PROVIDER` + `TEXT_PROVIDER` |
| `DIRECT_MULTIMODAL` | Audio sent directly to VL model | `MM_PROVIDER` (must support audio) |

Default `TRANSCRIBE_THEN_ANALYZE` recommended; `DIRECT_MULTIMODAL` requires audio-capable model.

### 3.4 Feature Flags
- **EXTRACT_ONLY**: when `true`, only timeline extract; **skips** insights and summary; `ENABLE_INSIGHTS`/`ENABLE_SUMMARY` ignored
- **ENABLE_SCHEDULER**: master switch (default `true`); when `false`, GitHub Actions job skips, self-host script exits early; **does not affect** HTTP manual trigger `/v1/tasks/run-scheduled`
- **ENABLE_INSIGHTS**: enable daily insights (default `true`)
- **ENABLE_SUMMARY**: enable periodic summary (default `true`)
- **ENABLE_CUSTOM_OPERATION**: enable custom operation (default `false`), see below

**Custom operation**: Extra AI processing on timeline extract results, output to `storage/customized/`. Requires `prompts/customized_prompts.md` (or `CUSTOMIZED_PROMPT_FILE`). `CUSTOM_OPERATION_MODE`:
- `ON_EACH_TRIGGER`: run immediately after each capture
- `CRON`: run on `CUSTOM_OPERATION_CRON` (default every 6 hours)

**Manual scheduler trigger**: `POST /v1/tasks/run-scheduled` runs insights/summary once; unaffected by `ENABLE_SCHEDULER=false`. Self-host users can use cron to call this endpoint instead of the scheduler container.

### 3.5 Scheduler

| Variable | Default | Meaning |
| -------- | ------- | ------- |
| `INSIGHTS_CRON` | `0 1 * * *` | Insights run time (daily, UTC 01:00) |
| `SUMMARY_CRON` | `0 2 * * 0` | Summary run time (weekly Sunday, UTC 02:00) |
| `SUMMARY_WINDOW_DAYS` | `7` | Summary window in days |
| `ENABLE_SCHEDULER` | `true` | Enable automatic scheduling |

- **Timezone**: Cron runs in **UTC** on GitHub Actions; self-host uses system timezone
- **Weekday convention**: Standard cron (0=Sunday, 6=Saturday, 7=Sunday alias)
- **Docker**: When `ENABLE_SCHEDULER=false`, container still runs but script exits immediately; use `docker compose stop scheduler` to fully stop
- **Examples**: Weekly Monday insights `0 8 * * 1`; bi-weekly summary `0 2 * * 0` with `SUMMARY_WINDOW_DAYS=14`

### 3.6 Prompts

Three prompt files under `prompts/` drive timeline extraction, daily insights, and periodic summaries. Edit them directly or set custom paths via env vars.

| File | Purpose | Trigger | Model |
|------|---------|---------|-------|
| `timeline_prompts.md` | Extract core info from screenshots/recordings into `storage/timeline.md` | On each capture upload | VL (screenshot) / Text or VL (audio) |
| `insights_prompts.md` | Analyze the day's timeline for patterns, intent, and open threads | Daily (see variables below) | Text |
| `summary_prompts.md` | Longitudinal analysis of timeline + insights; themes, progress, suggestions | Weekly (see variables below) | Text |

**Trigger variables** (Self-host: `.env`. GitHub-only: `Settings -> Secrets and variables -> Actions` -> Variables):

| Prompt | Variable | Meaning | Default |
|--------|----------|---------|---------|
| timeline | — | Event-driven; runs on each capture, no schedule var | — |
| insights | `ENABLE_INSIGHTS` | Enable daily insights | `true` |
| | `INSIGHTS_CRON` | Cron expression (min hour day month weekday) | `0 1 * * *` (daily UTC 01:00) |
| | `INSIGHTS_TARGET_DAY_OFFSET` | Which day to analyze: `0`=today, `1`=yesterday | `1` |
| summary | `ENABLE_SUMMARY` | Enable periodic summary | `true` |
| | `SUMMARY_CRON` | Cron expression | `0 2 * * 0` (weekly Sunday UTC 02:00) |
| | `SUMMARY_WINDOW_DAYS` | Summary window in days | `7` |

These take effect when `ENABLE_SCHEDULER=true` and the respective `ENABLE_*` is `true`. Cron format and examples: [3.5 Scheduler](#35-scheduler).

**Custom paths**: Set `TIMELINE_PROMPT_FILE`, `INSIGHTS_PROMPT_FILE`, `SUMMARY_PROMPT_FILE` in `.env` or GitHub Actions Variables to point to your own Markdown files.

**Screenshots vs recordings**: The default timeline prompt targets **iOS screenshots** (filtering status bar etc.). If you mainly use **recordings**:

- In `TRANSCRIBE_THEN_ANALYZE` mode, the model receives ASR transcript text; the "ignore iOS noise" instructions are harmless and the extraction logic still applies.
- To better match voice memos, edit the prompt: reduce screenshot-specific guidance and add instructions for meeting notes, ideas, to-dos, and verbal memos.

### 4. Storage Output
- `storage/timeline.md`: raw time-ordered entries
- `storage/insights/`: daily insights
- `storage/summary/`: periodic summaries
- `storage/customized/`: custom operation output

Paths configurable via `STORAGE_ROOT`, `TIMELINE_FILE`, `INSIGHTS_DIR`, `SUMMARY_DIR`, `CUSTOMIZED_DIR`.

### 4.1 Input Limits and Media Types
- **MAX_UPLOAD_MB**: upload size limit (default 25MB)
- **MAX_BASE64_CHARS**: `/json` endpoint Base64 string limit (default 2M chars)
- **ALLOWED_IMAGE_MIME**: e.g. `image/png,image/jpeg,image/heic`
- **ALLOWED_AUDIO_MIME**: e.g. `audio/m4a,audio/mp4,audio/mpeg,audio/wav,audio/x-wav`

### 4.2 Sync
Set `SYNC_ENABLE=true` and configure channels (Feishu `FEISHU_*`, Telegram `TELEGRAM_*`, Discord `DISCORD_*`, WhatsApp `WHATSAPP_*`) to push timeline/insights/summary externally. `SYNC_DEFAULT_FREQUENCY` controls immediate vs batch at `SYNC_DEFAULT_CRON`. See `.env.example` comments.

### 4.3 Security (Optional)
Default `SKIP_SIGNATURE_VERIFICATION=true`, no request signature check. To enable, set `REQUEST_SIGNATURE_SECRET` and send `X-AuraCap-Signature` (HMAC-SHA256) in client requests.

### 5. Troubleshooting
1. `PAYLOAD_TOO_LARGE`: use `/v1/capture/raw` or `/v1/capture/upload`
2. `AUTH_FAILED`: check provider and API key
3. Self-host no write: check backend process and `storage/` permissions
4. GitHub-only no write: check Actions permissions, dispatch returns 204, `asset_id` correct

### 6. Related Docs
- [GITHUB_RELEASE_INBOX.md](GITHUB_RELEASE_INBOX.md): GitHub-only full guide (with step screenshots)
- [TESTING_GITHUB_APP.md](TESTING_GITHUB_APP.md): GitHub App test checklist
- [shortcuts/README.md](../shortcuts/README.md): Shortcut templates
