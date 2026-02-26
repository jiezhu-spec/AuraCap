# AuraCap Timeline

This file appends one markdown-json entry per trigger.
### entry-cc8bf6991ca147b9af5d7b09f1dfb7fa
```json
{
  "id": "entry-cc8bf6991ca147b9af5d7b09f1dfb7fa",
  "timestamp": "2026-02-26T15:49:19.820443+00:00",
  "timestamp_display": "2026-02-26 15:49:19 UTC",
  "extracted_content": "### 核心内容\n\n- **测试对象**：Qwen3.5 的 35B 和 27B 模型，均使用 FP8 精度。\n- **硬件配置**：单卡 4090，显存 48G。\n- **测试结果**：\n  - **35B 模型**：\n    - 单卡请求速度 120-130 时，200k 上下文仅能衰退到 90，性能不足。\n  - **27B 模型**：\n    - Dense 模型性能较好，输出稳定在 20t/s。\n    - 200k 前缓冲 4k 输入时，保持 19t/s 左右，prefill 时间约 200 毫秒。\n    - 使用 Agent Teams 并发，六个并发稳定输出 120t，任务完成。\n\n### 行动项\n\n- **优化方向**：27B 模型性能表现较好，值得进一步挖掘其潜力。\n- **改进建议**：尝试提升 27B 模型的速度，优化时间消耗。\n\n### 待确认\n\n- **时间优化**：是否有进一步提升 prefill 时间的可能性。"
}
```

### entry-29855104f239432c9e0e9735838e20b6
```json
{
  "id": "entry-29855104f239432c9e0e9735838e20b6",
  "timestamp": "2026-02-26T16:27:35.771356+00:00",
  "timestamp_display": "2026-02-26 16:27:35 UTC",
  "extracted_content": "### 核心内容\n- **研究背景**：探讨了LLM（大语言模型）的Base与Instruct之间的权重相似性，定义了权重的sigma值。\n- **关键数据**：Qwen 3.5 A3B的Base模型sigma值为 **0.01768391**，约为1%上下，表明相似性极高。\n- **补充说明**：主流LLM的sigma值普遍较小，具体细节可参考P2论文。\n\n### 行动项\n- 进一步研究P2和P3论文中的相关细节。\n\n### 标签\n#Qwen3 #weight #LLM #HKU #相似性 #reasoning"
}
```

### entry-9853886539fd4fda8b5bcd9ba13906a6
```json
{
  "id": "entry-9853886539fd4fda8b5bcd9ba13906a6",
  "timestamp": "2026-02-26T17:15:52.062101+00:00",
  "timestamp_display": "2026-02-26 17:15:52 UTC",
  "extracted_content": "### 核心内容\n\n- **模型信息**  \n  - 名称：Qwen3.5-35B-A3B  \n  - 参数量：35亿  \n  - 每个token活跃参数：30亿  \n  - 量化：4-bit  \n  - 磁盘占用：19.7GB  \n\n- **运行环境**  \n  - 硬件：单张3090显卡  \n  - 上下文长度：从4K扩展到262K  \n  - 零卸载，所有层运行在GPU上  \n  - 性能：4K时112 tok/s，262K时114 tok/s，速度稳定  \n\n- **默认设置问题**  \n  - 默认设置在262K上下文时会OOM（内存溢出）  \n  - 通过一个标志位解锁，具体解锁命令和细节在后续图表中  \n\n- **模型架构**  \n  - 非纯Transformer结构  \n  - 40层中30层为Mamba2状态空间层，固定内存占用，与上下文长度无关  \n  - 仅10层携带KV缓存，75%的层对上下文长度不敏感  \n\n- **性能评价**  \n  - 在单张消费级显卡上实现4-bit量化的全原生上下文运行  \n  - 对代码质量尚未优化的情况下，性能已令人印象深刻  \n  - 计划在该模型上运行Claude Code，若其代码生成能力与扩展能力一致，将改变本地推理的游戏规则  \n\n### 行动项\n\n- 查看后续图表获取解锁命令和详细设置  \n- 测试Claude Code在该模型上的运行效果"
}
```

### entry-275b130bb47349339d300e845543a38e
```json
{
  "id": "entry-275b130bb47349339d300e845543a38e",
  "timestamp": "2026-02-26T17:23:37.997513+00:00",
  "timestamp_display": "2026-02-26 17:23:37 UTC",
  "extracted_content": "### 核心内容\n\n**如何在 Cursor 中使用 Context7：**\n\n1. **操作步骤：**\n   - 打开 Cursor 的设置 → 选择 MCP。\n   - 添加新的 MCP。\n\n2. **代码配置：**\n   将以下代码粘贴到 `~/.cursor/mcp.json` 文件中：\n   ```json\n   {\n       \"mcpServers\": {\n           \"context7\": {\n               \"command\": \"npx\",\n               \"args\": [\"-y\", \"@upstash/context7-mcp@latest\"]\n           }\n       }\n   }\n   ```\n\n3. **注意事项：**\n   - 如果需要，可以重启 Cursor。\n\n---\n\n### 补充信息\n\n- **主题**：Cursor 的高效使用技巧。\n- **亮点**：通过 Context7 提升 Cursor 的效率，号称能让其性能提升 200 倍。\n- **互动数据**：点赞 45，收藏 92，评论 1。"
}
```

### entry-076c16f469f643f791727ed5a38dc5fd
```json
{
  "id": "entry-076c16f469f643f791727ed5a38dc5fd",
  "timestamp": "2026-02-26T17:25:47.858712+00:00",
  "timestamp_display": "2026-02-26 17:25:47 UTC",
  "extracted_content": "### 核心内容\n\n#### 【核心引擎升级】\n- **Mamba 前缀缓存**  \n  - 使用参数：`--enable-prefix-caching --mamba-cache-mode align`  \n  - 直接缓存 Mamba 状态，性能提升约 2 倍。\n\n- **会话式流式输入**  \n  - 新增 `StreamingInput API`  \n  - 专为 ASR 等交互式场景设计。\n\n- **异步调度 + 流水线并行**  \n  - `--async-scheduling` 现已支持 Pipeline Parallelism。\n\n---\n\n#### 【NVIDIA Blackwell】\n- **FlashInfer MLA** 成为默认后端。  \n- **FP4 内核优化**：性能最高提升 65%。  \n- **E2E 吞吐提升**：约 4%。  \n- **MoE 性能**：`grouped topk fusion` 提升 1.2%-2%。\n\n---\n\n#### 【AMD ROCm】\n- **MoRI EP**：高性能 Expert Parallel all2all 通信。  \n- **RDNA3/RDNA4** 消费级显卡支持。  \n- **FP4 MLA**：投影 GEMM 动态量化。"
}
```

