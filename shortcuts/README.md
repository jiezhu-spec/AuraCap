# AuraCap 快捷指令模板说明

## 1. 这份模板用于哪条路径
本目录模板用于 **路径 A（自部署/云部署直传后端 API）**。

可导入文件：
- `templates/AuraCap_Capture.shortcut`
- `templates/AuraCap_Voice.shortcut`
- `templates/AuraCap_Capture.plist`
- `templates/AuraCap_Voice.plist`

不适用场景：
- GitHub-only 路径（那条路径使用 GitHub Release Inbox 上传，再调用 `repository_dispatch`）。

## 2. 重新生成模板
```bash
python scripts/build_shortcuts.py
```

## 3. 导入方式

### 方式 A：直接导入 `.shortcut`
1. 把 `.shortcut` 文件放到 iCloud Drive。  
2. 在 iPhone 文件 App 打开。  
3. 选择导入到快捷指令。

### 方式 B：使用 `.plist` 回退导入
如果 iOS 拒绝 `.shortcut`，使用 `*.plist` 配合 source importer 工具导入。

## 4. 运行时会问什么
模板运行时只问一个值：
- `AuraCap Backend Base URL`

示例：
- 本地局域网：`http://192.168.1.23:8000`
- 云端域名：`https://cap.yourdomain.com`

模板会自动拼接并调用：
- 截图：`/v1/capture/raw?media_type=screenshot...`
- 录音：`/v1/capture/raw?media_type=audio...`

## 5. 如何确认成功
1. 快捷指令返回 JSON 且 `status: success`。  
2. 后端 `storage/timeline.md` 出现新记录。

GitHub-only 用户请改看：
- `/Users/massif/AuraCap/USERGUIDE.md` 第 2 章
- `/Users/massif/AuraCap/docs/GITHUB_RELEASE_INBOX.md`
