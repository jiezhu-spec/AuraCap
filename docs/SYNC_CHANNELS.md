 # AuraCap 推送渠道配置指南

**Language / 语言**：[中文](#中文) | [English](#english)

---

<a name="中文"></a>
## 中文

本指南为飞书、Telegram、Discord、WhatsApp 四种推送渠道提供完整配置流程。**前置条件**：已启用 `SYNC_ENABLE=true`，并至少配置一个渠道的 `*_ENABLED=true` 及对应凭证。

---

### 0. 概述与前置

#### 四渠道一览

| 渠道 | 所需凭证 | 配置变量 | 凭证获取难度 |
|------|----------|----------|--------------|
| 飞书 | Webhook URL | `FEISHU_ENABLED`、`FEISHU_WEBHOOK_URL` | 简 |
| Telegram | Bot Token、Chat ID | `TELEGRAM_ENABLED`、`TELEGRAM_BOT_TOKEN`、`TELEGRAM_CHAT_ID` | 中 |
| Discord | Webhook URL | `DISCORD_ENABLED`、`DISCORD_WEBHOOK_URL` | 简 |
| WhatsApp | Gateway URL、Token | `WHATSAPP_ENABLED`、`WHATSAPP_GATEWAY_URL`、`WHATSAPP_TOKEN` | 高 |

#### 推送触发时机

| 类型 | 触发条件 | 默认是否推送 |
|------|----------|--------------|
| timeline | 每次 capture 完成 | 是 |
| insight | 每日洞察生成 | 否 |
| summary | 定期摘要生成 | 是 |
| customized | 自定义操作输出 | 否 |
| error | 错误通知（预留） | 是 |

#### 配置路径

| 部署模式 | 非敏感配置 | 敏感配置 |
|----------|------------|----------|
| 自托管 | `.env` 中设置 | `.env` 中设置 |
| GitHub-only | Actions Variables | Actions Secrets |

---

### 1. 通用配置

#### 推送类型

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SYNC_SEND_TIMELINE` | 推送 timeline 条目 | `true` |
| `SYNC_SEND_INSIGHT` | 推送每日洞察 | `false` |
| `SYNC_SEND_SUMMARY` | 推送定期摘要 | `true` |
| `SYNC_SEND_CUSTOMIZED` | 推送自定义操作输出 | `false` |
| `SYNC_SEND_ERRORS` | 推送错误通知 | `true` |

#### 推送频率

| 变量 | 说明 | 可选值 |
|------|------|--------|
| `SYNC_DEFAULT_FREQUENCY` | 推送模式 | `ON_EVENT`（即时）、`DAILY`、`CRON` |
| `SYNC_DEFAULT_CRON` | 批量推送时间（DAILY/CRON 时） | cron 表达式，默认 `0 9 * * *`（每天 9:00） |

---

### 2. 飞书（Feishu）

#### 2.1 获取凭证

1. 打开飞书，进入目标群组
2. 点击群组右上角设置 → **群机器人** → **添加机器人**
3. 选择 **自定义机器人**
4. 填写头像、名称、描述，点击 **添加**
5. 在安全设置中：**不要启用签名校验**（AuraCap 当前不支持，启用会导致推送失败）
6. 若启用「自定义关键词」，需确保 AuraCap 推送内容包含至少一个关键词
7. 点击 Webhook 右侧 **复制**，得到格式如 `https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxxxxxxxxxxx`

#### 2.2 GitHub-only 配置

- **Variables**：`FEISHU_ENABLED` = `true`
- **Secrets**：`FEISHU_WEBHOOK_URL` = 完整的 Webhook URL

#### 2.3 自托管配置

编辑 `.env`：

```env
SYNC_ENABLE=true
FEISHU_ENABLED=true
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/你的webhook_id
```

修改后重启 AuraCap 后端。

---

### 3. Telegram

#### 3.1 获取凭证

**1. 创建 Bot 并获取 Token**

- 在 Telegram 中搜索 @BotFather
- 发送 `/newbot`，按提示设置名称和 username
- 获得 Bot Token 后保存

**2. 获取 Chat ID**

- **私聊**：给 Bot 发一条消息（如 `/start`），然后访问：
  ```
  https://api.telegram.org/bot<你的BotToken>/getUpdates
  ```
  在返回的 JSON 中查找 `message.chat.id` 即为 chat_id（正数）

- **群组**：先将 Bot 加入群组，在群内发一条消息，再访问上述 `getUpdates` 链接，`message.chat.id` 即为群组 chat_id（通常为负数）

#### 3.2 GitHub-only 配置

- **Variables**：`TELEGRAM_ENABLED` = `true`
- **Secrets**：`TELEGRAM_BOT_TOKEN`、`TELEGRAM_CHAT_ID`

#### 3.3 自托管配置

编辑 `.env`：

```env
SYNC_ENABLE=true
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=你的BotToken
TELEGRAM_CHAT_ID=你的chat_id
```

修改后重启 AuraCap 后端。

---

### 4. Discord

#### 4.1 获取凭证

1. 打开 Discord，进入目标服务器
2. **方式一**：服务器名称 → **服务器设置** → **集成** → **创建 Webhook**
3. **方式二**：编辑目标频道 → **集成** → **创建 Webhook**
4. 选择频道、命名 Webhook，点击 **复制 Webhook URL**

**注意**：Discord 单条消息 content 限制 **2000 字符**。若 insights 或 summary 较长，推送可能因超限而失败（返回 400）。

#### 4.2 GitHub-only 配置

- **Variables**：`DISCORD_ENABLED` = `true`
- **Secrets**：`DISCORD_WEBHOOK_URL` = 完整的 Webhook URL

#### 4.3 自托管配置

编辑 `.env`：

```env
SYNC_ENABLE=true
DISCORD_ENABLED=true
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/你的webhook_id/token
```

修改后重启 AuraCap 后端。

---

### 5. WhatsApp

#### 5.1 获取凭证

AuraCap 不直接对接 WhatsApp 官方 API，需自行部署或选用**兼容 Gateway**（转发服务）。Gateway 需接受以下契约：

| 项目 | 要求 |
|------|------|
| 方法 | `POST` |
| URL | `WHATSAPP_GATEWAY_URL` |
| 请求头 | `Authorization: Bearer {WHATSAPP_TOKEN}` |
| 请求体 | `{"text": "消息内容"}`（JSON） |
| 成功条件 | HTTP 状态码 < 400 |

Gateway 负责将上述请求转发至 WhatsApp（如通过 WhatsApp Business API 或第三方服务）。AuraCap 不推荐具体第三方产品，请自行选型或自建。

#### 5.2 GitHub-only 配置

- **Variables**：`WHATSAPP_ENABLED` = `true`
- **Secrets**：`WHATSAPP_GATEWAY_URL`、`WHATSAPP_TOKEN`

#### 5.3 自托管配置

编辑 `.env`：

```env
SYNC_ENABLE=true
WHATSAPP_ENABLED=true
WHATSAPP_GATEWAY_URL=你的Gateway完整URL
WHATSAPP_TOKEN=你的Bearer认证Token
```

修改后重启 AuraCap 后端。

---

### 6. 验证与排障

#### 验证步骤

1. 完成上述配置后，触发一次 capture（截图或录音）
2. 检查对应渠道是否收到包含标题和正文的文本消息

#### 排障清单

| 现象 | 可能原因 |
|------|----------|
| 所有渠道均无推送 | `SYNC_ENABLE` 未设为 `true`；或 `*_ENABLED` 未正确配置 |
| 飞书无推送 | 检查是否启用了签名校验（需关闭）；若启用自定义关键词，确认推送内容包含关键词 |
| Telegram 无推送 | 检查 `TELEGRAM_BOT_TOKEN`、`TELEGRAM_CHAT_ID` 是否正确；Bot 需先收到用户消息才能发送 |
| Discord 推送失败 | 若 content 超 2000 字符会返回 400；可尝试关闭 `SYNC_SEND_INSIGHT` 或 `SYNC_SEND_SUMMARY` 以减小单条长度 |
| WhatsApp 无推送 | 确认 Gateway 接受上述契约；检查 `WHATSAPP_GATEWAY_URL`、`WHATSAPP_TOKEN` |
| GitHub-only 无推送 | 检查 Actions 的 Variables 与 Secrets 是否已配置；`*_ENABLED` 在 Variables，凭证在 Secrets |

---

<a name="english"></a>
## English

This guide provides step-by-step configuration for Feishu, Telegram, Discord, and WhatsApp. **Prerequisites**: `SYNC_ENABLE=true` and at least one channel with `*_ENABLED=true` and valid credentials.

---

### 0. Overview and Prerequisites

#### Four Channels at a Glance

| Channel | Credentials Required | Config Variables | Setup Difficulty |
|---------|----------------------|------------------|------------------|
| Feishu | Webhook URL | `FEISHU_ENABLED`, `FEISHU_WEBHOOK_URL` | Easy |
| Telegram | Bot Token, Chat ID | `TELEGRAM_ENABLED`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | Medium |
| Discord | Webhook URL | `DISCORD_ENABLED`, `DISCORD_WEBHOOK_URL` | Easy |
| WhatsApp | Gateway URL, Token | `WHATSAPP_ENABLED`, `WHATSAPP_GATEWAY_URL`, `WHATSAPP_TOKEN` | High |

#### Push Triggers

| Type | Trigger | Default |
|------|---------|---------|
| timeline | Each capture completes | Yes |
| insight | Daily insight generated | No |
| summary | Periodic summary generated | Yes |
| customized | Custom operation output | No |
| error | Error notification (reserved) | Yes |

#### Config Paths

| Deployment | Non-sensitive | Sensitive |
|------------|--------------|----------|
| Self-host | `.env` | `.env` |
| GitHub-only | Actions Variables | Actions Secrets |

---

### 1. Common Config

#### Push Types

| Variable | Description | Default |
|----------|-------------|---------|
| `SYNC_SEND_TIMELINE` | Push timeline entries | `true` |
| `SYNC_SEND_INSIGHT` | Push daily insights | `false` |
| `SYNC_SEND_SUMMARY` | Push periodic summaries | `true` |
| `SYNC_SEND_CUSTOMIZED` | Push custom operation output | `false` |
| `SYNC_SEND_ERRORS` | Push error notifications | `true` |

#### Push Frequency

| Variable | Description | Values |
|----------|-------------|--------|
| `SYNC_DEFAULT_FREQUENCY` | Push mode | `ON_EVENT` (immediate), `DAILY`, `CRON` |
| `SYNC_DEFAULT_CRON` | Batch push time (when DAILY/CRON) | cron expression, default `0 9 * * *` (9:00 daily) |

---

### 2. Feishu

#### 2.1 Get Credentials

1. Open Feishu, go to target group
2. Group settings → **Group Bots** → **Add Bot**
3. Select **Custom Bot**
4. Set avatar, name, description; click **Add**
5. In security settings: **Do not enable signature verification** (AuraCap does not support it; enabling will cause push failures)
6. If "Custom Keywords" is enabled, ensure AuraCap push content includes at least one keyword
7. Click **Copy** next to Webhook to get URL like `https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxxxxxxxxxxx`

#### 2.2 GitHub-only Config

- **Variables**: `FEISHU_ENABLED` = `true`
- **Secrets**: `FEISHU_WEBHOOK_URL` = full Webhook URL

#### 2.3 Self-host Config

Edit `.env`:

```env
SYNC_ENABLE=true
FEISHU_ENABLED=true
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/your_webhook_id
```

Restart AuraCap backend after changes.

---

### 3. Telegram

#### 3.1 Get Credentials

**1. Create Bot and Get Token**

- Search @BotFather in Telegram
- Send `/newbot`, follow prompts to set name and username
- Save the Bot Token

**2. Get Chat ID**

- **Private chat**: Send a message to the bot (e.g. `/start`), then visit:
  ```
  https://api.telegram.org/bot<YourBotToken>/getUpdates
  ```
  Find `message.chat.id` in the JSON response (positive number)

- **Group**: Add the bot to the group first, send a message in the group, then visit the same `getUpdates` URL; `message.chat.id` is the group chat_id (usually negative)

#### 3.2 GitHub-only Config

- **Variables**: `TELEGRAM_ENABLED` = `true`
- **Secrets**: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`

#### 3.3 Self-host Config

Edit `.env`:

```env
SYNC_ENABLE=true
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

Restart AuraCap backend after changes.

---

### 4. Discord

#### 4.1 Get Credentials

1. Open Discord, go to target server
2. **Option A**: Server name → **Server Settings** → **Integrations** → **Create Webhook**
3. **Option B**: Edit target channel → **Integrations** → **Create Webhook**
4. Select channel, name the webhook, click **Copy Webhook URL**

**Note**: Discord limits message content to **2000 characters**. Long insights or summaries may cause push failures (400 response).

#### 4.2 GitHub-only Config

- **Variables**: `DISCORD_ENABLED` = `true`
- **Secrets**: `DISCORD_WEBHOOK_URL` = full Webhook URL

#### 4.3 Self-host Config

Edit `.env`:

```env
SYNC_ENABLE=true
DISCORD_ENABLED=true
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_id/token
```

Restart AuraCap backend after changes.

---

### 5. WhatsApp

#### 5.1 Get Credentials

AuraCap does not integrate directly with WhatsApp Cloud API. You must deploy or use a **compatible Gateway** that accepts this contract:

| Item | Requirement |
|------|-------------|
| Method | `POST` |
| URL | `WHATSAPP_GATEWAY_URL` |
| Header | `Authorization: Bearer {WHATSAPP_TOKEN}` |
| Body | `{"text": "message content"}` (JSON) |
| Success | HTTP status code < 400 |

The Gateway forwards requests to WhatsApp (e.g. via WhatsApp Business API or third-party services). AuraCap does not recommend specific third-party products; choose or build your own.

#### 5.2 GitHub-only Config

- **Variables**: `WHATSAPP_ENABLED` = `true`
- **Secrets**: `WHATSAPP_GATEWAY_URL`, `WHATSAPP_TOKEN`

#### 5.3 Self-host Config

Edit `.env`:

```env
SYNC_ENABLE=true
WHATSAPP_ENABLED=true
WHATSAPP_GATEWAY_URL=your_full_gateway_url
WHATSAPP_TOKEN=your_bearer_token
```

Restart AuraCap backend after changes.

---

### 6. Verification and Troubleshooting

#### Verification Steps

1. After configuration, trigger one capture (screenshot or recording)
2. Check that the target channel receives a text message with title and body

#### Troubleshooting

| Issue | Possible Cause |
|-------|----------------|
| No push on any channel | `SYNC_ENABLE` not `true`; or `*_ENABLED` misconfigured |
| Feishu no push | Signature verification enabled (must be disabled); if custom keywords enabled, ensure push content includes them |
| Telegram no push | Check `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`; bot must receive a message from user before it can send |
| Discord push fails | Content over 2000 chars returns 400; try disabling `SYNC_SEND_INSIGHT` or `SYNC_SEND_SUMMARY` to reduce length |
| WhatsApp no push | Ensure Gateway accepts the contract above; verify `WHATSAPP_GATEWAY_URL`, `WHATSAPP_TOKEN` |
| GitHub-only no push | Verify Actions Variables and Secrets; `*_ENABLED` in Variables, credentials in Secrets |
