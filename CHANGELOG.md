# Changelog

## [0.1.1] - 2026-02-22
### Fixed
- EXTRACT_ONLY now correctly skips insights and summary in scheduler.
- Insights/summary/customized artifacts now trigger sync dispatch to Feishu/Telegram/Discord/WhatsApp.
- Daily insights target day: added INSIGHTS_TARGET_DAY_OFFSET (default 1 = yesterday) for correct day selection when run at e.g. 1am.
### Added
- i18n module: OUTPUT_LOCALE controls SyncEvent titles (zh-CN/en-US).
- sync_default_frequency: ON_EVENT (immediate), DAILY/CRON (batch at sync_default_cron time) with .sync_pending.jsonl queue.
- USERGUIDE English summary section.

## [0.1.0] - 2026-02-21
### Added
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
