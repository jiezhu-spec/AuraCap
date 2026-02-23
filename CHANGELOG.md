# Changelog

**Language / 语言**：[中文](#中文) | [English](#english)

---

<a name="中文"></a>
## 中文

### [Unreleased]
#### 变更
- CI 与 workflow 修复：
  - `pyproject.toml`：新增 `[tool.setuptools.packages.find] include = ["backend*"]`，修复 `pip install .[dev]` 时「Multiple top-level packages」错误
  - `scheduler_tick.yml`：运行脚本时添加 `PYTHONPATH=.`，修复 `ModuleNotFoundError: No module named 'backend'`
- Release 处理：`GITHUB_RELEASE_DELETE_AFTER_PROCESS` 固定为 `true`，处理完成后自动删除 Release 文件，避免 `shot.png` 重复上传时 `already_exists`；移除该变量配置项
- Timeline 存储格式精简：`storage/timeline.md` 每条仅保留 `timestamp`、`timestamp_display`、`extracted_content` 三字段，移除 id、locale、timezone、input_type、source、metadata、trace
- 文档：Fine-grained Token 补充 `Actions: Read and write`（使用「调度工作流程」时）；常见问题补充 `already_exists` 与动态文件名说明
- USERGUIDE 文档补全与结构优化：
  - 2.2 Docker：补充 backend/scheduler 双容器说明及 scheduler 每小时执行
  - 2.5 新增「捕获 API 的三种方式」（raw/upload/json）及适用场景
  - 3.2 时间戳与输出：补充 DEFAULT_TIMEZONE 语义、TIMESTAMP_FORMAT、OUTPUT_LOCALE
  - 3.3 音频模式：详细说明 TRANSCRIBE_THEN_ANALYZE 与 DIRECT_MULTIMODAL 的流程与依赖
  - 3.4 功能开关：补全 ENABLE_INSIGHTS/ENABLE_SUMMARY 说明；EXTRACT_ONLY 优先级；Custom Operation 完整说明（CUSTOM_OPERATION_MODE、prompt 配置）；手动触发 /v1/tasks/run-scheduled 的用途
  - 3.1 模型配置：补充 Anthropic、Groq、Mistral 配置指引
  - 4 存储：各目录用途、STORAGE_ROOT 等路径可配置；4.1 输入限制与媒体类型（MAX_UPLOAD_MB、ALLOWED_*_MIME）；4.2 Sync 简介；4.3 安全（签名校验）
- Summary 默认频率由每 3 天改为每周（`SUMMARY_CRON` 默认 `0 2 * * 0`，`SUMMARY_WINDOW_DAYS` 默认 `7`）；两者均可通过变量自定义
- Insights 保持每日一次，可通过 `INSIGHTS_CRON` 自定义
- 文档重构并双语（中/英）：
  - USERGUIDE：与 README 内容与顺序对齐；GitHub-only 精简并引导至 GITHUB_RELEASE_INBOX；模型配置整合至第 3 节
  - GITHUB_RELEASE_INBOX：按已验证的 TESTING_GITHUB_APP 流程重写；9 处 iOS 快捷指令截图占位；新增无 GitHub App 时手写 repository_dispatch 备选方案
  - TESTING_GITHUB_APP：增加对 GITHUB_RELEASE_INBOX 作为主指南的引用
  - 术语统一：路径 A/B → 自部署 / GitHub-only
  - USERGUIDE、GITHUB_RELEASE_INBOX、TESTING_GITHUB_APP 新增完整英文版及语言切换（中文 | English）
#### 新增
- 多提示词路由系统（Prompt Router）：
  - 新增 `backend/app/services/prompt_router.py` 模块，集中封装语言检测与提示词路由逻辑
  - Timeline 新增 4 套场景化提示词：`timeline_screenshot_zh.md`、`timeline_screenshot_en.md`、`timeline_audio_zh.md`、`timeline_audio_en.md`
  - Insights 新增双语提示词：`insights_zh.md`、`insights_en.md`
  - Summary 新增双语提示词：`summary_zh.md`、`summary_en.md`
  - 新增 `TIMELINE_LANG_MODE` 配置（默认 `request_locale`）：`request_locale` 按 `AURACAP_LOCALE`/`OUTPUT_LOCALE` 选提示词；`content_detect` 自动检测截图/录音内容语言（截图需额外 VL 调用，录音用 CJK 字符比例启发式检测）
  - Insights/Summary 始终通过 `OUTPUT_LOCALE` 路由至对应语言提示词
  - 所有语言专属提示词文件均缺失时自动回退到原有通用提示词文件，零迁移成本
- 统一 Provider 模式：`UNIFIED_PROVIDER` 可将 text/mm/asr 统一到同一 provider，只需配置一个 API key；支持 openai、google、groq、mistral、mock（不含 anthropic）
- 文档澄清：`DIRECT_MULTIMODAL` 下 ASR 配置可忽略；`OPENAI_*` 适用于 OpenAI 官方及所有 OpenAI API 兼容的第三方服务（SiliconFlow、OpenRouter、DeepSeek 等）
- 提示词重写：`timeline_prompts.md`、`insights_prompts.md`、`summary_prompts.md` 全部重写，增强中文输出与场景适配
  - timeline：针对 iOS 截图优化，过滤状态栏等系统噪音，按内容类型自适应提取，输出核心内容/行动项/待确认
  - insights：跨条目模式分析，今日焦点、隐含意图、未完成信号、值得跟进内容
  - summary：纵向轨迹分析，持续关注主题、意图与行为对照、进展与停滞、注意力漂移
- README 新增「提示词说明」小节；补充自部署快速上手（git clone、Docker 选项）、输出目录（含 customized）、模型列表（Anthropic/Groq/Mistral）；USERGUIDE 3.6 补充提示词完整文档（作用、触发变量、自定义路径、截图 vs 录音说明）
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
- CI and workflow fixes:
  - `pyproject.toml`: added `[tool.setuptools.packages.find] include = ["backend*"]` to fix "Multiple top-level packages" error on `pip install .[dev]`
  - `scheduler_tick.yml`: added `PYTHONPATH=.` when running script to fix `ModuleNotFoundError: No module named 'backend'`
- Release handling: `GITHUB_RELEASE_DELETE_AFTER_PROCESS` hardcoded to `true`; uploaded files auto-deleted after processing to avoid `already_exists` when re-uploading `shot.png`; removed variable from config
- Timeline storage format simplified: each entry in `storage/timeline.md` now has only `timestamp`, `timestamp_display`, `extracted_content`; removed id, locale, timezone, input_type, source, metadata, trace
- Docs: Fine-grained Token now documents `Actions: Read and write` when using "Run workflow"; troubleshooting updated for `already_exists` and dynamic filename
- USERGUIDE documentation completion and restructuring:
  - 2.2 Docker: added backend/scheduler dual-container description, scheduler hourly tick
  - 2.5 New "Capture API options" (raw/upload/json) and use cases
  - 3.2 Timestamp and output: DEFAULT_TIMEZONE semantics, TIMESTAMP_FORMAT, OUTPUT_LOCALE
  - 3.3 Audio mode: TRANSCRIBE_THEN_ANALYZE vs DIRECT_MULTIMODAL flow and dependencies
  - 3.4 Feature flags: ENABLE_INSIGHTS/ENABLE_SUMMARY; EXTRACT_ONLY precedence; full Custom Operation (CUSTOM_OPERATION_MODE, prompt config); manual trigger /v1/tasks/run-scheduled
  - 3.1 Model config: Anthropic, Groq, Mistral setup
  - 4 Storage: directory purposes, path customization; 4.1 input limits and media types; 4.2 Sync; 4.3 security (signature)
- Summary default frequency: every 3 days → weekly (`SUMMARY_CRON` default `0 2 * * 0`, `SUMMARY_WINDOW_DAYS` default `7`); both configurable via variables
- Insights remain daily; configurable via `INSIGHTS_CRON`
- Documentation restructure and bilingual (zh/en):
  - USERGUIDE: aligned with README content/order; GitHub-only section simplified with redirect to GITHUB_RELEASE_INBOX; model config consolidated in section 3
  - GITHUB_RELEASE_INBOX: rewritten based on verified TESTING_GITHUB_APP flow; 9 screenshot placeholders for iOS Shortcuts steps; added fallback for hand-written repository_dispatch without GitHub App
  - TESTING_GITHUB_APP: added reference to GITHUB_RELEASE_INBOX as primary guide
  - Terminology unified: 路径 A/B → 自部署 / GitHub-only
  - Added full English versions to USERGUIDE, GITHUB_RELEASE_INBOX, TESTING_GITHUB_APP with language switcher (中文 | English)
#### Added
- Multi-prompt routing system (Prompt Router):
  - Added `backend/app/services/prompt_router.py` module encapsulating language detection and prompt routing logic
  - Timeline: 4 scenario-specific prompts: `timeline_screenshot_zh.md`, `timeline_screenshot_en.md`, `timeline_audio_zh.md`, `timeline_audio_en.md`
  - Insights: bilingual prompts: `insights_zh.md`, `insights_en.md`
  - Summary: bilingual prompts: `summary_zh.md`, `summary_en.md`
  - New `TIMELINE_LANG_MODE` setting (default `request_locale`): `request_locale` uses `AURACAP_LOCALE`/`OUTPUT_LOCALE` for prompt selection; `content_detect` auto-detects content language (screenshots incur 1 extra VL call; audio uses CJK character ratio heuristic)
  - Insights/Summary always route to the language-specific prompt via `OUTPUT_LOCALE`
  - Graceful fallback to existing generic prompt files when language-specific variants are absent — zero migration cost
- Unified Provider mode: `UNIFIED_PROVIDER` routes text/mm/asr to one provider with a single API key; supports openai, google, groq, mistral, mock (excludes anthropic)
- Doc clarification: ASR config can be ignored when `DIRECT_MULTIMODAL`; `OPENAI_*` applies to OpenAI official and all OpenAI API compatible third-party services (SiliconFlow, OpenRouter, DeepSeek, etc.)
- Prompt rewrites: `timeline_prompts.md`, `insights_prompts.md`, `summary_prompts.md` rewritten for better Chinese output and scene adaptation
  - timeline: iOS screenshot optimization, filter status bar etc., content-type adaptive extraction, output 核心内容/行动项/待确认
  - insights: cross-entry pattern analysis (今日焦点, 隐含意图, 未完成信号, 值得跟进)
  - summary: longitudinal trajectory (持续关注主题, 意图与行为对照, 进展与停滞, 注意力漂移)
- README "提示词说明" section; self-host quick start (git clone, Docker option), output dirs (incl. customized), model list (Anthropic/Groq/Mistral); USERGUIDE 3.6 prompt docs (purpose, trigger vars, custom paths, screenshot vs recording)
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
