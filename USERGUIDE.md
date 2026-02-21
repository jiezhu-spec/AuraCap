# AuraCap 用户手册（小白可执行版）

## 0. 你先做一个选择

### 路径 A：我有服务器/本机，可以跑后端
- 你会得到一个 API 地址（例如 `https://cap.yourdomain.com`）
- iOS 快捷指令直接把截图/录音发给这个地址

### 路径 B：我不想维护后端，只用 GitHub
- 你不需要常驻后端
- iOS 先上传文件到 GitHub Release Asset
- iOS 再触发 `repository_dispatch`
- GitHub Action 自动处理并写回 `storage/`

如果你是小白，建议先走路径 B。

## 1. 路径 A（自部署/云部署）

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

### 1.3 路径 A 的 iOS 快捷指令

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
- 文件选“截取屏幕”输出
6. 动作 `显示结果`

录音：
1. 新建快捷指令
2. 动作 `文本`：
`https://cap.yourdomain.com/v1/capture/raw?media_type=audio&source=ios_shortcut&locale=zh-CN&timezone=local&mime_type=audio/m4a`
3. 动作 `URL`
4. 动作 `录制音频`
5. 动作 `获取 URL 内容`（POST + 文件）
6. 动作 `显示结果`

### 1.4 路径 A 成功判定
1. 快捷指令返回 JSON，含 `status: success`
2. 本地或服务器的 `storage/timeline.md` 增加新记录

## 2. 路径 B（GitHub-only，无外部中转）

### 2.1 第一步：准备仓库与权限
1. fork AuraCap 到你自己的 GitHub。
2. 进入仓库：`Settings -> Secrets and variables -> Actions`。
3. 先点 `Variables` 页签，逐个点击 `New repository variable` 添加以下变量：
- `TEXT_PROVIDER=mock`
- `MM_PROVIDER=mock`
- `ASR_PROVIDER=mock`
- `OUTPUT_LOCALE=zh-CN`
- `DEFAULT_TIMEZONE=local`
- `GITHUB_RELEASE_INBOX_TAG=auracap-inbox`
- `GITHUB_RELEASE_DELETE_AFTER_PROCESS=true`
4. 再点 `Secrets` 页签，点击 `New repository secret` 添加模型 key。
5. 推荐先把 `TEXT_PROVIDER`、`MM_PROVIDER`、`ASR_PROVIDER` 统一为同一供应商，先跑通后再做混搭。

#### 2.1.1 OpenAI 实填示例（GitHub-only）
在 `Settings -> Secrets and variables -> Actions` 中：

Variables 这样填：
- `TEXT_PROVIDER=openai`
- `MM_PROVIDER=openai`
- `ASR_PROVIDER=openai`
- `OPENAI_TEXT_MODEL=gpt-4.1-mini`
- `OPENAI_MM_MODEL=gpt-4.1-mini`
- `OPENAI_ASR_MODEL=gpt-4o-mini-transcribe`
- `OUTPUT_LOCALE=zh-CN`
- `DEFAULT_TIMEZONE=local`

Secrets 这样填：
- Name：`OPENAI_API_KEY`
- Secret：`<你的OpenAI API Key>`

可选 Variables（不填也能跑）：
- `OPENAI_BASE_URL=https://api.openai.com/v1`

完整可复制版本：
```env
TEXT_PROVIDER=openai
MM_PROVIDER=openai
ASR_PROVIDER=openai
OPENAI_TEXT_MODEL=gpt-4.1-mini
OPENAI_MM_MODEL=gpt-4.1-mini
OPENAI_ASR_MODEL=gpt-4o-mini-transcribe
OUTPUT_LOCALE=zh-CN
DEFAULT_TIMEZONE=local
OPENAI_BASE_URL=https://api.openai.com/v1
```

#### 2.1.2 Gemini 实填示例（GitHub-only）
在 `Settings -> Secrets and variables -> Actions` 中：

