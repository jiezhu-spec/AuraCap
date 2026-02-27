# Storage 防覆盖配置

Storage 保留在项目仓库中。从上游 sync 时，通过配置可避免你的 storage 被覆盖。

## 方式一：本地 clone 过的用户

在**第一次 sync 之前**执行一次（仅需一次）：

```bash
git config merge.ours.driver true
```

之后每次 `git pull` 或 sync 都会自动保留你的 storage。

## 方式二：只用 GitHub 网页、从不 clone 的用户

`merge=ours` 依赖本地 git 配置，网页端 Sync fork 无法使用。

**可选做法：**

1. **不 sync**：继续用当前 fork，不拉取上游更新。
2. **Sync 时手动保留 storage**：若 Sync 后出现 storage 相关冲突，在解决冲突时选择「保留当前分支的版本」（Keep ours / Accept yours）。
3. **偶尔 clone 一次**：需要 sync 时，本地 clone → 执行上面的 `git config` → `git pull upstream main` → `git push`，之后可继续只用网页。

## 原理

- Storage 仍在仓库中，workflow 照常提交
- `merge=ours` 在合并时保留当前分支的 storage 版本
