# AuraCap Test Flow (GitHub App)

**Language / 语言**：[中文](#中文) | [English](#english)

---

<a name="中文"></a>
## 中文

本流程已整合进 [GITHUB_RELEASE_INBOX.md](GITHUB_RELEASE_INBOX.md) 作为主指南，本文档保留为测试清单与快速参考。

本流程按用户实际操作顺序编写，逐项完成后即可正常使用。**前置条件**：iPhone 已安装 [GitHub App](https://apps.apple.com/app/github/id1477376905) 并登录你的 GitHub 账号。

---

### 一、在 GitHub 上的准备

### 步骤 1：Fork 仓库

Fork `AuraCap` 到你自己的 GitHub 账号，后续所有操作都在你的 fork 上。

### 步骤 2：配置 Variables

进入 `Settings -> Secrets and variables -> Actions`，点 `Variables` 页签，添加：

| 变量名 | 值 |
|--------|-----|
| `TEXT_PROVIDER` | `mock` |
| `MM_PROVIDER` | `mock` |
| `ASR_PROVIDER` | `mock` |
| `OUTPUT_LOCALE` | `zh-CN` |
| `DEFAULT_TIMEZONE` | `local` |
| `AURACAP_RELEASE_INBOX_TAG` | `auracap-inbox` |
| `AURACAP_RELEASE_DELETE_AFTER_PROCESS` | `true` |

说明：GitHub 不允许变量名以 `GITHUB_` 开头，故使用 `AURACAP_` 前缀。mock 模式无需配置 Secrets。调度相关变量详见 [USERGUIDE.md § 3.5 自动化调度](USERGUIDE.md#35-自动化调度)。

若使用真实模型（如 Google、OpenAI、SiliconFlow 等），需额外配置 Variables 和 Secrets，详见 [USERGUIDE.md 配置说明](USERGUIDE.md#3-配置说明两条路径通用)。

### 步骤 3：创建 Fine-grained Token

1. GitHub 右上角头像 -> `Settings`
2. 左侧底部 -> `Developer settings`
3. `Personal access tokens` -> `Fine-grained tokens` -> `Generate new token`
4. 填写：`Token name`（如 `auracap-ios`），`Expiration`（如 90 天），`Repository access` 选 `Only select repositories` 并勾选你的 AuraCap fork
5. `Repository permissions` -> `Contents` 设为 `Read and write`
6. 生成后**立即复制 token**（只显示一次），先保存在备忘录，后面填到快捷指令里

### 步骤 4：初始化 Release Inbox

1. 进入仓库 `Actions` 页面
2. 左侧选择 `AuraCap Setup Release Inbox`
3. 点击 `Run workflow` -> `Run workflow`
4. 运行完成后，点击该次运行 -> 点击 job `setup` -> 展开步骤 **`Ensure release inbox exists`**
5. 在**步骤日志**中复制 `release_id` 的数值（例如 `123456789`），保存到备忘录

---

### 二、在 iPhone 上搭快捷指令

### 步骤 5：新建快捷指令并添加变量

**只建一个快捷指令**（可命名为「AuraCap 截图」）。在这个快捷指令里，**重复 6 次**以下组合：

1. **「文本」动作**：搜索「文本」，添加后往文本框里填**值**
2. **「设定变量」动作**：搜索「设定变量」，添加；上一步的文本会自动接到「输入」；**点「变量名称」那一行**，输入下表中的变量名

| 第几组 | 变量名（在「变量名称」里填） | 值（文本动作里填） |
|--------|-----------------------------|---------------------|
| 1 | `AURACAP_GH_OWNER` | 你的 GitHub 用户名（如 `massif-01`） |
| 2 | `AURACAP_GH_REPO` | `AuraCap` |
| 3 | `AURACAP_GH_TOKEN` | 步骤 3 复制的 token |
| 4 | `AURACAP_INBOX_RELEASE_ID` | 步骤 4 得到的 `release_id` 数值 |
| 5 | `AURACAP_LOCALE` | `zh-CN` |
| 6 | `AURACAP_TIMEZONE` | `local` |

提示：底部搜索框输入「设定变量」或「变量」，在「脚本」分类里找；添加后该动作会显示「输入」「变量名称」两行，点「变量名称」即可输入名字。完成后共 12 个动作（6 组「文本」+「设定变量」），后面再接截屏、上传等。

**从这里开始，所有动作都在同一个快捷指令里，紧接在 12 个变量动作的下方按顺序添加。**

完整动作顺序（非常重要，不能乱）：
```
[12个变量]
→ 文本(Bearer)
→ 截屏
→ 文本(URL)
→ 获取 URL 内容
→ 获取词典值
→ 词典
→ 调度工作流程
→ 显示通知（可选）
```

### 步骤 6：添加「文本」——Bearer token

搜索「文本」，添加在 12 个变量动作的最下方。在文本框输入 `Bearer `（注意后面有**一个空格**），再点输入框 →「选择变量」→ 选 `AURACAP_GH_TOKEN`。

这一步必须放在截屏和上传之前，方便后面「获取 URL 内容」的头部直接引用。

### 步骤 7：添加「截屏」

搜索「截取屏幕」或「截屏」，添加在「文本(Bearer)」下方。

### 步骤 8：添加「文本」——拼接上传 URL

搜索「文本」，添加在「截屏」下方。在文本框里这样拼：

1. 先输入：`https://uploads.github.com/repos/`
2. 点一下输入框，弹出「选择变量」后选 `AURACAP_GH_OWNER`
3. 再输入：`/`
4. 点一下输入框，弹出「选择变量」后选 `AURACAP_GH_REPO`
5. 再输入：`/releases/`
6. 点一下输入框，弹出「选择变量」后选 `AURACAP_INBOX_RELEASE_ID`
7. 最后输入：`/assets?name=shot.png`

拼完后类似：`https://uploads.github.com/repos/massif-01/AuraCap/releases/123456789/assets?name=shot.png`

### 步骤 9：添加「获取 URL 内容」——上传截图

搜索「获取 URL 内容」，添加在「文本(URL)」正下方。此时标题栏自动接入上一步的 URL，不需要手动选。然后配置：

1. **方法**：点右侧「GET」→ 改成 **POST**，改完后出现「请求体」行。
2. **请求体**：点右侧「JSON」→ 改成 **文件**，改完后出现「文件」行。
3. **文件**：点「文件」右侧「选取变量」→ 直接点「**截屏**」即可。
4. **头部**：点「头部」右侧 `>` 展开 → 点「添加新头部」（绿色 ＋）→ 添加以下头部：

| 键（左栏输入） | 值（右栏输入） |
|----------------|----------------|
| `Authorization` | 点右边值栏 →「选择变量」→ 选「**文本(Bearer)**」（即步骤 6 的文本动作输出） |
| `Accept` | 直接输入 `application/vnd.github+json` |
| `Content-Type` | 直接输入 `image/png` |

### 步骤 10：添加「获取词典值」——取 asset_id

搜索「获取词典值」，添加在「获取 URL 内容」正下方。此时自动接入上一步的返回结果，不需要手动改。然后：

1. 点「**键**」→ 输入 `id`
2. 「获取」保持「值」不变

### 步骤 11：添加「词典」——构造 WF_INPUTS

搜索「**词典**」，添加。点「添加新项目」依次添加 5 个条目，每次点「添加新项目」后选「**文本**」类型：

| 左边（键）填 | 右边（值）填 |
|-------------|-------------|
| `asset_id` | 点右边值栏 →「选择变量」→ 选「**获取词典值**」的输出 |
| `media_type` | 直接输入 `screenshot` |
| `mime_type` | 直接输入 `image/png` |
| `locale` | 点右边值栏 →「选择变量」→ 选 `AURACAP_LOCALE` |
| `timezone` | 点右边值栏 →「选择变量」→ 选 `AURACAP_TIMEZONE` |

### 步骤 12：添加「调度工作流程」

搜索「**调度工作流程**」，添加。每个字段右边是「文本」输入栏，点进去填：

| 字段 | 填法 |
|------|------|
| Owner | 点右边值栏 →「选择变量」→ 选 `AURACAP_GH_OWNER` |
| Workflow ID | 直接输入 `ingest_dispatch.yml` |
| Repository | 点右边值栏 →「选择变量」→ 选 `AURACAP_GH_REPO` |
| Branch / ref | 直接输入 `main` |
| Inputs | 点右边值栏 →「选择变量」→ 选上一步「词典」的输出 |
| Account | 已自动识别，无需修改 |

注意：**Inputs 灰色无法点击时**，先把 Owner、Workflow ID、Repository、Branch、Account 都填好，Inputs 才会变成可点击状态。

### 步骤 13：添加「显示通知」（可选）

搜索「**显示通知**」，添加。界面有两个输入栏：

- **「你好，世界！」**（通知正文）：可直接输入任意文字，如 `AuraCap 截图已上传`，或保持默认不改
- **「通知」右边的 `>`**：点进去可设置标题等，不需要可忽略

这一步纯粹用于确认快捷指令执行结束，不影响功能，也可以不加。

---

### 三、实测与验证

### 步骤 14：运行快捷指令

在 iPhone 上运行该快捷指令。会先截屏，再自动上传并触发 workflow。

### 步骤 15：验证成功

1. **快捷指令**：无报错、无「参数错误」提示
2. **GitHub Actions**：进入仓库 Actions，应看到 `AuraCap Ingest Dispatch` 有新运行记录
3. **存储**：该次运行成功后，`storage/timeline.md` 会有新提交和新内容
4. **Asset 清理**：若 `AURACAP_RELEASE_DELETE_AFTER_PROCESS=true`，对应 Release Asset 会被自动删除

---

### 四、常见问题

| 现象 | 可能原因 | 处理 |
|------|----------|------|
| Inputs 灰色 | 必填字段未填完 | 先填 Owner、Workflow ID、Repository、Branch、Account |
| 401 / 403 | Token 无效或权限不足 | 检查 Token 是否过期、是否勾选 Contents: Read and write |
| 404 | owner / repo / release_id 错误 | 核对变量值与仓库、Release 是否一致 |
| Action 未触发 | 参数缺失或错误 | 检查 Workflow ID 是否为 `ingest_dispatch.yml`，WF_INPUTS 是否包含 `asset_id` |

---

### 五、录音版快捷指令

在截图版基础上，修改以下三处：

1. 步骤 7「截取屏幕」改为「录制音频」
2. 步骤 9（上传）的 Header：`Content-Type` 改为 `audio/m4a`
3. 步骤 11（词典）：`media_type` 改为 `audio`，`mime_type` 改为 `audio/m4a`

其余步骤不变。

---

<a name="english"></a>
## English

This flow is consolidated into [GITHUB_RELEASE_INBOX.md](GITHUB_RELEASE_INBOX.md) as the primary guide. This doc remains as a test checklist and quick reference.

Steps follow actual user flow. **Prerequisite**: iPhone has [GitHub App](https://apps.apple.com/app/github/id1477376905) installed with your GitHub account logged in.

---

### Part I: GitHub Preparation

#### Step 1: Fork Repository

Fork `AuraCap` to your GitHub account. All following operations are on your fork.

#### Step 2: Configure Variables

Go to `Settings -> Secrets and variables -> Actions`, click `Variables`, add:

| Variable | Value |
|----------|-------|
| `TEXT_PROVIDER` | `mock` |
| `MM_PROVIDER` | `mock` |
| `ASR_PROVIDER` | `mock` |
| `OUTPUT_LOCALE` | `zh-CN` |
| `DEFAULT_TIMEZONE` | `local` |
| `AURACAP_RELEASE_INBOX_TAG` | `auracap-inbox` |
| `AURACAP_RELEASE_DELETE_AFTER_PROCESS` | `true` |

Note: GitHub disallows variable names starting with `GITHUB_`, so we use `AURACAP_` prefix. Mock mode needs no Secrets. For scheduler variables, see [USERGUIDE § 3.5 Scheduler](USERGUIDE.md#35-scheduler).

For real models (OpenAI, Gemini, SiliconFlow, etc.), add Variables and Secrets. See [USERGUIDE configuration](USERGUIDE.md#3-configuration-both-modes).

#### Step 3: Create Fine-grained Token

1. GitHub profile -> `Settings`
2. Bottom left -> `Developer settings`
3. `Personal access tokens` -> `Fine-grained tokens` -> `Generate new token`
4. Fill: `Token name` (e.g. `auracap-ios`), `Expiration` (e.g. 90 days), `Repository access` = `Only select repositories`, select your AuraCap fork
5. `Repository permissions` -> `Contents` = `Read and write`
6. **Copy token immediately** (shown once). Save in Notes, then paste into shortcut variables

#### Step 4: Initialize Release Inbox

1. Go to repo `Actions`
2. Select `AuraCap Setup Release Inbox`
3. Click `Run workflow` -> `Run workflow`
4. After run, click the run -> job `setup` -> expand step **`Ensure release inbox exists`**
5. Copy `release_id` from step log (e.g. `123456789`), save to Notes

---

### Part II: Build Shortcut on iPhone

#### Step 5: New Shortcut and Variables

**Create one shortcut** (e.g. "AuraCap Screenshot"). **Repeat 6 times**:

1. **"Text" action**: Search "Text", add, fill value
2. **"Set Variable" action**: Search "Set Variable", add; previous text auto-wires to "Input"; tap "Variable Name" row, enter name from table

| # | Variable name | Value |
|---|---------------|-------|
| 1 | `AURACAP_GH_OWNER` | Your GitHub username (e.g. `massif-01`) |
| 2 | `AURACAP_GH_REPO` | `AuraCap` |
| 3 | `AURACAP_GH_TOKEN` | Token from Step 3 |
| 4 | `AURACAP_INBOX_RELEASE_ID` | `release_id` from Step 4 |
| 5 | `AURACAP_LOCALE` | `zh-CN` |
| 6 | `AURACAP_TIMEZONE` | `local` |

Tip: Search "Set Variable" or "variable" in Scripts. After adding, tap "Variable Name" to enter. Total 12 actions (6 Text + Set Variable pairs), then screenshot and upload.

**From here, all actions go in the same shortcut, below the 12 variable actions, in order.**

Action sequence (order matters):
```
[12 variables]
→ Text(Bearer)
→ Take Screenshot
→ Text(URL)
→ Get Contents of URL
→ Get Dictionary Value
→ Dictionary
→ Run Workflow
→ Show Notification (optional)
```

#### Step 6: Add "Text" — Bearer token

Search "Text", add below the 12 variable actions. In text box enter `Bearer ` (one space after), then tap input -> "Select Variable" -> `AURACAP_GH_TOKEN`.

Must be before screenshot/upload so "Get Contents of URL" headers can reference it.

#### Step 7: Add "Take Screenshot"

Search "Take Screenshot" or "Screenshot", add below "Text(Bearer)".

#### Step 8: Add "Text" — Upload URL

Search "Text", add below Screenshot. Build URL:
1. Enter `https://uploads.github.com/repos/`
2. Tap input -> Select Variable -> `AURACAP_GH_OWNER`
3. Enter `/`
4. Select Variable -> `AURACAP_GH_REPO`
5. Enter `/releases/`
6. Select Variable -> `AURACAP_INBOX_RELEASE_ID`
7. Enter `/assets?name=shot.png`

Result: `https://uploads.github.com/repos/massif-01/AuraCap/releases/123456789/assets?name=shot.png`

#### Step 9: Add "Get Contents of URL" — Upload

Search "Get Contents of URL", add below "Text(URL)". URL auto-wires. Configure:
1. **Method**: Change GET to **POST**; "Request Body" row appears
2. **Request Body**: Change JSON to **File**; "File" row appears
3. **File**: Tap "File" -> "Select Variable" -> choose **Screenshot** output
4. **Headers**: Expand "Headers" -> "Add new header" (+) -> add:

| Key | Value |
|-----|-------|
| `Authorization` | Tap value -> "Select Variable" -> "Text(Bearer)" (Step 6 output) |
| `Accept` | `application/vnd.github+json` |
| `Content-Type` | `image/png` |

#### Step 10: Add "Get Dictionary Value" — asset_id

Search "Get Dictionary Value", add below previous. Auto-wires to URL response. Set:
1. **Key** -> enter `id`
2. **Get** -> keep "Value"

#### Step 11: Add "Dictionary" — WF_INPUTS

Search "Dictionary", add. Tap "Add new item" and add 5 entries (select "Text" type each time):

| Key | Value |
|-----|-------|
| `asset_id` | Tap value -> "Select Variable" -> "Get Dictionary Value" output |
| `media_type` | `screenshot` |
| `mime_type` | `image/png` |
| `locale` | Tap value -> Select Variable -> `AURACAP_LOCALE` |
| `timezone` | Tap value -> Select Variable -> `AURACAP_TIMEZONE` |

#### Step 12: Add "Run Workflow"

Search "Run Workflow", add. Each field has a text input; fill:

| Field | Value |
|-------|-------|
| Owner | Tap value -> Select Variable -> `AURACAP_GH_OWNER` |
| Workflow ID | `ingest_dispatch.yml` |
| Repository | Tap value -> Select Variable -> `AURACAP_GH_REPO` |
| Branch / ref | `main` |
| Inputs | Tap value -> Select Variable -> previous "Dictionary" output |
| Account | Auto-filled, no change needed |

Note: **If Inputs is grey**, fill Owner, Workflow ID, Repository, Branch, Account first; Inputs becomes clickable.

#### Step 13: Add "Show Notification" (optional)

Search "Show Notification", add. Two input fields:
- **"Hello, World!"** (body): Enter any text, e.g. `AuraCap screenshot uploaded`, or leave default
- **">" next to "Notification"**: Tap for title etc.; optional

Purely for confirming shortcut completion; no functional impact. Can be omitted.

---

### Part III: Test and Verify

#### Step 14: Run Shortcut

Run the shortcut on iPhone. It screenshots, uploads, and triggers the workflow.

#### Step 15: Verify Success

1. **Shortcut**: No error, no "parameter error"
2. **GitHub Actions**: Enter repo Actions; new run of `AuraCap Ingest Dispatch` should appear
3. **Storage**: After run succeeds, `storage/timeline.md` gains new commit and content
4. **Asset cleanup**: If `AURACAP_RELEASE_DELETE_AFTER_PROCESS=true`, the Release Asset is auto-deleted

---

### Part IV: Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Inputs grey | Required fields empty | Fill Owner, Workflow ID, Repository, Branch, Account first |
| 401 / 403 | Token invalid or insufficient permissions | Check token expiry, Contents: Read and write |
| 404 | owner / repo / release_id wrong | Verify variable values match repo and Release |
| Action not triggered | Missing or wrong parameters | Check Workflow ID = `ingest_dispatch.yml`, WF_INPUTS contains `asset_id` |

---

### Part V: Voice Recording Shortcut

Same as screenshot. Change these three:
1. Step 7: "Take Screenshot" -> "Record Audio"
2. Step 9 (upload) Header: `Content-Type` -> `audio/m4a`
3. Step 11 (Dictionary): `media_type` -> `audio`, `mime_type` -> `audio/m4a`

All other steps unchanged.