Variables 这样填：
- `TEXT_PROVIDER=google`
- `MM_PROVIDER=google`
- `ASR_PROVIDER=google`
- `GOOGLE_TEXT_MODEL=gemini-2.0-flash`
- `GOOGLE_MM_MODEL=gemini-2.0-flash`
- `GOOGLE_ASR_MODEL=gemini-2.0-flash`
- `OUTPUT_LOCALE=zh-CN`
- `DEFAULT_TIMEZONE=local`

Secrets 这样填：
- Name：`GOOGLE_API_KEY`
- Secret：`<你的Gemini API Key>`

可选 Variables（不填也能跑）：
- `GOOGLE_BASE_URL=https://generativelanguage.googleapis.com`

完整可复制版本：
```env
TEXT_PROVIDER=google
MM_PROVIDER=google
ASR_PROVIDER=google
GOOGLE_TEXT_MODEL=gemini-2.0-flash
GOOGLE_MM_MODEL=gemini-2.0-flash
GOOGLE_ASR_MODEL=gemini-2.0-flash
OUTPUT_LOCALE=zh-CN
DEFAULT_TIMEZONE=local
GOOGLE_BASE_URL=https://generativelanguage.googleapis.com
```

#### 2.1.3 如何判断模型配置成功
1. 手动触发一次 `AuraCap Ingest Dispatch` 或跑一次 iOS 快捷指令。
2. 在 Actions 日志里不再看到 `AUTH_FAILED`。
3. `storage/timeline.md` 里出现非空提取内容，而不是 mock 文本。

#### 2.1.4 路径 A（本地/云部署）如何配 OpenAI/Gemini
如果你走路径 A（自己跑后端），不是在 GitHub 页面配，而是改仓库根目录 `.env`。

OpenAI 示例：
```env
TEXT_PROVIDER=openai
MM_PROVIDER=openai
ASR_PROVIDER=openai
OPENAI_API_KEY=<你的OpenAI API Key>
OPENAI_TEXT_MODEL=gpt-4.1-mini
OPENAI_MM_MODEL=gpt-4.1-mini
OPENAI_ASR_MODEL=gpt-4o-mini-transcribe
```

Gemini 示例：
```env
TEXT_PROVIDER=google
MM_PROVIDER=google
ASR_PROVIDER=google
GOOGLE_API_KEY=<你的Gemini API Key>
GOOGLE_TEXT_MODEL=gemini-2.0-flash
GOOGLE_MM_MODEL=gemini-2.0-flash
GOOGLE_ASR_MODEL=gemini-2.0-flash
```

改完后重启服务：
- 本地运行：重启 `python backend/main.py`
- Docker：`docker compose up -d --build`

### 2.2 第二步：创建 GitHub Token（逐步点击版）
你需要一个给 iOS 快捷指令使用的 GitHub token，用来上传 Release Asset 和触发 `repository_dispatch`。

按下面步骤做：
1. 打开 GitHub 右上角头像，点 `Settings`。
2. 左侧拉到最下面，点 `Developer settings`。
3. 点 `Personal access tokens` -> `Fine-grained tokens`。
4. 点 `Generate new token`。
5. `Token name` 填：`auracap-ios-dispatch`（可自定义）。
6. `Expiration` 选一个到期时间（建议先选 90 天，后续可续期）。
7. `Repository access` 选：`Only select repositories`，然后只勾选你的 AuraCap fork 仓库。
8. `Repository permissions` 里把 `Contents` 设为 `Read and write`。
9. 点页面底部 `Generate token`。
10. 复制生成的 token，放到快捷指令变量 `AURACAP_GH_TOKEN`。这个值只会显示一次，丢了就要重建。

避免踩坑：
1. 不要用过期 token。
2. 不要选错仓库（必须是你实际触发 workflow 的那个 fork）。
3. 不要把权限设成 `Read-only`，否则会上传/触发失败。

