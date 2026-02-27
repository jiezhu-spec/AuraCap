# Storage 迁移说明

Storage 已改为使用 GitHub Actions Cache 持久化，不再通过 git 提交。这样在 PR 或 fork 同步时，`storage/` 不会被覆盖。

## 首次部署（新 fork）

无需操作。Storage 会在首次 workflow 运行时自动创建并缓存。

## 从旧版本迁移（已有 storage 的仓库）

1. 推送本次改动后，**先手动触发一次** Ingest 或 Scheduler workflow，让 cache 完成首次填充。
2. 确认 workflow 成功运行后，执行：

   ```bash
   git rm -r --cached storage/
   git commit -m "chore: complete storage migration to cache"
   git push
   ```

3. 之后 `storage/` 将完全由 cache 管理，PR 和 fork 同步不会覆盖你的数据。
