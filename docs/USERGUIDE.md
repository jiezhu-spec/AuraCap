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

### 1. 自部署

### 1.1 本地部署
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

### 1.2 云服务器部署（Docker）
```bash
git clone <your-fork-or-repo-url>
cd AuraCap
cp .env.example .env
docker compose up -d --build
docker compose ps
```

建议：
- 用 Nginx/Caddy 反代到 `127.0.0.1:8000`
- 开 HTTPS
- 只开放 80/443

### 1.3 自部署的 iOS 快捷指令

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

### 1.4 自部署成功判定
1. 快捷指令返回 JSON，含 `status: success`
2. 本地或服务器的 `storage/timeline.md` 增加新记录

### 2. GitHub-only

GitHub-only 模式下，你不需要常驻后端。iOS 将截图/录音上传到 GitHub Release Asset，再触发 Workflow；GitHub Actions 自动处理并写回 `storage/`。

**四步快速开始**：
1. Fork 本仓库
2. 在 `Settings -> Secrets and variables -> Actions` 中配置必要变量（可先用 `mock` 跑通）
3. 运行一次 `AuraCap Setup Release Inbox` 工作流
4. 按详细指南在 iPhone 上搭好快捷指令

建议首次用 `mock` 模式完成端到端验证，再切换真实模型。**完整步骤与截图占位见 [GITHUB_RELEASE_INBOX.md](GITHUB_RELEASE_INBOX.md)。**

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

改完后：自部署重启 `python backend/main.py` 或 `docker compose up -d --build`；GitHub-only 无需重启。

#### 如何判断模型配置成功
1. 跑一次快捷指令或手动触发 `AuraCap Ingest Dispatch`
2. Actions 日志中不再出现 `AUTH_FAILED`
3. `storage/timeline.md` 出现非空提取内容

### 3.2 时间戳
- 默认时区：`DEFAULT_TIMEZONE=local`
- 格式：`TIMESTAMP_FORMAT`
- 时间戳由服务端写入，不依赖 prompt 文本生成

### 3.3 音频模式
- `TRANSCRIBE_THEN_ANALYZE`
- `DIRECT_MULTIMODAL`

### 3.4 功能开关
- `EXTRACT_ONLY`：为 `true` 时仅做提取，跳过 insights 与 summary
- `ENABLE_SCHEDULER`：scheduler 总开关（默认 `true`）；为 `false` 时 GitHub Actions scheduler job 不运行、自部署脚本 early return；**不影响** HTTP 手动触发端点 `/v1/tasks/run-scheduled`
- `ENABLE_INSIGHTS`
- `ENABLE_SUMMARY`
- `ENABLE_CUSTOM_OPERATION`

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

### 4. 存储输出
- `storage/timeline.md`
- `storage/insights/`
- `storage/summary/`
- `storage/customized/`

### 5. 排障清单
1. `PAYLOAD_TOO_LARGE`：改用 `/v1/capture/raw` 或 `/v1/capture/upload`
2. `AUTH_FAILED`：检查 provider 与对应 key
3. 自部署没写入：检查后端进程和 `storage/` 权限
4. GitHub-only 没写入：检查 Actions 权限、dispatch 是否 `204`、`asset_id` 是否正确

### 6. 相关文档
- [GITHUB_RELEASE_INBOX.md](GITHUB_RELEASE_INBOX.md)：GitHub-only 完整指南（含截图占位）
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

### 1. Self-host

#### 1.1 Local Deployment
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

#### 1.2 Cloud / Docker Deployment
```bash
git clone <your-fork-or-repo-url>
cd AuraCap
cp .env.example .env
docker compose up -d --build
docker compose ps
```

Recommendations:
- Use Nginx/Caddy to reverse-proxy to `127.0.0.1:8000`
- Enable HTTPS
- Expose only ports 80/443

#### 1.3 iOS Shortcuts for Self-host

**Option 1: Import templates (recommended)**
1. In the repo, run:
```bash
python scripts/build_shortcuts.py
```
2. Import to iPhone: `shortcuts/templates/AuraCap_Capture.shortcut`, `shortcuts/templates/AuraCap_Voice.shortcut`
3. On first run, enter `AuraCap Backend Base URL` (e.g. `http://192.168.1.23:8000` for LAN, `https://cap.yourdomain.com` for cloud)

**Option 2: Manual setup**
Screenshot: Create shortcut with `Text` (URL), `URL`, `Take Screenshot`, `Get Contents of URL` (POST, body: File, file: screenshot output), `Show Result`.
Audio: Same flow with `Record Audio`, `audio/m4a` in URL params.

#### 1.4 Success Criteria
1. Shortcut returns JSON with `status: success`
2. `storage/timeline.md` on server gains new entries

### 2. GitHub-only

No persistent backend. iOS uploads screenshots/recordings to GitHub Release Asset, triggers Workflow; GitHub Actions processes and writes to `storage/`.

**Four-step quick start**:
1. Fork this repository
2. Configure variables under `Settings -> Secrets and variables -> Actions` (use `mock` first to verify)
3. Run `AuraCap Setup Release Inbox` workflow once
4. Follow the detailed guide to set up shortcuts on iPhone

Start with `mock` mode for end-to-end verification, then switch to real models. **Full steps and screenshot placeholders: [GITHUB_RELEASE_INBOX.md](GITHUB_RELEASE_INBOX.md).**

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

After changes: Self-host restart `python backend/main.py` or `docker compose up -d --build`; GitHub-only needs no restart.

#### Verifying model config
1. Run shortcut or manually trigger `AuraCap Ingest Dispatch`
2. No `AUTH_FAILED` in Actions logs
3. Non-empty content in `storage/timeline.md`

### 3.2 Timestamp
- Default timezone: `DEFAULT_TIMEZONE=local`
- Format: `TIMESTAMP_FORMAT`
- Timestamp written server-side

### 3.3 Audio Mode
- `TRANSCRIBE_THEN_ANALYZE`
- `DIRECT_MULTIMODAL`

### 3.4 Feature Flags
- `EXTRACT_ONLY`: when `true`, only extract; skip insights and summary
- `ENABLE_SCHEDULER`: master switch for scheduler (default `true`); when `false`, GitHub Actions scheduler job is skipped, self-host script exits early; **does not affect** HTTP manual trigger `/v1/tasks/run-scheduled`
- `ENABLE_INSIGHTS`
- `ENABLE_SUMMARY`
- `ENABLE_CUSTOM_OPERATION`

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

### 4. Storage Output
- `storage/timeline.md`
- `storage/insights/`
- `storage/summary/`
- `storage/customized/`

### 5. Troubleshooting
1. `PAYLOAD_TOO_LARGE`: use `/v1/capture/raw` or `/v1/capture/upload`
2. `AUTH_FAILED`: check provider and API key
3. Self-host no write: check backend process and `storage/` permissions
4. GitHub-only no write: check Actions permissions, dispatch returns 204, `asset_id` correct

### 6. Related Docs
- [GITHUB_RELEASE_INBOX.md](GITHUB_RELEASE_INBOX.md): GitHub-only full guide (with screenshot placeholders)
- [TESTING_GITHUB_APP.md](TESTING_GITHUB_APP.md): GitHub App test checklist
- [shortcuts/README.md](../shortcuts/README.md): Shortcut templates