### 2.3 第三步：初始化 Release Inbox（一键）
1. 打开仓库 `Actions` 页面。
2. 运行 workflow：`AuraCap Setup Release Inbox`。
3. 运行结束后，在 Summary 里记下：
- `release_id`
- `upload_url`

你后面在 iOS 里主要用 `release_id`。

### 2.4 第四步：搭建 GitHub-only 截图快捷指令

### 2.4.1 先建变量（文本动作）
- `AURACAP_GH_OWNER`：你的 GitHub 用户名
- `AURACAP_GH_REPO`：仓库名
- `AURACAP_GH_TOKEN`：上一步创建的 token
- `AURACAP_INBOX_RELEASE_ID`：第 2.3 得到的 release_id
- `AURACAP_LOCALE`：`zh-CN`
- `AURACAP_TIMEZONE`：`local` 或 `Asia/Shanghai`

### 2.4.2 动作步骤
1. 动作：`截取屏幕`
2. 动作：`获取 URL 内容`（上传到 GitHub Release Asset）
- URL：
`https://uploads.github.com/repos/<owner>/<repo>/releases/<release_id>/assets?name=shot_<timestamp>.png`
- 方法：`POST`
- 请求正文：`文件`
- 文件：上一步截图
- Header：
  - `Authorization: Bearer <token>`
  - `Accept: application/vnd.github+json`
  - `Content-Type: image/png`
3. 动作：`获取字典值`，取返回 JSON 里的 `id`（记为 `asset_id`）
4. 动作：`文本`，填 dispatch JSON：
```json
{
  "event_type": "auracap_ingest",
  "client_payload": {
    "media_type": "screenshot",
    "mime_type": "image/png",
    "asset_id": "<asset_id>",
    "locale": "<locale>",
    "timezone": "<timezone>"
  }
}
```
5. 动作：`获取 URL 内容`（dispatch）
- URL：`https://api.github.com/repos/<owner>/<repo>/dispatches`
- 方法：`POST`
- Header：
  - `Authorization: Bearer <token>`
  - `Accept: application/vnd.github+json`
  - `Content-Type: application/json`
- 请求正文：第 4 步 JSON
6. 动作：`显示结果`

### 2.4.3 可选优化：用 GitHub App 的“调度工作流程”替代手写 dispatch
如果你的 iPhone 已安装并登录 GitHub App，可把 2.4.2 的第 4-5 步替换成下面做法，减少手写 JSON 和 header。

前提：
1. 你的 workflow 支持 `workflow_dispatch`（本项目已支持）。
2. 你知道 workflow 文件名（建议填 `ingest_dispatch.yml`）。
3. 你已在 GitHub App 登录对应账号。

替换步骤：
1. 保留 2.4.2 的第 1-3 步，拿到 `asset_id`。
2. 新增动作 `字典`，命名 `WF_INPUTS`，填入：
```json
{
  "asset_id": "<asset_id>",
  "media_type": "screenshot",
  "mime_type": "image/png",
  "locale": "<locale>",
  "timezone": "<timezone>"
}
```
3. 新增 GitHub 动作 `调度工作流程`，字段这样填：
- `Owner`：`AURACAP_GH_OWNER`
- `Workflow ID`：`ingest_dispatch.yml`
- `Repository`：`AURACAP_GH_REPO`
- `Branch / ref`：`main`（或你的默认分支）
- `Inputs`：上一步 `WF_INPUTS`
- `Account`：你在 GitHub App 登录的账号
4. 删掉 2.4.2 原来的第 4-5 步（手写 dispatch JSON + `POST /dispatches`）。
5. 保留“显示结果”或改成“显示通知”。

### 2.5 第五步：搭建 GitHub-only 录音快捷指令
步骤与 2.4 相同，改两处：
- 上传 `Content-Type` 用 `audio/m4a`
- dispatch 中改：
  - `media_type=audio`
  - `mime_type=audio/m4a`

### 2.5.1 录音的 GitHub App 调度版（可选）
如果你使用 2.4.3 的 GitHub App 调度方式，录音版只改 `WF_INPUTS` 两个字段：
1. `media_type=audio`
2. `mime_type=audio/m4a`

