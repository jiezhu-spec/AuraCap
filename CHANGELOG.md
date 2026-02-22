# Changelog

**Language / 语言**：[中文](#中文) | [English](#english)

---

<a name="中文"></a>
## 中文

### [Unreleased]
#### 变更
- Summary 默认频率由每 3 天改为每周（`SUMMARY_CRON` 默认 `0 2 * * 0`，`SUMMARY_WINDOW_DAYS` 默认 `7`）；两者均可通过变量自定义
- Insights 保持每日一次，可通过 `INSIGHTS_CRON` 自定义
- 文档重构并双语（中/英）：
  - USERGUIDE：与 README 内容与顺序对齐；GitHub-only 精简并引导至 GITHUB_RELEASE_INBOX；模型配置整合至第 3 节
  - GITHUB_RELEASE_INBOX：按已验证的 TESTING_GITHUB_APP 流程重写；9 处 iOS 快捷指令截图占位；新增无 GitHub App 时手写 repository_dispatch 备选方案
  - TESTING_GITHUB_APP：增加对 GITHUB_RELEASE_INBOX 作为主指南的引用
  - 术语统一：路径 A/B → 自部署 / GitHub-only
  - USERGUIDE、GITHUB_RELEASE_INBOX、TESTING_GITHUB_APP 新增完整英文版及语言切换（中文 | English）
#### 新增
- `ENABLE_SCHEDULER`：scheduler 总开关（默认 `true`）；`false` 时 GitHub Actions job 直接 skip、自部署脚本 early return；不影响 HTTP 手动触发端点
#### 修复
- `_matches_cron` weekday 字段现遵循标准 cron 约定（0=周日）；之前 weekday 与 Python datetime.weekday() 约定混用，导致含 weekday 的 cron 表达式执行在错误的星期

### [0.1.1] - 2026-02-22
#### 修复
- EXTRACT_ONLY 现正确跳过 scheduler 中的 insights 与 summary
- Insights/summary/customized 产物现触发同步至 Feishu/Telegram/Discord/WhatsApp
- 每日洞察目标日：新增 INSIGHTS_TARGET_DAY_OFFSET（默认 1 = 昨天），以在例如 1 点运行等场景正确选择日期
#### 新增
- i18n 模块：OUTPUT_LOCALE 控制 SyncEvent 标题（zh-CN/en-US）
- sync_default_frequency：ON_EVENT（即时）、DAILY/CRON（按 sync_default_cron 时间批量），含 .sync_pending.jsonl 队列
- USERGUIDE 英文摘要章节

### [0.1.0] - 2026-02-21
#### 新增
- 初始 AuraCap 架构与 Python 后端
- 双入口 ingest API：
  - `/v1/capture/json` 用于 base64 JSON
  - `/v1/capture/upload` 用于 multipart 上传与服务端转换
  - `/v1/capture/raw` 用于可直接导入的快捷指令模板原始文件上传
- GitHub dispatch webhook 路径与 GitHub workflow 脚本
- 多模型抽象：OpenAI、Anthropic、Google、Groq、Mistral、Mock
- 音频处理模式切换：
  - `TRANSCRIBE_THEN_ANALYZE`
  - `DIRECT_MULTIMODAL`
- 存储链路：
  - timeline
  - 每日 insights
  - 定期 summary
  - 自定义操作输出
- 基于 cron 的 Scheduler 服务
- Sync 适配器协议及 Feishu、Telegram、Discord、WhatsApp 渠道适配器
- Docker Compose 部署
- 双语文档：`README.md`、`USERGUIDE.md`
- 快捷指令模板生成器及 `shortcuts/templates` 包
- 媒体 ingest、timeline 写入、scheduler 执行测试
- GitHub workflows 以 Actions Secrets/Variables 为主要配置源并自动提交 `storage/` 产物
- 文档 overhaul：
  - README.md 重组为清晰的路径 A/路径 B 划分
  - USERGUIDE.md 改为分步执行流程
  - 新增 `docs/GITHUB_RELEASE_INBOX.md` 提供具体 GitHub-only 搭建指引
  - 明确 `shortcuts/templates/*` 仅用于后端直传路由
- GitHub-only 简化：
  - 新增 `AuraCap Setup Release Inbox` workflow
  - 新增 `scripts/ensure_release_inbox.py` 一键 inbox release 初始化
  - 更新 ingest 脚本以从 GitHub Release Assets 获取 `asset_id`（无需外部中转）

---

<a name="english"></a>
## English

### [Unreleased]
#### Changed
- Summary default frequency: every 3 days → weekly (`SUMMARY_CRON` default `0 2 * * 0`, `SUMMARY_WINDOW_DAYS` default `7`); both configurable via variables
- Insights remain daily; configurable via `INSIGHTS_CRON`
- Documentation restructure and bilingual (zh/en):
  - USERGUIDE: aligned with README content/order; GitHub-only section simplified with redirect to GITHUB_RELEASE_INBOX; model config consolidated in section 3
  - GITHUB_RELEASE_INBOX: rewritten based on verified TESTING_GITHUB_APP flow; 9 screenshot placeholders for iOS Shortcuts steps; added fallback for hand-written repository_dispatch without GitHub App
  - TESTING_GITHUB_APP: added reference to GITHUB_RELEASE_INBOX as primary guide
  - Terminology unified: 路径 A/B → 自部署 / GitHub-only
  - Added full English versions to USERGUIDE, GITHUB_RELEASE_INBOX, TESTING_GITHUB_APP with language switcher (中文 | English)
#### Added
- `ENABLE_SCHEDULER`: master switch for scheduler (default `true`); when `false`, GitHub Actions job skips, self-host script exits early; does not affect HTTP manual trigger endpoint
#### Fixed
- `_matches_cron` weekday field now follows standard cron convention (0=Sunday); previously mixed with Python datetime.weekday(), causing weekday cron expressions to run on wrong day

### [0.1.1] - 2026-02-22
#### Fixed
- EXTRACT_ONLY now correctly skips insights and summary in scheduler.
- Insights/summary/customized artifacts now trigger sync dispatch to Feishu/Telegram/Discord/WhatsApp.
- Daily insights target day: added INSIGHTS_TARGET_DAY_OFFSET (default 1 = yesterday) for correct day selection when run at e.g. 1am.
#### Added
- i18n module: OUTPUT_LOCALE controls SyncEvent titles (zh-CN/en-US).
- sync_default_frequency: ON_EVENT (immediate), DAILY/CRON (batch at sync_default_cron time) with .sync_pending.jsonl queue.
- USERGUIDE English summary section.

### [0.1.0] - 2026-02-21
#### Added
- Initial AuraCap architecture with Python backend.
- Dual ingest API:
  - `/v1/capture/json` for base64 JSON
  - `/v1/capture/upload` for multipart upload and server-side conversion
  - `/v1/capture/raw` for direct raw file upload from import-ready shortcut templates
- GitHub dispatch webhook path and GitHub workflow scripts.
- Multi-provider abstraction for OpenAI, Anthropic, Google, Groq, Mistral, and Mock.
- Audio processing mode switch:
  - `TRANSCRIBE_THEN_ANALYZE`
  - `DIRECT_MULTIMODAL`
- Storage pipeline:
  - timeline
  - daily insights
  - periodic summary
  - custom operation output
- Scheduler service with cron-based checks.
- Sync adapter protocol and channel adapters for Feishu, Telegram, Discord, WhatsApp.
- Docker Compose deployment.
- Bilingual docs: `README.md` and `USERGUIDE.md`.
- Shortcut template generator and package under `shortcuts/templates`.
- Tests for media ingest, timeline write, scheduler execution.
- GitHub workflows updated to use Actions Secrets/Variables as primary config source and auto-commit `storage/` artifacts.
- Documentation overhaul:
  - Reorganized `README.md` with clear Route A/Route B split
  - Rewrote `USERGUIDE.md` into step-by-step execution flows
  - Added `docs/GITHUB_RELEASE_INBOX.md` with concrete GitHub-only setup guidance
  - Clarified that `shortcuts/templates/*` are for backend direct-upload route only
- GitHub-only simplification:
  - Added `AuraCap Setup Release Inbox` workflow
  - Added `scripts/ensure_release_inbox.py` for one-click inbox release bootstrap
  - Updated ingest script to consume `asset_id` from GitHub Release Assets (no external middleware required)
