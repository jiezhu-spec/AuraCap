![AuraCap Banner](docs/banner.png)

> 让每一次截图与录音，都成为可追溯、可复用的长期资产。 | Turn every screenshot and recording into traceable, reusable long-term assets.

[![Unique Architecture](https://img.shields.io/badge/Architecture-GitHub--Native%20Media%20Relay-blueviolet?style=flat)](https://github.com/massif-01/AuraCap#unique-innovation-github-release-as-transient-middleware)
[![Serverless](https://img.shields.io/badge/Serverless-Zero%20Cost-brightgreen?style=flat&logo=github)](https://github.com/massif-01/AuraCap)
[![Releases as Queue](https://img.shields.io/badge/Innovation-Releases%20as%20Queue-orange?style=flat&logo=github-actions)](https://github.com/massif-01/AuraCap/blob/main/docs/GITHUB_RELEASE_INBOX.md)
[![iOS Shortcuts](https://img.shields.io/badge/iOS-Shortcuts-black?style=flat&logo=apple&logoColor=white)](https://github.com/massif-01/AuraCap/tree/main/shortcuts)
[![Platform](https://img.shields.io/badge/Platform-iOS%20%7C%20GitHub%20Actions-lightgrey?style=flat)](.)
[![License](https://img.shields.io/github/license/massif-01/AuraCap?style=flat)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat)](https://www.python.org/)

---

**Language / 语言**：[中文](#中文) | [English](#english)

---

<a name="中文"></a>
## 中文

### 介绍

AuraCap 是一条从"即时捕捉"到"结构化沉淀"的通路：通过 **iOS 快捷指令**完成截图或录音，再由 AI 自动提取信息、归纳要点并写入时间线。不改变原有习惯，只是把原本会散落的信息，持续整理成可检索、可复盘的知识资产。

### 解决什么问题

多数信息系统的问题，不在于记录能力不足，而在于记录与整理被拆成了两件事：当下来不及整理，事后也很难回到现场。AuraCap 的目标，是把这两件事重新连接起来，让"捕捉"天然通向"沉淀"。

### 为什么选择 Action（快捷指令）作为入口

选择 Action，不是为了"更酷"，而是为了降低长期使用门槛。

- **贴近真实场景**：在通勤、会议、阅读或对话中，需要的是一步可达，而不是切换到重应用再组织流程
- **交互轻量且稳定**：快捷指令是系统级能力，调用链路短、交互负担低，适合高频、低摩擦的日常记录
- **系统边界清晰**：前端交互极简，后端能力可独立演进；可以替换模型、切换部署方式，而不必重做采集入口
- **更容易被坚持**：真正产生价值的记录系统，不是功能最多，而是愿意每天都用

### 特点

- **入口轻，能力重**：采集通过快捷指令完成，整理由 AI 自动执行
- **部署路径灵活**：可自部署后端，也可仅依赖 GitHub 工作流；后者无需自建服务器
- **输出长期可控**：统一写入 Markdown（如 `storage/timeline.md`），便于检索、归档、迁移与备份
- **模型生态开放**：支持 OpenAI、Gemini、SiliconFlow 等模型及平台

<a name="unique-innovation-github-release-as-transient-middleware"></a>

### 架构设计：为什么选择 GitHub Release 作为"瞬态媒体中转站"

AuraCap 可能是首个提出并实现 "GitHub Release as a Transient Middleware"（将 GitHub Release 作为瞬态中间件）的开源项目。

在设计 AuraCap 时，我面临一个核心矛盾：**如何在不依赖付费 S3 存储、不自建图床、且不暴露 Webhook 代理的情况下，让 iOS 快捷指令与 GitHub Actions 传递大体积媒体文件，实现零外部依赖的媒体采集与处理，把 GitHub Release 变成模型的预处理器？**

AuraCap 最终采取了一种些许"黑客精神"的方案：**利用 GitHub Release Assets 作为异步中转。**

1. **打破"静态发布"的刻板印象**：通常 Release 用于托管稳定的二进制包，但我将其视为一个 **带身份认证的临时对象存储（Object Storage）**。
2. **利用 `asset_id` 建立信任链**：
   - iOS 端通过 API 将截图/录音上传至特定的 `Inbox` Release。
   - 上传成功后，GitHub 返回一个唯一的 `asset_id`。
   - 快捷指令仅需携带这个 `asset_id` 触发 `workflow_dispatch`，而无需传输整个文件。
3. **零配置的安全内循环**：
   - GitHub Actions 环境中自带 `GITHUB_TOKEN`，拥有拉取本仓库 Release Assets 的天然权限。
   - 处理脚本根据 `asset_id` 直接下载、处理、写入。
   - **闭环完成**：整个过程不产生额外的存储费用，不依赖第三方 API Key，且媒体流始终在 GitHub 安全边界内流动。

### 选择使用方式

| 方式 | 条件 | 特点 |
|------|------|------|
| **GitHub-only** | 不希望维护服务器，希望尽量简化运维 | 上传截图至 Release 后触发 Workflow 自动处理 |
| **自部署** | 有服务器，或本机可运行 Python / Docker | iOS 直接连接你的 API，响应快、可控性高 |

两种方式都可独立使用：前者强调低维护成本与开箱即用，后者强调实时性与控制力。

### 快速上手

**GitHub-only（推荐）**

1. Fork 本仓库
2. 在仓库 `Settings -> Secrets and variables -> Actions` 中配置必要变量（可先使用 `mock` 跑通流程）
3. 运行一次 `AuraCap Setup Release Inbox` 工作流
4. 按用户手册在 iPhone 上搭好快捷指令

建议首次先使用 `mock` 模式完成端到端验证，再切换为 OpenAI、Gemini 等真实模型。详细步骤见 [用户手册](docs/USERGUIDE.md)。

**自部署（3 步）**

```bash
cp .env.example .env
pip install -r requirements.txt
python backend/main.py
```

浏览器访问 `http://127.0.0.1:8000/health`，出现响应即表示服务启动成功。随后在 iOS 快捷指令中填入你的 API 地址。

### 会得到什么输出

- `storage/timeline.md`：按时间顺序记录条目，包含 AI 提取结果
- `storage/insights/`：每日洞察（默认每天一次，可配置）
- `storage/summary/`：定期摘要（默认每周一次，可配置）

所有结果均为 Markdown，可同步到 Notion、Obsidian 或任意知识管理系统。你的数据结构不会被平台锁定，也便于长期积累与二次利用。调度频率与 cron 配置见 [用户手册 3.5 自动化调度](docs/USERGUIDE.md#35-自动化调度)。

### 下一步

- 完整配置与模型选择：[docs/USERGUIDE.md](docs/USERGUIDE.md)
- GitHub-only 详细说明：[docs/GITHUB_RELEASE_INBOX.md](docs/GITHUB_RELEASE_INBOX.md)
- 快捷指令模板与手动搭建：[shortcuts/README.md](shortcuts/README.md)

### 协议

[MIT License](LICENSE)

---

<a name="english"></a>
## English

### Introduction

AuraCap is a pipeline from "instant capture" to "structured consolidation": you take screenshots or voice recordings with **iOS Shortcuts**, and AI extracts information, summarizes key points, and writes them into a timeline. Without changing your existing habits, it turns scattered information into searchable, reviewable knowledge assets.

### The Problem It Solves

The issue with most information systems is not a lack of recording capacity, but that recording and organizing are split into two separate tasks: you don't have time to organize in the moment, and it's hard to return to the context later. AuraCap's goal is to reconnect these two tasks so that "capture" naturally leads to "consolidation".

### Why Shortcuts as the Entry Point

Choosing Shortcuts is not about being "cooler"—it's about lowering the barrier for long-term use.

- **Close to real scenarios**: When commuting, in meetings, reading, or in conversations, you need one-tap access, not switching to a heavy app and orchestrating a flow
- **Lightweight, stable interaction**: Shortcuts are a system-level capability; the call path is short, the interaction burden is low, suitable for high-frequency, low-friction daily capture
- **Clear system boundaries**: Minimal frontend, backend can evolve independently; you can swap models and deployment modes without rebuilding the capture entry
- **Easier to stick with**: A recording system that actually adds value is not the one with the most features, but the one you're willing to use every day

### Features

- **Light entry, heavy capability**: Capture via Shortcuts, organization by AI
- **Flexible deployment**: Self-host a backend or rely solely on GitHub workflows; the latter requires no server
- **Long-term control over output**: Everything written to Markdown (e.g. `storage/timeline.md`), easy to search, archive, migrate, and back up
- **Open model ecosystem**: Supports OpenAI, Gemini, SiliconFlow, and other models/platforms

### Architecture: Why Use GitHub Release as a "Transient Media Relay"

AuraCap may be the first open-source project to propose and implement "GitHub Release as a Transient Middleware."

The core design challenge was: **How can iOS Shortcuts and GitHub Actions pass large media files without paid S3 storage, self-hosted image hosting, or exposed webhook proxies—achieving zero external dependencies for media capture and processing, turning GitHub Release into the model's preprocessor?**

AuraCap's answer: **Use GitHub Release Assets as an asynchronous relay.**

1. **Rethinking Release**: Instead of treating Release only as a place for stable binaries, we treat it as **authenticated temporary object storage**.
2. **Trust chain via `asset_id`**:
   - iOS uploads screenshots/recordings to a dedicated Inbox Release via API.
   - GitHub returns a unique `asset_id`.
   - The shortcut passes only this `asset_id` to trigger `workflow_dispatch`—no need to transmit the full file.
3. **Zero-config secure loop**:
   - GitHub Actions has `GITHUB_TOKEN` with built-in permission to fetch the repo's Release Assets.
   - The processing script downloads, processes, and writes based on `asset_id`.
   - **Closed loop**: No extra storage cost, no third-party API keys, and the media flow stays within GitHub's security boundary.

### Choose Your Mode

| Mode | Requirement | Characteristics |
|------|-------------|-----------------|
| **GitHub-only** | No server maintenance; minimal ops | Upload to Release, trigger Workflow; processing is automatic |
| **Self-host** | Server or local Python/Docker | iOS connects directly to your API; fast response, full control |

Both can be used independently: the former emphasizes low maintenance and out-of-the-box use, the latter emphasizes real-time control.

### Quick Start

**GitHub-only (recommended)**

1. Fork this repository
2. Configure required variables under `Settings -> Secrets and variables -> Actions` (use `mock` first to verify the flow)
3. Run the `AuraCap Setup Release Inbox` workflow once
4. Set up the shortcut on your iPhone following the [user guide](docs/USERGUIDE.md)

Start with `mock` mode to complete an end-to-end run, then switch to OpenAI, Gemini, or other real models. See [docs/USERGUIDE.md](docs/USERGUIDE.md) for details.

**Self-host (3 steps)**

```bash
cp .env.example .env
pip install -r requirements.txt
python backend/main.py
```

Visit `http://127.0.0.1:8000/health` in your browser; a response means the service is up. Then add your API base URL in the iOS shortcut.

### Output

- `storage/timeline.md`: Time-ordered entries with AI-extracted content
- `storage/insights/`: Daily insights (default: once per day, configurable)
- `storage/summary/`: Periodic summaries (default: once per week, configurable)

All output is Markdown and can be synced to Notion, Obsidian, or any knowledge management system. Your data format stays platform-agnostic and supports long-term accumulation and reuse. For schedule frequency and cron configuration, see [User Guide 3.5 Scheduler](docs/USERGUIDE.md#35-scheduler).

### Next Steps

- Full configuration and model selection: [docs/USERGUIDE.md](docs/USERGUIDE.md)
- GitHub-only setup details: [docs/GITHUB_RELEASE_INBOX.md](docs/GITHUB_RELEASE_INBOX.md)
- Shortcut templates and manual setup: [shortcuts/README.md](shortcuts/README.md)

### License

[MIT License](LICENSE)