其余 `Owner`、`Workflow ID`、`Repository`、`Branch / ref`、`Account` 保持一致。

### 2.6 路径 B 成功判定
1. 如果用手写 dispatch：接口返回 `204 No Content`
2. 如果用 GitHub App 调度：快捷指令动作执行成功且无参数错误提示
3. Actions 出现 `AuraCap Ingest Dispatch` 运行记录
4. 运行后 `storage/` 有新提交
5. 若 `GITHUB_RELEASE_DELETE_AFTER_PROCESS=true`，对应上传 asset 会自动删除

### 2.7 路径 B 常见错误
- `401/403`：token 错或权限不足
- `404`：owner/repo/release_id 错
- Action 不触发：`event_type` 不是 `auracap_ingest` 或 workflow 不在默认分支
- Action 失败：asset 无法下载（被删、URL异常、权限问题）
- GitHub App 的 `Inputs` 灰色：先填 `Owner / Workflow ID / Repository / Branch / Account`
- GitHub App 报参数错误：检查 `Workflow ID` 是否填 `ingest_dispatch.yml`，以及 `WF_INPUTS` 是否含 `asset_id`

## 3. 配置说明（两条路径通用）

### 3.1 时间戳
- 默认时区：`DEFAULT_TIMEZONE=local`
- 格式：`TIMESTAMP_FORMAT`
- 时间戳由服务端写入，不依赖 prompt 文本生成

### 3.2 音频模式
- `TRANSCRIBE_THEN_ANALYZE`
- `DIRECT_MULTIMODAL`

### 3.3 功能开关
- `EXTRACT_ONLY`
- `ENABLE_INSIGHTS`
- `ENABLE_SUMMARY`
- `ENABLE_CUSTOM_OPERATION`

## 4. 存储输出
- `storage/timeline.md`
- `storage/insights/`
- `storage/summary/`
- `storage/customized/`

## 5. 排障清单
1. `PAYLOAD_TOO_LARGE`：改用 `/v1/capture/raw` 或 `/v1/capture/upload`
2. `AUTH_FAILED`：检查 provider 与对应 key
3. 路径 A 没写入：检查后端进程和 `storage/` 权限
4. 路径 B 没写入：检查 Actions 权限、dispatch 是否 `204`、`asset_id` 是否正确

## 6. 相关文档
- GitHub-only Inbox 详解：`/Users/massif/AuraCap/docs/GITHUB_RELEASE_INBOX.md`
- 模板快捷指令说明：`/Users/massif/AuraCap/shortcuts/README.md`

## 7. English Summary

### Path A (Self-host / Cloud)
- Run backend locally or on a server; iOS shortcuts POST to your API (`/v1/capture/raw`).
- Configure via `.env`. Generate templates: `python scripts/build_shortcuts.py`.
- Success: JSON `status: success`, new entries in `storage/timeline.md`.

### Path B (GitHub-only)
- No backend required. iOS uploads to GitHub Release Asset, then triggers `repository_dispatch`.
- Configure in `Settings -> Secrets and variables -> Actions`.
- One-time setup: run `AuraCap Setup Release Inbox`, create token with `Contents: Read and write`.
- Success: Dispatch returns 204, Actions run, `storage/` updated.

### Key Configuration
- `EXTRACT_ONLY`: only extract to timeline (no insights/summary).
- `INSIGHTS_TARGET_DAY_OFFSET`: 0=today, 1=yesterday (default).
- `SYNC_DEFAULT_FREQUENCY`: ON_EVENT (immediate), DAILY/CRON (batch at cron time).

### Troubleshooting
- `PAYLOAD_TOO_LARGE`: use `/v1/capture/raw` or `/v1/capture/upload`.
- `AUTH_FAILED`: check provider and API key.
- Path B no write: check token permissions, `event_type=auracap_ingest`, `asset_id` correct.
