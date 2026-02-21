# AuraCap GitHub-only：Release Inbox 模式

## 1. 目标
不使用外部中转存储（Cloudflare/S3/Supabase）。  
全部依赖 GitHub：
1. iOS 先把截图/录音上传到 GitHub Release Asset。  
2. iOS 再触发 `repository_dispatch`，只传 `asset_id` 等元数据。  
3. Action 下载该 asset 处理，并按配置自动删除 asset。

## 2. 一次性准备

### 2.1 配置 Actions Variables/Secrets
进入：`Settings -> Secrets and variables -> Actions`

最小 Variables：
- `TEXT_PROVIDER=mock`
- `MM_PROVIDER=mock`
- `ASR_PROVIDER=mock`
- `OUTPUT_LOCALE=zh-CN`
- `DEFAULT_TIMEZONE=local`
- `GITHUB_RELEASE_INBOX_TAG=auracap-inbox`
- `GITHUB_RELEASE_DELETE_AFTER_PROCESS=true`

最小 Secrets：
- mock 联调可以不填模型 key
- 如用真实模型，再补对应 key（如 `OPENAI_API_KEY`）

### 2.2 创建 GitHub Token（给 iOS 快捷指令用）
按这个顺序点：
1. GitHub 右上角头像 -> `Settings`
2. `Developer settings`
3. `Personal access tokens` -> `Fine-grained tokens`
4. `Generate new token`

填写建议：
1. `Token name`：`auracap-ios-dispatch`
2. `Expiration`：先设 90 天
3. `Repository access`：`Only select repositories`
4. 只选择你的 AuraCap fork
5. `Repository permissions`：`Contents = Read and write`
6. 生成后复制 token，存入快捷指令变量 `AURACAP_GH_TOKEN`

常见错误：
1. token 已过期
2. 选错仓库
3. `Contents` 不是 `Read and write`

### 2.3 初始化 Inbox Release
在 Actions 手动运行：`AuraCap Setup Release Inbox`。  
运行结束后，Summary 会输出：
- `release_id`
- `upload_url`

把 `release_id` 记下来，后续 iOS 快捷指令会用到。

## 3. iOS 快捷指令变量（GitHub-only）
建议在快捷指令开头用“文本”动作维护以下变量：
- `AURACAP_GH_OWNER`（GitHub 用户名）
- `AURACAP_GH_REPO`（AuraCap 仓库名）
- `AURACAP_GH_TOKEN`（上一步创建的 token）
- `AURACAP_INBOX_RELEASE_ID`（上一步得到的 release_id）
- `AURACAP_LOCALE`（如 `zh-CN`）
- `AURACAP_TIMEZONE`（如 `Asia/Shanghai` 或 `local`）

## 4. 截图快捷指令（GitHub-only）

### 4.1 上传到 Release Asset
1. 动作：`截取屏幕`。
2. 动作：`获取 URL 内容`，设置如下：
- URL：
`https://uploads.github.com/repos/<owner>/<repo>/releases/<release_id>/assets?name=shot_<timestamp>.png`
- 方法：`POST`
- 请求正文：`文件`
- 文件：上一步“截取屏幕”输出
- Header：
  - `Authorization: Bearer <token>`
  - `Accept: application/vnd.github+json`
  - `Content-Type: image/png`
3. 动作：`获取字典值`，取上传返回 JSON 的 `id`，记为 `asset_id`。

### 4.2 触发 dispatch
4. 动作：`文本`，内容：
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
5. 动作：`获取 URL 内容`：
- URL：`https://api.github.com/repos/<owner>/<repo>/dispatches`
- 方法：`POST`
- 请求正文：`JSON`（或文本 JSON）
- Header：
  - `Authorization: Bearer <token>`
  - `Accept: application/vnd.github+json`
  - `Content-Type: application/json`
6. 动作：`显示结果`。

## 5. 录音快捷指令（GitHub-only）
步骤同截图，只改两处：
- 上传 `Content-Type` 改为 `audio/m4a`
- dispatch JSON 改为：
  - `media_type=audio`
  - `mime_type=audio/m4a`

## 6. 成功判定
1. dispatch 接口返回 `204 No Content`。  
2. Actions 页面出现 `AuraCap Ingest Dispatch` 运行。  
3. 运行成功后，仓库 `storage/` 出现新提交。  
4. 若 `GITHUB_RELEASE_DELETE_AFTER_PROCESS=true`，对应 asset 会被自动删除。

## 7. 常见问题
- `401/403`：token 错误或权限不足。  
- `404`：owner/repo/release_id 错。  
- Action 未触发：`event_type` 不等于 `auracap_ingest`。  
- Action 失败下载 asset：asset 已被手动删除或 token 无权限。  
